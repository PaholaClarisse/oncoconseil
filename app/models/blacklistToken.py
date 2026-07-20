from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base
from datetime import datetime
from sqlalchemy.orm import relationship

class BlacklistToken(Base):
    __tablename__ = 'blacklist_tokens'

    id = Column(Integer, primary_key =True, index=True, autoincrement=True)
    jti = Column(String, unique=True, nullable=False)
    expired_at = Column(DateTime(timezone=True), nullable=False)  