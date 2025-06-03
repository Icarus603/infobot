"""主機器人邏輯模組"""

import time
from datetime import datetime
from typing import Dict, List, Optional

import schedule

from ..ai.siliconflow_client import SiliconFlowClient
from ..utils.config import Config
from ..utils.logger import get_logger
from .message_handler import Message, MessageHandler
from .wechat_controller import WeChatController

logger = get_logger(__name__)


class InfoBot:
    """智能微信機器人主類"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        """初始化機器人"""
        # 載入配置
        self.config = Config.load_from_yaml(config_path)
        
        # 初始化AI客戶端
        self.ai_client = SiliconFlowClient(self.config.siliconflow)
        
        # 初始化消息處理器
        self.message_handler = MessageHandler(self.config, self.ai_client)
        
        # 初始化WeChat控制器
        self.wechat_controller = WeChatController(self.config)
        
        # 機器人狀態
        self.is_running = False
        self.start_time: Optional[datetime] = None
        self.stats = {
            "messages_received": 0,
            "messages_sent": 0,
            "messages_forwarded": 0,
            "auto_replies_sent": 0
        }
        
        # 設置回調函數
        self._setup_callbacks()
        
        logger.info("InfoBot 初始化完成")
    
    def _setup_callbacks(self):
        """設置回調函數"""
        # 設置WeChat消息回調
        self.wechat_controller.add_message_callback(self._on_message_received)
        
        # 設置消息處理器回調
        self.message_handler.add_message_callback("teacher_message", self._on_teacher_message)
        self.message_handler.add_message_callback("student_message", self._on_student_message)
        self.message_handler.add_message_callback("unknown_message", self._on_unknown_message)
    
    def _on_message_received(self, sender: str, content: str):
        """當收到消息時的回調函數"""
        self.stats["messages_received"] += 1
        
        # 處理消息
        message = self.message_handler.process_incoming_message(sender, content)
        
        if message:
            logger.info(f"成功處理來自 {sender} 的消息")
        else:
            logger.error(f"處理來自 {sender} 的消息失敗")
    
    def _on_teacher_message(self, message: Message):
        """處理老師消息的回調"""
        logger.info(f"處理老師 {message.sender} 的消息")
        
        try:
            # 1. 自動回覆老師
            if self._should_auto_reply(message):
                reply = self.message_handler.generate_auto_reply(message)
                success = self.wechat_controller.reply_to_sender(message.sender, reply)
                
                if success:
                    self.stats["auto_replies_sent"] += 1
                    logger.info(f"已向 {message.sender} 發送自動回覆: {reply}")
                else:
                    logger.error(f"向 {message.sender} 發送自動回覆失敗")
            
            # 2. 判斷是否需要轉發
            if self.message_handler.should_forward_message(message):
                self._forward_message_to_students(message)
            
            # 3. 標記消息為已處理
            self.message_handler.mark_message_processed(message)
            
        except Exception as e:
            logger.error(f"處理老師消息時發生錯誤: {e}")
    
    def _on_student_message(self, message: Message):
        """處理學生消息的回調"""
        logger.info(f"收到學生 {message.sender} 的消息")
        
        # 對於學生消息，通常不需要特殊處理
        # 可以在這裡添加處理學生問題的邏輯
        
        self.message_handler.mark_message_processed(message)
    
    def _on_unknown_message(self, message: Message):
        """處理未知用戶消息的回調"""
        logger.warning(f"收到來自未知用戶 {message.sender} 的消息")
        
        # 可以選擇性回覆或忽略
        self.message_handler.mark_message_processed(message)
    
    def _should_auto_reply(self, message: Message) -> bool:
        """判斷是否應該自動回覆"""
        # 簡化邏輯：對所有老師消息都自動回覆
        return message.is_from_teacher
    
    def _forward_message_to_students(self, message: Message):
        """轉發消息給學生"""
        try:
            # 獲取目標學生列表
            target_students = self.message_handler.get_target_students(message)
            
            if not target_students:
                logger.warning("沒有找到目標學生，跳過轉發")
                return
            
            # 生成轉發消息
            forward_message = self.message_handler.generate_forward_message(message)
            
            logger.info(f"準備向 {len(target_students)} 個學生轉發消息")
            
            # 批量發送消息
            results = self.wechat_controller.send_message_to_multiple_contacts(
                target_students, forward_message
            )
            
            # 統計結果
            success_count = sum(1 for success in results.values() if success)
            self.stats["messages_forwarded"] += success_count
            self.stats["messages_sent"] += len(target_students)
            
            logger.info(f"消息轉發完成: {success_count}/{len(target_students)} 成功")
            
        except Exception as e:
            logger.error(f"轉發消息時發生錯誤: {e}")
    
    def start(self):
        """啟動機器人"""
        if self.is_running:
            logger.warning("機器人已經在運行")
            return
        
        logger.info("正在啟動 InfoBot...")
        
        # 檢查WeChat狀態
        if not self.wechat_controller.check_wechat_status():
            logger.error("WeChat 狀態異常，無法啟動機器人")
            return
        
        # 設置定時任務
        self._setup_scheduled_tasks()
        
        # 開始監控老師的消息
        teacher_names = self.config.get_teacher_names()
        student_names = self.config.get_student_names()
        all_contacts = teacher_names + student_names
        
        if teacher_names:
            self.wechat_controller.start_monitoring_multiple_contacts(teacher_names)
            logger.info(f"開始監控 {len(teacher_names)} 位老師的消息")
        else:
            logger.warning("未配置老師信息，無法開始監控")
        
        # 打開所有聊天窗口（老師和學生）
        if all_contacts:
            logger.info(f"正在打開 {len(all_contacts)} 個聊天窗口（{len(teacher_names)} 位老師 + {len(student_names)} 位學生）")
            
            # 打開所有聊天窗口
            all_results = self.wechat_controller.open_chat_windows(all_contacts)
            success_count = sum(1 for success in all_results.values() if success)
            
            logger.info(f"聊天窗口打開完成: {success_count}/{len(all_contacts)} 成功")
        else:
            logger.warning("未配置任何聯繫人，跳過打開聊天窗口")
        
        self.is_running = True
        self.start_time = datetime.now()
        
        logger.info("InfoBot 啟動成功！")
        
        # 主運行循環
        self._run_main_loop()
    
    def _setup_scheduled_tasks(self):
        """設置定時任務"""
        # 每小時清理舊消息
        schedule.every().hour.do(self.message_handler.cleanup_old_messages, days=7)
        
        # 每天生成統計報告
        schedule.every().day.at("23:59").do(self._generate_daily_report)
        
        # 每30分鐘檢查系統狀態
        schedule.every(30).minutes.do(self._health_check)
        
        logger.info("定時任務設置完成")
    
    def _run_main_loop(self):
        """主運行循環"""
        logger.info("進入主運行循環")
        
        try:
            while self.is_running:
                # 運行定時任務
                schedule.run_pending()
                
                # 處理待處理的消息
                pending_messages = self.message_handler.get_pending_messages()
                if pending_messages:
                    logger.info(f"處理 {len(pending_messages)} 條待處理消息")
                    for message in pending_messages:
                        if message.is_from_teacher:
                            self._on_teacher_message(message)
                        else:
                            self.message_handler.mark_message_processed(message)
                
                # 主循環無需延遲
                
        except KeyboardInterrupt:
            logger.info("收到停止信號")
        except Exception as e:
            logger.error(f"主循環發生錯誤: {e}")
        finally:
            self.stop()
    
    def stop(self):
        """停止機器人"""
        if not self.is_running:
            logger.warning("機器人未在運行")
            return
        
        logger.info("正在停止 InfoBot...")
        
        self.is_running = False
        
        # 停止所有監控
        self.wechat_controller.stop_all_monitoring()
        
        # 生成最終報告
        self._generate_final_report()
        
        logger.info("InfoBot 已停止")
    
    def _health_check(self):
        """健康檢查"""
        logger.info("執行系統健康檢查")
        
        # 檢查WeChat狀態
        wechat_status = self.wechat_controller.check_wechat_status()
        
        # 檢查監控狀態
        monitoring_status = self.wechat_controller.get_monitoring_status()
        active_monitors = sum(1 for status in monitoring_status.values() if status)
        
        # 檢查消息處理狀態
        pending_count = len(self.message_handler.get_pending_messages())
        
        logger.info(f"健康檢查結果 - WeChat: {'正常' if wechat_status else '異常'}, "
                   f"活躍監控: {active_monitors}, 待處理消息: {pending_count}")
        
        # 如果有異常，嘗試恢復
        if not wechat_status:
            logger.warning("WeChat狀態異常，嘗試刷新")
            self.wechat_controller.refresh_wechat()
    
    def _generate_daily_report(self):
        """生成日常報告"""
        if not self.start_time:
            return
        
        runtime = datetime.now() - self.start_time
        teacher_msg_count = self.message_handler.get_teacher_message_count(24)
        
        report = f"""
