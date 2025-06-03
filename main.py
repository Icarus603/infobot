#!/Users/liuzhehong/projects/my_projects/infobot/.venv/bin/python3
"""
InfoBot - 智能微信機器人主程式
用於自動化處理班級事務通知的微信機器人

作者: Icarus <zhehongl91@gmail.com>
"""

import signal
import sys
from pathlib import Path

from infobot.core.bot import InfoBot
from infobot.utils.logger import get_logger, setup_logger

# 添加項目根目錄到路徑
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 全局變量存儲機器人實例
bot_instance = None


def signal_handler(signum, frame):
    """信號處理器，用於優雅關閉"""
    global bot_instance
    logger = get_logger(__name__)
    
    logger.info(f"收到信號 {signum}，正在關閉機器人...")
    
    if bot_instance:
        bot_instance.stop()
    
    logger.info("機器人已關閉")
    sys.exit(0)


def check_requirements():
    """檢查運行環境和必需文件"""
    import subprocess
    logger = get_logger(__name__)
    
    # 檢查微信進程是否在運行
    logger.info("正在檢查微信運行狀態...")
    try:
        result = subprocess.run(['pgrep', '-f', 'WeChat'], capture_output=True, text=True)
        if result.returncode != 0:
            logger.error("❌ 微信應用未運行！")
            logger.error("請執行以下步驟：")
            logger.error("1. 打開微信應用")
            logger.error("2. 確保已登錄")
            logger.error("3. 重新運行此程序")
            return False
        
        pids = result.stdout.strip().split('\n')
        logger.info(f"✅ 檢測到微信進程：{len(pids)} 個")
        
    except Exception as e:
        logger.error(f"❌ 檢查微信進程失敗: {e}")
        return False
    
    # 檢查權限已簡化（由 wxauto_macos 處理）
    logger.info("✅ 權限檢查已簡化，將在初始化時驗證")
    
    # 檢查配置文件
    config_file = Path("config/config.yaml")
    if not config_file.exists():
        logger.error("配置文件不存在: config/config.yaml")
        logger.info("請複製 config/config.example.yaml 為 config/config.yaml 並填入配置")
        return False
    
    # 檢查日誌目錄
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # 檢查腳本目錄
    scripts_dir = Path("scripts")
    scripts_dir.mkdir(exist_ok=True)
    
    logger.info("✅ 所有前提條件檢查通過")
    return True


def main():
    """主函數"""
    global bot_instance
    
    # 設置日誌
    setup_logger()
    logger = get_logger(__name__)
    
    logger.info("=" * 50)
    logger.info("InfoBot - 智能微信機器人 啟動中...")
    logger.info("=" * 50)
    
    # 檢查運行環境
    if not check_requirements():
        logger.error("環境檢查失敗，程式退出")
        sys.exit(1)
    
    # 設置信號處理器
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        # 創建機器人實例
        logger.info("正在初始化 InfoBot...")
        bot_instance = InfoBot()
        
        # 顯示配置信息
        teacher_names = bot_instance.config.get_teacher_names()
        student_names = bot_instance.config.get_student_names()
        
        logger.info(f"配置載入完成:")
        logger.info(f"  - AI模型: {bot_instance.config.siliconflow.model}")
        logger.info(f"  - 日誌級別: {bot_instance.config.log_level}")
        logger.info("")
        
        # 顯示老師信息
        logger.info(f"📚 老師列表 (共 {len(teacher_names)} 位):")
        if teacher_names:
            for i, teacher in enumerate(teacher_names, 1):
                logger.info(f"     {i}. {teacher}")
        else:
            logger.warning("  ⚠️  未配置任何老師！")
        logger.info("")
        
        # 顯示學生信息
        logger.info(f"🎓 學生列表 (共 {len(student_names)} 位):")
        if student_names:
            for i, student in enumerate(student_names, 1):
                logger.info(f"     {i}. {student}")
        else:
            logger.warning("  ⚠️  未配置任何學生！")
        logger.info("")
        
        # 驗證配置
        if not teacher_names:
            logger.error("❌ 錯誤：沒有配置任何老師！")
            logger.error("請在 config/config.yaml 的 teachers 節點下添加老師的微信備註名稱")
            sys.exit(1)
            
        if not student_names:
            logger.error("❌ 錯誤：沒有配置任何學生！")
            logger.error("請在 config/config.yaml 的 students 節點下添加學生的微信備註名稱")
            sys.exit(1)
        
        # 顯示注意事項
        logger.info("\n" + "=" * 50)
        logger.info("重要提醒:")
        logger.info("1. 請確保已給予終端機「輔助使用」權限")
        logger.info("2. 請確保 WeChat 桌面版已啟動並登錄")
        logger.info("3. 機器人將自動監控老師消息並轉發給學生")
        logger.info("4. 按 Ctrl+C 可優雅停止機器人")
        logger.info("=" * 50 + "\n")
        
        # 啟動機器人
        bot_instance.start()
        
    except KeyboardInterrupt:
        logger.info("收到停止信號")
    except FileNotFoundError as e:
        logger.error(f"文件未找到: {e}")
        logger.info("請檢查配置文件是否存在且格式正確")
    except Exception as e:
        logger.error(f"運行時發生錯誤: {e}", exc_info=True)
    finally:
        if bot_instance:
            bot_instance.stop()


if __name__ == "__main__":
    main() 