"""
MacOS 微信自動化庫 - 參照 wxauto 設計理念

這個庫提供了在 macOS 上自動化操作微信的功能，
類似於 Windows 版本的 wxauto，但使用 AppleScript 和 Accessibility API。

作者: InfoBot 團隊
版本: 1.0.0
"""

from .utils import config, logger
from .wechat import WeChat

VERSION = "1.1.0"

__all__ = ['WeChat', 'VERSION', 'logger', 'config'] 