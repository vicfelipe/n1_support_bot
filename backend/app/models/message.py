from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional

class MessageType(str, Enum):
    USER = "user"
    BOT = "bot"
    SYSTEM = "system"

class Message(BaseModel):
    id: int
    content: str
    type: MessageType
    timestamp: datetime = datetime.now()
    metadata: Optional[dict] = None
    
    class Config:
        orm_mode = True