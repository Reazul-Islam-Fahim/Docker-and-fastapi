from sqlalchemy import Column, Integer, String, func, ForeignKey, Float, Enum as senum, ARRAY, JSON
from sqlalchemy.orm import relationship
from database.db import Base
from enum import Enum

class InventoryTypeEnum(str, Enum):
    purchase = "purchase"
    sell = "sell"
    returrn = "return"
    adjustment = "adjustment"
    damage = "damage"
    restock = "restock"

    
class Inventory(Base):
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    unit_price = Column(Float, nullable=False)
    total_quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    inventory_type = Column(senum(InventoryTypeEnum), nullable=False)
    invoice_number = Column(String(50), nullable=False)
    notes = Column(String(511), nullable=True)
    created_at = Column(String(50), nullable=False, server_default=func.now())
    updated_at = Column(String(50), nullable=False, server_default=func.now(), onupdate=func.now())
    
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    
    products = relationship("Products", back_populates="inventory")
    vendors = relationship("Vendors", back_populates="inventory")