📊 【InfoBot 日報】
運行時間: {runtime.days}天 {runtime.seconds//3600}小時
收到消息: {self.stats['messages_received']}
發送消息: {self.stats['messages_sent']}
轉發消息: {self.stats['messages_forwarded']}
自動回覆: {self.stats['auto_replies_sent']}
24小時內老師消息: {teacher_msg_count}
        """
        
        logger.info(report)
    
    def _generate_final_report(self):
        """生成最終報告"""
        if not self.start_time:
            return
        
        runtime = datetime.now() - self.start_time
        
        report = f"""
📈 【InfoBot 運行總結】
總運行時間: {runtime.days}天 {runtime.seconds//3600}小時 {(runtime.seconds%3600)//60}分鐘
總收到消息: {self.stats['messages_received']}
總發送消息: {self.stats['messages_sent']}
總轉發消息: {self.stats['messages_forwarded']}
總自動回覆: {self.stats['auto_replies_sent']}
        """
        
        logger.info(report)
    
    def get_status(self) -> Dict:
        """獲取機器人狀態"""
        runtime = None
        if self.start_time:
            runtime = str(datetime.now() - self.start_time)
        
        return {
            "is_running": self.is_running,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "runtime": runtime,
            "stats": self.stats.copy(),
            "monitoring_status": self.wechat_controller.get_monitoring_status(),
            "opened_windows": self.wechat_controller.get_opened_windows(),
            "pending_messages": len(self.message_handler.get_pending_messages())
        }
    
    def send_manual_message(self, contact_name: str, message: str) -> bool:
        """手動發送消息"""
        logger.info(f"手動向 {contact_name} 發送消息")
        
        success = self.wechat_controller.send_message(contact_name, message)
        if success:
            self.stats["messages_sent"] += 1
        
        return success
    
    def broadcast_message(self, message: str) -> Dict[str, bool]:
        """廣播消息給所有學生"""
        student_names = self.config.get_student_names()
        
        logger.info(f"向 {len(student_names)} 個學生廣播消息")
        
        results = self.wechat_controller.send_message_to_multiple_contacts(
            student_names, message
        )
        
        success_count = sum(1 for success in results.values() if success)
        self.stats["messages_sent"] += len(student_names)
        
        logger.info(f"廣播完成: {success_count}/{len(student_names)} 成功")
        
        return results 