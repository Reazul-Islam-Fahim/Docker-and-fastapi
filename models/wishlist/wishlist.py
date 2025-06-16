from sqlalchemy import Column, Integer, String, Boolean, func, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class Wishlist(Base):
    __tablename__ = "wishlist"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    created_at = Column(String(50), nullable=False, server_default=func.now())
    
    users = relationship("Users", back_populates="wishlist")
    products = relationship("Products", back_populates="wishlist")
