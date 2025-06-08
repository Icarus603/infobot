"""消息處理器模組"""

import time
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional

from ..ai.siliconflow_client import SiliconFlowClient
from ..utils.config import Config
from ..utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class Message:
    """消息數據類"""
    sender: str
    content: str
    timestamp: datetime
    message_type: str = "text"
    is_from_teacher: bool = False
    processed: bool = False


class MessageHandler:
    """消息處理器"""
    
    def __init__(self, config: Config, ai_client: SiliconFlowClient):
        """初始化消息處理器"""
        self.config = config
        self.ai_client = ai_client
        self.message_queue: List[Message] = []
        self.processed_messages: List[Message] = []
        self.message_callbacks: Dict[str, List[Callable]] = {
            "teacher_message": [],
            "student_message": [],
            "unknown_message": []
        }
        
    def add_message_callback(self, message_type: str, callback: Callable):
        """添加消息回調函數"""
        if message_type in self.message_callbacks:
            self.message_callbacks[message_type].append(callback)
        else:
            logger.warning(f"未知的消息類型: {message_type}")
    
    def process_incoming_message(self, sender: str, content: str) -> Optional[Message]:
        """處理收到的消息"""
        try:
            # 創建消息對象
            message = Message(
                sender=sender,
                content=content,
                timestamp=datetime.now(),
                is_from_teacher=self.config.is_teacher(sender)
            )
            
            logger.info(f"收到來自 {sender} 的消息: {content[:50]}...")
            
            # 只添加到消息隊列，不立即處理，讓主循環統一處理
            self.message_queue.append(message)
            
            logger.info(f"消息已加入處理隊列，當前隊列長度: {len(self.message_queue)}")
            
            return message
            
        except Exception as e:
            logger.error(f"處理消息時發生錯誤: {e}")
            return None
    
    def _handle_teacher_message(self, message: Message):
        """處理老師的消息"""
        logger.info(f"處理老師 {message.sender} 的消息")
        
        # 調用回調函數
        for callback in self.message_callbacks["teacher_message"]:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"執行老師消息回調時發生錯誤: {e}")
    
    def _handle_student_message(self, message: Message):
        """處理學生的消息"""
        logger.info(f"處理學生 {message.sender} 的消息")
        
        # 調用回調函數
        for callback in self.message_callbacks["student_message"]:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"執行學生消息回調時發生錯誤: {e}")
    
    def _handle_unknown_message(self, message: Message):
        """處理未知用戶的消息"""
        logger.warning(f"收到來自未知用戶 {message.sender} 的消息")
        
        # 調用回調函數
        for callback in self.message_callbacks["unknown_message"]:
            try:
                callback(message)
            except Exception as e:
                logger.error(f"執行未知消息回調時發生錯誤: {e}")
    
    def generate_auto_reply(self, message: Message) -> str:
        """生成自動回覆"""
        if message.is_from_teacher:
            # 對老師的消息統一回覆"收到！"
            return "收到！"
        else:
            # 對其他消息可以有不同的回覆策略
            return "收到您的消息，我會盡快處理。"
    
    def generate_forward_message(self, original_message: Message) -> str:
        """生成轉發消息（直接轉發原文，不使用AI加工）"""
        return self._generate_simple_forward_message(original_message)
    
    def _generate_simple_forward_message(self, original_message: Message) -> str:
        """生成簡單的轉發消息"""
        timestamp = original_message.timestamp.strftime("%Y-%m-%d %H:%M")
        
        return f"""📢 【班級通知】
來源：{original_message.sender}
時間：{timestamp}

{original_message.content}

請大家注意查看！
---
班長轉發"""
    
    def analyze_message_should_forward(self, message: Message) -> bool:
        """使用AI分析消息是否應該轉發"""
        try:
            if self.config.prompts.get("use_ai_for_analysis", True):
                analysis_result = self.ai_client.analyze_message(
                    message.content,
                    f"發送者: {message.sender}"
                )
                return "需要轉發" in analysis_result
            else:
                # 回退到關鍵詞檢查
                return self._check_keywords_for_forwarding(message.content)
                
        except Exception as e:
            logger.error(f"分析消息是否轉發失敗: {e}")
            # 回退到關鍵詞檢查
            return self._check_keywords_for_forwarding(message.content)
    
    def _check_keywords_for_forwarding(self, content: str) -> bool:
        """使用關鍵詞檢查是否需要轉發"""
        content_lower = content.lower()
        
        # 檢查重要關鍵詞
        important_keywords = self.config.prompts.get("important_keywords", [])
        for keyword in important_keywords:
            if keyword in content_lower:
                return True
        
        # 檢查非重要關鍵詞
        unimportant_keywords = self.config.prompts.get("unimportant_keywords", [])
        for keyword in unimportant_keywords:
            if keyword in content_lower:
                return False
        
        # 預設情況下，如果消息足夠長且來自老師，則轉發
        return len(content.strip()) >= self.config.prompts.get("min_message_length", 5)
    
    def should_forward_message(self, message: Message) -> bool:
        """判斷是否應該轉發消息"""
        # 只轉發老師的消息
        if not message.is_from_teacher:
            return False
        
        # 檢查是否在黑名單關鍵詞中
        blacklist_keywords = self.config.prompts.get("blacklist_keywords", [])
        for keyword in blacklist_keywords:
            if keyword.lower() in message.content.lower():
                logger.info(f"消息包含黑名單關鍵詞 '{keyword}'，不轉發")
                return False
        
        # 檢查消息長度
        min_length = self.config.prompts.get("min_message_length", 5)
        if len(message.content.strip()) < min_length:
            logger.info("消息過短，不轉發")
            return False
        
        # 使用AI或關鍵詞分析是否需要轉發
        return self.analyze_message_should_forward(message)
    
    def get_target_students(self, message: Message) -> List[str]:
        """獲取消息轉發目標學生列表（簡化版：轉發給所有學生）"""
        return self.config.get_student_names()
    
    def mark_message_processed(self, message: Message):
        """標記消息為已處理"""
        message.processed = True
        message.timestamp = datetime.now()
        
        # 移動到已處理消息列表
        if message in self.message_queue:
            self.message_queue.remove(message)
        
        self.processed_messages.append(message)
        
        # 保持已處理消息列表不超過一定數量
        max_processed = 1000
        if len(self.processed_messages) > max_processed:
            self.processed_messages = self.processed_messages[-max_processed:]
    
    def get_pending_messages(self) -> List[Message]:
        """獲取待處理的消息"""
        return [msg for msg in self.message_queue if not msg.processed]
    
    def get_teacher_message_count(self, hours: int = 24) -> int:
        """獲取指定時間內老師消息數量"""
        cutoff_time = datetime.now().timestamp() - (hours * 3600)
        
        count = 0
        for msg in self.processed_messages + self.message_queue:
            if (msg.is_from_teacher and 
                msg.timestamp.timestamp() > cutoff_time):
                count += 1
        
        return count
    
    def cleanup_old_messages(self, days: int = 7):
        """清理舊消息"""
        cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
        
        # 清理已處理消息
        self.processed_messages = [
            msg for msg in self.processed_messages
            if msg.timestamp.timestamp() > cutoff_time
        ]
        
        # 清理消息隊列中的舊消息
        self.message_queue = [
            msg for msg in self.message_queue
            if msg.timestamp.timestamp() > cutoff_time
        ]
        
        logger.info(f"清理了 {days} 天前的舊消息") 