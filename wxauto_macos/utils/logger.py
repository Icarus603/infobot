"""
日誌記錄工具模組
"""

import logging
import sys
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """彩色日誌格式化器"""
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


def setup_logger(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """設置日誌記錄器"""
    logger = logging.getLogger(name or "wxauto_macos")
    
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # 創建控制台處理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    
    # 設置格式
    formatter = ColoredFormatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.propagate = False
    
    return logger


# 創建預設的日誌記錄器
logger = setup_logger() 