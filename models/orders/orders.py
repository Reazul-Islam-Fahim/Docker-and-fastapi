from sqlalchemy import Column, Integer, String, Boolean, func, ForeignKey, Enum as senum
from sqlalchemy.orm import relationship
from database.db import Base
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    RETURNED = "returned"
    CANCELLED = "cancelled"
    
class DeliveryStatus(str, Enum):
    PENDING = "pending"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    RETURNED = "returned"


class Orders(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    total_amount = Column(Integer, nullable=False, default=0)
    is_paid = Column(Boolean, default=False)
    status = Column(senum(OrderStatus), nullable=False, default=OrderStatus.PENDING)
    delivery_charge = Column(Integer, nullable=False, default=0)
    delivery_status = Column(senum(DeliveryStatus), nullable=False, default=DeliveryStatus.PENDING)
    placed_at = Column(String(50), nullable=False, server_default=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    shipping_address_id = Column(Integer, ForeignKey("user_addresses.id"), nullable=False)
    
    users = relationship("Users", back_populates="orders")
    user_addresses = relationship("UserAddresses", back_populates="orders")
    order_items = relationship("OrderItems", back_populates="orders")
    payments = relationship("Payments", back_populates="orders")