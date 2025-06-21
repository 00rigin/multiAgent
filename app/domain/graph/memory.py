from typing import Dict, List, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from datetime import datetime
import json

class ChatMemory:
    def __init__(self, max_messages: int = 50):
        self.max_messages = max_messages
        self.conversations: Dict[str, List[BaseMessage]] = {}
    
    def add_message(self, session_id: str, message: BaseMessage):
        """세션에 메시지를 추가합니다."""
        if session_id not in self.conversations:
            self.conversations[session_id] = []
        
        self.conversations[session_id].append(message)
        
        # 최대 메시지 수를 초과하면 오래된 메시지 제거
        if len(self.conversations[session_id]) > self.max_messages:
            self.conversations[session_id] = self.conversations[session_id][-self.max_messages:]
    
    def get_messages(self, session_id: str) -> List[BaseMessage]:
        """세션의 메시지 히스토리를 반환합니다."""
        return self.conversations.get(session_id, [])
    
    def clear_session(self, session_id: str):
        """세션의 메시지를 모두 삭제합니다."""
        if session_id in self.conversations:
            del self.conversations[session_id]
    
    def get_session_count(self) -> int:
        """활성 세션 수를 반환합니다."""
        return len(self.conversations)
    
    def get_total_messages(self) -> int:
        """전체 메시지 수를 반환합니다."""
        return sum(len(messages) for messages in self.conversations.values())

# 전역 메모리 인스턴스
chat_memory = ChatMemory() 