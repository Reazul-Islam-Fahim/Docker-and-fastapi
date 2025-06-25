from sqlalchemy import Column, Integer, String, func, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base


class Payments(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    amount = Column(Integer, nullable=False)
    transaction_id = Column(String(255), unique=True, nullable=False)
    created_at = Column(String(50), nullable=False, server_default=func.now())
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    payment_method_id = Column(Integer, ForeignKey("payment_method.id"), nullable=False)

    users = relationship("Users", back_populates="payments")
    orders = relationship("Orders", back_populates="payments")
    payment_method = relationship("PaymentMethod", back_populates="payments")