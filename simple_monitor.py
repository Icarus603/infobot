#!/Users/liuzhehong/projects/my_projects/infobot/.venv/bin/python3
"""簡化的消息監控測試"""

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

def test_message_detection():
    """測試消息檢測功能"""
    print("=== 簡化的消息檢測測試 ===")
    
    try:
        # 初始化微信
        wechat = wxauto_macos.WeChat()
        
        # 載入配置
        config = Config.load_from_yaml("config/config.yaml")
        teacher_name = config.get_teacher_names()[0]
        
        print(f"準備監控: {teacher_name}")
        
        # 打開聊天窗口
        print("正在打開聊天窗口...")
        success = wechat._open_chat(teacher_name)
        
        if not success:
            print("❌ 無法打開聊天窗口")
            return
        
        print("✅ 聊天窗口已打開")
        print("開始監控新消息...")
        print("請在微信中發送一條消息，然後等待檢測...")
        
        last_message_count = 0
        check_count = 0
        
        while check_count < 20:  # 最多檢查20次，每次間隔3秒
            check_count += 1
            print(f"\n--- 第 {check_count} 次檢查 ---")
            
            # 重新打開聊天確保處於正確狀態
            wechat._open_chat(teacher_name)
            time.sleep(1)  # 等待窗口穩定
            
            # 獲取消息
            messages = wechat.GetAllMessage()
            current_count = len(messages)
            
            print(f"當前消息數量: {current_count}")
            
            if current_count > last_message_count:
                print(f"🔔 檢測到新消息！({last_message_count} -> {current_count})")
                
                # 顯示新消息
                if messages:
                    for i, msg in enumerate(messages[last_message_count:]):
                        print(f"新消息 {i+1}: {msg}")
                
                last_message_count = current_count
                print("✅ 成功檢測到消息變化！")
                break
            else:
                print("沒有檢測到新消息")
            
            print("等待3秒後繼續檢查...")
            time.sleep(3)
        
        if check_count >= 20:
            print("⚠️ 達到最大檢查次數，測試結束")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_message_detection() 