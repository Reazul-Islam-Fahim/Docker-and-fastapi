from sqlalchemy import Column, Integer, String, Boolean, func, ForeignKey, Enum as senum
from sqlalchemy.orm import relationship
from database.db import Base


class PaymentMethod(Base):
    __tablename__ = "payment_method"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)

    payments = relationship("Payments", back_populates="payment_method")