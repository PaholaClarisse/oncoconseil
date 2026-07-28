from pydantic import BaseModel
from datetime import datetime
from app.models.message import MessageRole

class MessageOut(BaseModel):
    role: MessageRole
    content: str
    created_at: datetime

    class Config:
        from_attributes = True