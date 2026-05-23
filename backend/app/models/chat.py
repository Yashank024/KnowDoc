from typing import List, Optional
from pydantic import BaseModel

class ChatMessage(BaseModel):
    id: str
    sender: str  # 'user' or 'ai'
    text: str
    timestamp: str
    isStreaming: Optional[bool] = False

class ChatSession(BaseModel):
    id: str
    title: str
    timestamp: str
    messages: List[ChatMessage] = []
