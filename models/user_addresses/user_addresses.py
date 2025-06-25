from sqlalchemy import Column, Integer, String, Boolean, func, ForeignKey
from sqlalchemy.orm import relationship
from database.db import Base

class UserAddresses(Base):
    __tablename__ = "user_addresses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    address_line = Column(String(255), nullable=False)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=False)
    postal_code = Column(String(20), nullable=False)
    country = Column(String(100), nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    users = relationship("Users", back_populates="user_addresses")
    orders = relationship("Orders", back_populates="user_addresses")
