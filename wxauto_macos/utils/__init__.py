"""
MacOS 微信自動化庫 - 工具模組

提供日誌記錄、配置管理等工具功能
"""

from .config import Config
from .logger import logger

__all__ = ['logger', 'Config'] 
