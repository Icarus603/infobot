"""WeChat 控制器模組 - 使用 wxauto_macos 庫"""

import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# 添加 wxauto_macos 庫到路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import wxauto_macos

from ..utils.config import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


class WeChatController:
    """WeChat 控制器 - 使用 wxauto_macos 庫"""
    
    def __init__(self, config: Config):
        """初始化WeChat控制器"""
        self.config = config
        self.wechat = None
        self.is_monitoring = False
        self.monitor_threads: Dict[str, threading.Thread] = {}
        self.message_callbacks: List[Callable] = []
        self.opened_windows: List[str] = []
        
        # 初始化微信實例
        self._initialize_wechat()
        
    def _initialize_wechat(self):
        """初始化微信實例"""
        try:
            logger.info("正在初始化 wxauto_macos...")
            self.wechat = wxauto_macos.WeChat()
            logger.info("✅ wxauto_macos 初始化成功")
        except Exception as e:
            logger.error(f"❌ 初始化 wxauto_macos 失敗: {e}")
            raise
    
    def add_message_callback(self, callback: Callable):
        """添加消息回調函數"""
        self.message_callbacks.append(callback)
    
    def check_wechat_status(self) -> bool:
        """檢查WeChat狀態"""
        try:
            if not self.wechat:
                logger.error("WeChat 實例未初始化")
                return False
            
            # 檢查登錄狀態
            is_logged_in = self.wechat.check_login_status()
            if not is_logged_in:
                logger.error("WeChat 未登錄")
                return False
            
            logger.info("WeChat 狀態正常")
            return True
            
        except Exception as e:
            logger.error(f"檢查WeChat狀態失敗: {e}")
            return False
    
    def send_message(self, contact_name: str, message: str) -> bool:
        """向指定聯繫人發送消息"""
        try:
            logger.info(f"正在向 {contact_name} 發送消息")
            
            # 檢查WeChat狀態
            if not self.check_wechat_status():
                return False
            
            # 發送消息
            success = self.wechat.SendMsg(message, contact_name)
            
            if success:
                logger.info(f"✅ 成功向 {contact_name} 發送消息")
                
                # 記錄已打開的窗口
                if contact_name not in self.opened_windows:
                    self.opened_windows.append(contact_name)
            else:
                logger.error(f"❌ 向 {contact_name} 發送消息失敗")
            
            return success
            
        except Exception as e:
            logger.error(f"發送消息時發生錯誤: {e}")
            return False
    
    def send_message_to_multiple_contacts(self, contact_names: List[str], message: str) -> Dict[str, bool]:
        """向多個聯繫人批量發送消息"""
        results = {}
        
        logger.info(f"開始向 {len(contact_names)} 個聯繫人發送消息")
        
        # 序列化發送避免衝突（macOS 上並行操作可能不穩定）
        for contact_name in contact_names:
            try:
                success = self.send_message(contact_name, message)
                results[contact_name] = success
                
                # 批量操作間無需延遲
                
            except Exception as e:
                logger.error(f"向 {contact_name} 發送消息時發生異常: {e}")
                results[contact_name] = False
        
        # 統計結果
        success_count = sum(1 for success in results.values() if success)
        logger.info(f"批量發送完成: {success_count}/{len(contact_names)} 成功")
        
        return results
    
    def reply_to_sender(self, sender_name: str, reply_message: str) -> bool:
        """回覆發送者"""
        return self.send_message(sender_name, reply_message)
    
    def open_chat_windows(self, contact_names: List[str]) -> Dict[str, bool]:
        """批量打開聊天窗口"""
        results = {}
        
        logger.info(f"開始打開 {len(contact_names)} 個聊天窗口")
        
        for contact_name in contact_names:
            try:
                # 使用 wxauto_macos 的 SendMsg 來"測試"打開聊天窗口
                # 這會自動搜索並打開聯繫人
                success = self.wechat._open_chat(contact_name)
                results[contact_name] = success
                
                if success:
                    logger.info(f"✅ 成功打開 {contact_name} 的聊天窗口")
                    if contact_name not in self.opened_windows:
                        self.opened_windows.append(contact_name)
                else:
                    logger.error(f"❌ 打開 {contact_name} 聊天窗口失敗")
                

                
            except Exception as e:
                logger.error(f"打開 {contact_name} 聊天窗口時發生錯誤: {e}")
                results[contact_name] = False
        
        return results
    
    def start_monitoring_contact(self, contact_name: str, check_interval: float = 3.0):
        """開始監控指定聯繫人的消息 (改進版 - 基於變化檢測)"""
        if contact_name in self.monitor_threads:
            logger.warning(f"已經在監控 {contact_name} 的消息")
            return

        # 啟動監控前將狀態設置為 True
        self.is_monitoring = True
        
        logger.info(f"開始監控 {contact_name} 的消息")
        
        def monitor_loop():
            """監控循環 - 使用變化檢測方法"""
            
            while self.is_monitoring:
                try:
                    logger.debug(f"正在監控 {contact_name}...")
                    
                    # 打開聯繫人對話
                    if self.wechat._open_chat(contact_name):
                        logger.debug(f"✅ 成功打開 {contact_name} 的對話")
                        
                        # 等待消息變化
                        if self.wechat.wait_for_message_change(timeout=check_interval):
                            logger.info(f"🔔 檢測到 {contact_name} 的聊天窗口有變化!")
                            
                            # 觸發消息回調（模擬新消息）
                            for callback in self.message_callbacks:
                                try:
                                    callback(contact_name, "檢測到新活動")
                                except Exception as e:
                                    logger.error(f"消息回調執行失敗: {e}")
                        else:
                            logger.debug(f"在 {check_interval} 秒內未檢測到 {contact_name} 的變化")
                    
                    else:
                        logger.warning(f"❌ 無法打開 {contact_name} 的對話")
                        time.sleep(check_interval * 2)  # 失敗時等待更長時間
                        
                except Exception as e:
                    logger.error(f"監控 {contact_name} 時發生錯誤: {e}")
                    time.sleep(check_interval)
        
        # 啟動監控線程
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        self.monitor_threads[contact_name] = thread

        logger.info(f"✅ 已啟動 {contact_name} 的監控線程")

    def start_monitoring_multiple_contacts(self, contact_names: List[str], check_interval: float = 3.0):
        """批量啟動多個聯繫人的監控"""
        if not contact_names:
            logger.warning("沒有提供任何聯繫人，無法開始監控")
            return

        for index, name in enumerate(contact_names):
            interval = check_interval + index * 1.0
            self.start_monitoring_contact(name, interval)
            time.sleep(0.5)

    def start_monitoring_all_contacts(self, check_interval: float = 5.0):
        """開始監控所有聯繫人的消息 (改進版)"""
        logger.info("開始監控所有配置的聯繫人...")
        
        # 獲取所有需要監控的聯繫人
        all_contacts = []
        if self.config.teachers:
            all_contacts.extend(self.config.teachers)
        if self.config.students:
            all_contacts.extend(self.config.students)
        
        if not all_contacts:
            logger.warning("⚠️ 沒有配置任何聯繫人，無法開始監控")
            return
        
        # 為每個聯繫人啟動監控
        for contact_name in all_contacts:
            logger.info(f"準備監控聯繫人: {contact_name}")
            
            # 為不同聯繫人使用不同的檢查間隔，避免衝突
            individual_interval = check_interval + (len(self.monitor_threads) * 1.0)
            self.start_monitoring_contact(contact_name, individual_interval)
            
            # 避免同時啟動太多監控
            time.sleep(0.5)
        
        logger.info(f"✅ 已啟動 {len(all_contacts)} 個聯繫人的監控")

    def check_contact_activity(self, contact_name: str) -> bool:
        """檢查指定聯繫人是否有活動
        
        Args:
            contact_name: 聯繫人名稱
            
        Returns:
            bool: 是否有活動
        """
        try:
            logger.debug(f"檢查 {contact_name} 的活動...")
            
            # 打開聯繫人對話
            if not self.wechat._open_chat(contact_name):
                logger.warning(f"無法打開 {contact_name} 的對話")
                return False
            
            # 檢查新消息指示器
            has_indicator = self.wechat.check_new_message_indicator()
            if has_indicator:
                logger.info(f"🔔 {contact_name} 有新消息指示器")
                return True
            
            # 檢查窗口變化
            window_changes = self.wechat.get_chat_window_changes()
            if window_changes:
                logger.debug(f"{contact_name} 窗口狀態: {window_changes}")
                
                # 簡單的變化檢測邏輯
                if hasattr(self, f'_last_state_{contact_name}'):
                    last_state = getattr(self, f'_last_state_{contact_name}')
                    if window_changes != last_state:
                        logger.info(f"🔔 {contact_name} 窗口狀態有變化")
                        setattr(self, f'_last_state_{contact_name}', window_changes)
                        return True
                else:
                    # 首次檢查，記錄初始狀態
                    setattr(self, f'_last_state_{contact_name}', window_changes)
                    logger.debug(f"記錄 {contact_name} 的初始狀態")
            
            return False
            
        except Exception as e:
            logger.error(f"檢查 {contact_name} 活動時出錯: {e}")
            return False

    def get_monitoring_status(self) -> Dict[str, Any]:
        """獲取監控狀態信息
        
        Returns:
            dict: 監控狀態信息
        """
        status = {
            "is_monitoring": self.is_monitoring,
            "monitored_contacts": list(self.monitor_threads.keys()),
            "active_threads": len([t for t in self.monitor_threads.values() if t.is_alive()]),
            "message_callbacks": len(self.message_callbacks),
            "last_check": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return status
    
    def stop_monitoring_contact(self, contact_name: str):
        """停止監控指定聯繫人"""
        if contact_name in self.monitor_threads:
            logger.info(f"停止監控 {contact_name} 的消息")
            del self.monitor_threads[contact_name]
    
    def stop_all_monitoring(self):
        """停止所有監控"""
        logger.info("停止所有消息監控")
        self.is_monitoring = False
        self.monitor_threads.clear()

    # 兼容舊方法名
    def stop_monitoring_all(self):
        return self.stop_all_monitoring()
    
    def get_opened_windows(self) -> List[str]:
        """獲取已打開的聊天窗口列表"""
        return self.opened_windows.copy()
    
    def close_chat_window(self, contact_name: str) -> bool:
        """關閉聊天窗口（僅從記錄中移除）"""
        if contact_name in self.opened_windows:
            self.opened_windows.remove(contact_name)
            logger.info(f"已從記錄中移除 {contact_name} 的聊天窗口")
            return True
        return False
    
    def get_chat_list(self) -> List[str]:
        """獲取聊天列表"""
        try:
            if not self.wechat:
                return []
            
            # 使用 wxauto_macos 獲取會話列表
            sessions = self.wechat.GetSessionList()
            logger.debug(f"獲取到 {len(sessions)} 個會話")
            return sessions
            
        except Exception as e:
            logger.error(f"獲取聊天列表失敗: {e}")
            return []
    
    def refresh_wechat(self) -> bool:
        """刷新WeChat應用"""
        try:
            if not self.wechat:
                return False
            
            # 重新激活WeChat
            success = self.wechat.activate_wechat()
            if success:
                logger.info("✅ WeChat 刷新成功")
            else:
                logger.error("❌ WeChat 刷新失敗")
            return success
            
        except Exception as e:
            logger.error(f"刷新WeChat時發生錯誤: {e}")
            return False
    
 