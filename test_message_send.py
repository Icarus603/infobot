#!/Users/liuzhehong/projects/my_projects/infobot/.venv/bin/python3
"""測試發送消息功能"""

import sys
import time
from pathlib import Path

# 添加項目路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import wxauto_macos
from infobot.utils.config import Config
from infobot.utils.logger import get_logger, setup_logger

# 設置日誌
setup_logger(log_level="INFO")
logger = get_logger(__name__)

def test_send_message():
    """測試發送消息功能"""
    print("=== 測試發送消息功能 ===")
    
    try:
        # 初始化微信
        wechat = wxauto_macos.WeChat()
        
        # 載入配置
        config = Config.load_from_yaml("config/config.yaml")
        teacher_name = config.get_teacher_names()[0]
        
        print(f"準備向 {teacher_name} 發送測試消息")
        
        # 發送測試消息
        test_message = f"測試消息 - {time.strftime('%H:%M:%S')}"
        
        print(f"發送消息: {test_message}")
        success = wechat.SendMsg(test_message, teacher_name)
        
        if success:
            print("✅ 消息發送成功！")
            print("現在可以檢查微信是否收到消息")
        else:
            print("❌ 消息發送失敗")
            
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_send_message() 