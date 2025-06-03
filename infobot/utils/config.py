"""配置管理模組"""

import os
from pathlib import Path
from typing import Any, Dict, List

import yaml
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# 簡化配置，不再使用複雜的數據類別


class SiliconFlowConfig(BaseModel):
    """SiliconFlow API配置"""
    api_key: str = Field(..., description="API金鑰")
    base_url: str = Field("https://api.siliconflow.cn/v1", description="API基礎URL")
    model: str = Field("Pro/deepseek-ai/DeepSeek-R1-0120", description="使用的模型")
    max_tokens: int = Field(512, description="最大token數")
    temperature: float = Field(0.7, description="溫度參數")


# WeChatAutomationConfig 已移除，使用 wxauto_macos 的內建配置


class Config(BaseSettings):
    """主配置類"""
    
    # 基本配置
    debug: bool = Field(False, description="調試模式")
    log_level: str = Field("INFO", description="日誌級別")
    
    # API配置
    siliconflow: SiliconFlowConfig
    
    # 自動化配置已簡化（由 wxauto_macos 管理）
    
    # 用戶配置
    teachers: List[str] = Field(default_factory=list)
    students: List[str] = Field(default_factory=list)
    
    # 提示詞配置
    prompts: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
    
    @classmethod
    def load_from_yaml(cls, config_path: str = "config/config.yaml") -> "Config":
        """從YAML文件載入配置"""
        config_file = Path(config_path)
        
        if not config_file.exists():
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config_data = yaml.safe_load(f)
        
        # 載入提示詞
        prompts_file = Path("config/prompts.yaml")
        if prompts_file.exists():
            with open(prompts_file, 'r', encoding='utf-8') as f:
                prompts_data = yaml.safe_load(f)
                config_data.setdefault('prompts', {}).update(prompts_data)
        
        return cls(**config_data)
    
    def get_teacher_names(self) -> List[str]:
        """獲取所有老師的微信備註名稱"""
        return self.teachers
    
    def get_student_names(self) -> List[str]:
        """獲取所有學生的微信備註名稱"""
        return self.students
    
    def is_teacher(self, name: str) -> bool:
        """檢查是否為老師"""
        return name in self.teachers
    
    def is_student(self, name: str) -> bool:
        """檢查是否為學生"""
        return name in self.students 