from sqlalchemy import Column, Integer, String, Boolean, func, DateTime
from sqlalchemy.orm import relationship
from database.db import Base

class Cupons(Base):
    __tablename__ = "cupons"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_percentage = Column(Integer, nullable=False)
    max_discount = Column(Integer, nullable=False)
    min_purchase = Column(Integer, nullable=False)
    max_used = Column(Integer, nullable=False)
    used_count = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
