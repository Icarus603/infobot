#!/Users/liuzhehong/projects/my_projects/infobot/.venv/bin/python3
"""測試改進後的消息監控功能"""

import sys
import time
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from infobot.core.wechat_controller import WeChatController
from infobot.utils.config import Config
from infobot.utils.logger import get_logger, setup_logger

# 設置日誌
setup_logger(log_level="INFO")
logger = get_logger(__name__)

def message_callback(sender: str, content: str):
    """消息回調函數"""
    print(f"\n🔔 檢測到活動!")
    print(f"聯繫人: {sender}")
    print(f"內容: {content}")
    print(f"時間: {time.strftime('%H:%M:%S')}")
    print("-" * 50)

def main():
    """主函數"""
    print("=== InfoBot 改進版消息監控測試 ===")
    
    try:
        # 載入配置
        config = Config.load_from_yaml("config/config.yaml")
        
        # 初始化 WeChat 控制器
        wechat_controller = WeChatController(config)
        
        # 添加消息回調
        wechat_controller.add_message_callback(message_callback)
        
        # 顯示配置的聯繫人
        all_contacts = []
        if config.teachers:
            all_contacts.extend(config.teachers)
        if config.students:
            all_contacts.extend(config.students)
        
        print(f"配置的聯繫人: {all_contacts}")
        
        if not all_contacts:
            print("❌ 沒有配置任何聯繫人")
            return
        
        # 開始監控所有聯繫人
        print("開始監控所有聯繫人...")
        wechat_controller.start_monitoring_all_contacts(check_interval=8.0)
        
        # 監控狀態
        status = wechat_controller.get_monitoring_status()
        print(f"監控狀態: {status}")
        
        # 保持運行
        print("\n監控已啟動，等待消息...")
        print("按 Ctrl+C 停止監控")
        
        try:
            while True:
                time.sleep(5)
                # 每5秒顯示一次狀態
                status = wechat_controller.get_monitoring_status()
                active_contacts = status['monitored_contacts']
                active_threads = status['active_threads']
                print(f"[{time.strftime('%H:%M:%S')}] 監控中: {active_contacts} ({active_threads} 個活動線程)")
                
        except KeyboardInterrupt:
            print("\n停止監控...")
            wechat_controller.stop_monitoring_all()
            print("✅ 已停止所有監控")
    
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {e}")
        print(f"❌ 測試失敗: {e}")

if __name__ == "__main__":
    main() 