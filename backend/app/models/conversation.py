from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.models.message import Message

class Conversation(BaseModel):
    user_id: str
    messages: List[Message] = []
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    ticket_number: Optional[str] = None
    waiting_for_confirmation: bool = False
    
    def add_message(self, message: Message):
        self.messages.append(message)
        self.updated_at = datetime.now()
    
    class Config:
        orm_mode = True