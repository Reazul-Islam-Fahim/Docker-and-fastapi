from sqlalchemy import Column, Integer, JSON, String, Boolean, func, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class Reviews(Base):
    __tablename__ = "reviews"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    rating = Column(Integer, nullable=True, default=4)
    content = Column(JSON, nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(String(50), nullable=False, server_default=func.now())
    updated_at = Column(String(50), nullable=False, server_default=func.now(), onupdate=func.now())
    
    user_id =  Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    users = relationship("Users", back_populates="reviews")
    products = relationship("Products", back_populates="reviews")
    reply = relationship("Reply", back_populates="reviews")
