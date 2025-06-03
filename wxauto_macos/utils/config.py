"""
配置管理模組
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class Config:
    """配置類"""
    
    # 微信相關配置
    wechat_bundle_id: str = "com.tencent.xinWeChat"
    wechat_process_name: str = "WeChat"
    
    # 自動化配置
    default_wait_time: float = 1.0
    click_delay: float = 0.5
    type_delay: float = 0.1
    screenshot_timeout: int = 5
    find_element_timeout: int = 10
    
    # 搜索配置
    search_wait_time: float = 2.0
    search_result_wait_time: float = 1.5
    
    # 消息配置
    message_send_delay: float = 0.5
    message_input_delay: float = 0.2
    
    # AppleScript 配置
    applescript_timeout: int = 30
    
    def __post_init__(self):
        """初始化後處理"""
        pass
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'Config':
        """從字典創建配置"""
        return cls(**{k: v for k, v in config_dict.items() if hasattr(cls, k)})
    
    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典"""
        return {
            'wechat_bundle_id': self.wechat_bundle_id,
            'wechat_process_name': self.wechat_process_name,
            'default_wait_time': self.default_wait_time,
            'click_delay': self.click_delay,
            'type_delay': self.type_delay,
            'screenshot_timeout': self.screenshot_timeout,
            'find_element_timeout': self.find_element_timeout,
            'search_wait_time': self.search_wait_time,
            'search_result_wait_time': self.search_result_wait_time,
            'message_send_delay': self.message_send_delay,
            'message_input_delay': self.message_input_delay,
            'applescript_timeout': self.applescript_timeout
        }


# 預設配置實例
config = Config() 