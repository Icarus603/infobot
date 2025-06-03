"""SiliconFlow API 客戶端"""

from typing import Any, Dict, List, Optional

import requests

from ..utils.config import SiliconFlowConfig
from ..utils.logger import get_logger

logger = get_logger(__name__)


class SiliconFlowClient:
    """SiliconFlow API 客戶端"""
    
    def __init__(self, config: SiliconFlowConfig):
        """初始化客戶端"""
        self.config = config
        self.base_url = config.base_url
        self.api_key = config.api_key
        self.model = config.model
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """聊天完成API調用"""
        
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
            "max_tokens": max_tokens or self.config.max_tokens,
            "temperature": temperature or self.config.temperature,
            "top_p": 0.7,
            "top_k": 50,
            "frequency_penalty": 0.5,
            "n": 1,
            "response_format": {"type": "text"}
        }
        
        try:
            logger.info(f"發送請求到SiliconFlow API: {self.model}")
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            logger.info("成功獲取AI回應")
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API請求失敗: {e}")
            raise
        except Exception as e:
            logger.error(f"處理回應時發生錯誤: {e}")
            raise
    
    def analyze_message(self, message: str, context: str = "") -> str:
        """分析消息是否需要轉發"""
        
        system_prompt = """你是一個智能微信機器人助手，專門幫助大學班長判斷老師的消息是否需要轉發給學生。
        
        請判斷以下消息是否需要轉發給全班同學：
        - 如果是班級相關的重要通知、學業安排、科研信息、保研通知、集體活動等，回答"需要轉發"
        - 如果是私人聊天、個人問候、非正式交流等，回答"不需要轉發"
        
        只需要回答"需要轉發"或"不需要轉發"，不要添加其他內容。"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"上下文：{context}\n\n消息內容：{message}"}
        ]
        
        try:
            response = self.chat_completion(messages)
            if response.get("choices") and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"].strip()
            else:
                logger.warning("AI回應格式異常")
                return "不需要轉發"
                
        except Exception as e:
            logger.error(f"消息分析失敗: {e}")
            return "不需要轉發"
    
    def generate_forward_message(self, original_message: str, teacher_name: str) -> str:
        """生成轉發消息"""
        
        system_prompt = """你是一個大學班長，負責將老師的消息轉發給同學們。
        請將老師的原始消息整理成適合轉發給同學們的格式。
        
        要求：
        1. 保持原始信息的完整性
        2. 添加適當的標題和來源說明
        3. 使用正式但友好的語調
        4. 突出重要信息
        
        格式示例：
        📢 【重要通知】
        來源：[老師姓名]
        
        [整理後的消息內容]
        
        請大家注意查看！"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"老師姓名：{teacher_name}\n原始消息：{original_message}"}
        ]
        
        try:
            response = self.chat_completion(messages)
            if response.get("choices") and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"].strip()
            else:
                # 如果AI回應失敗，使用簡單的模板
                return f"📢 【通知】\n來源：{teacher_name}\n\n{original_message}\n\n請大家注意查看！"
                
        except Exception as e:
            logger.error(f"生成轉發消息失敗: {e}")
            return f"📢 【通知】\n來源：{teacher_name}\n\n{original_message}\n\n請大家注意查看！" 