from sqlalchemy import Column, ForeignKey, Integer, String, func, Enum as senum, Boolean
from sqlalchemy.orm import relationship
from database.db import Base
from enum import Enum

class NotificationType(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"

class Notifications(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    message = Column(String(255), nullable=False)
    type = Column(senum(NotificationType), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    created_at = Column(String(50), nullable=False, server_default=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    users = relationship("Users", back_populates="notifications")
    
