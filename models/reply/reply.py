from sqlalchemy import Column, Integer, String, Boolean, func, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class Reply(Base):
    __tablename__ = "reply"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    comment = Column(String(255), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(String(50), nullable=False, server_default=func.now())
    updated_at = Column(String(50), nullable=False, server_default=func.now(), onupdate=func.now())
    
    user_id =  Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    review_id = Column(Integer, ForeignKey("reviews.id"), nullable=True)
    
    users = relationship("Users", back_populates="reply")
    products = relationship("Products", back_populates="reply")
    reviews = relationship("Reviews", back_populates="reply")
