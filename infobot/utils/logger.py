"""日誌管理模組"""

import sys
from pathlib import Path

from loguru import logger


def setup_logger(log_level: str = "INFO", log_file: str = "logs/infobot.log") -> None:
    """設置日誌配置"""
    
    # 移除默認處理器
    logger.remove()
    
    # 創建日誌目錄
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True)
    
    # 控制台輸出
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )
    
    # 文件輸出
    logger.add(
        log_file,
        level=log_level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="7 days",
        encoding="utf-8",
    )
    
    logger.info(f"日誌系統已初始化，級別: {log_level}")


def get_logger(name: str = None):
    """獲取日誌記錄器"""
    if name:
        return logger.bind(name=name)
    return logger 