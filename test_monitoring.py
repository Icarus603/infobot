#!/Users/liuzhehong/projects/my_projects/infobot/.venv/bin/python3
"""測試消息監控功能"""

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
setup_logger(log_level="DEBUG")
logger = get_logger(__name__)

def message_callback(sender: str, content: str):
    """消息回調函數"""
    print(f"\n🔔 收到消息!")
    print(f"發送者: {sender}")
    print(f"內容: {content}")
    print("-" * 50)

def main():
    """主函數"""
    print("=== InfoBot 消息監控測試 ===")
    
    try:
        # 載入配置
        config = Config.load_from_yaml("config/config.yaml")
        
        # 初始化 WeChat 控制器
        wechat_controller = WeChatController(config)
        
        # 添加消息回調
        wechat_controller.add_message_callback(message_callback)
        
        # 檢查狀態
        if not wechat_controller.check_wechat_status():
            print("❌ WeChat 狀態異常")
            return
        
        # 獲取老師列表
        teacher_names = config.get_teacher_names()
        if not teacher_names:
            print("❌ 沒有配置老師信息")
            return
        
        print(f"準備監控的老師: {teacher_names}")
        
        # 開始監控
        for teacher in teacher_names:
            print(f"開始監控: {teacher}")
            wechat_controller.start_monitoring_contact(teacher, check_interval=5.0)
        
        print("\n監控已啟動，等待消息...")
        print("按 Ctrl+C 停止監控")
        
        # 保持運行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n停止監控...")
            wechat_controller.stop_all_monitoring()
            print("監控已停止")
            
    except Exception as e:
        logger.error(f"測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 