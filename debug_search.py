#!/Users/liuzhehong/projects/my_projects/infobot/.venv/bin/python3
"""
調試搜索功能
"""
import sys
from pathlib import Path

# 添加項目根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import wxauto_macos
from infobot.utils.config import Config


def debug_search():
    """調試搜索功能"""
    print("=== 調試搜索功能 ===")
    
    # 讀取配置
    config = Config.load_from_yaml("config/config.yaml")
    print(f"老師列表: {config.get_teacher_names()}")
    print(f"學生列表: {config.get_student_names()}")
    
    # 初始化 WeChat
    try:
        wechat = wxauto_macos.WeChat()
        print("✅ WeChat 初始化成功")
        
        # 只測試一個聯繫人的雙擊功能
        if config.get_student_names():
            student_name = config.get_student_names()[0]
            print(f"\n正在測試學生雙擊功能: '{student_name}'")
            
            # 步驟1：先搜索並進入對話
            print("步驟1: 搜索並進入對話...")
            result = wechat._search_and_click_contact(student_name)
            print(f"搜索結果: {result}")
            
            if result:
                print("\n步驟2: 等待3秒後測試雙擊左邊欄...")
                import time
                time.sleep(3)
                
                # 步驟2：直接測試雙擊座標功能
                print("步驟3: 直接測試改進後的雙擊座標功能...")
                double_click_result = wechat._double_click_sidebar_by_coordinates(student_name)
                print(f"雙擊結果: {double_click_result}")
                
                print("\n請檢查是否打開了獨立對話框！")
                print("新版本使用了 PyAutoGUI 的內建 doubleClick() 函數，應該更穩定。")
            else:
                print("搜索失敗，無法測試雙擊功能")
            
    except Exception as e:
        print(f"❌ 錯誤: {e}")

if __name__ == "__main__":
    debug_search() 