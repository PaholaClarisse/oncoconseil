import enum
from sqlalchemy import Column, Integer, String, DateTime, func, ForeignKey, Enum
from app.database import Base

class MessageRole(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    content = Column(String, nullable=False)
    role = Column(Enum(MessageRole), nullable=False)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())