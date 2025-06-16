from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.orm import relationship
from database.db import Base

class CartItems(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    quantity = Column(Integer, nullable=False, default=1)
    cost = Column(Integer, nullable=False, default=0)
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    cart_id = Column(Integer, ForeignKey("cart.id"), nullable=False)
    
    products = relationship("Products", back_populates="cart_items")
    cart = relationship("Cart", back_populates="cart_items")
    
