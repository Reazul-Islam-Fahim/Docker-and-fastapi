from sqlalchemy import Column, ForeignKey, Integer, String, Boolean, func, DateTime
from database.db import Base
from sqlalchemy.orm import relationship

class Sliders(Base):
    __tablename__ = "sliders"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    image = Column(String, nullable=False)
    link = Column(String(255), nullable=False)
    is_paid = Column(Boolean, nullable=False, default=False)
    is_active = Column(Boolean, nullable=False, default=True)
    expiration_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    slider_type_id = Column(Integer, ForeignKey("slider_type.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)
    payment_id = Column(Integer, ForeignKey("payments.id"), nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    sub_category_id = Column(Integer, ForeignKey("sub_categories.id"), nullable=True)

    # Relationships
    slider_type = relationship("SliderType", back_populates="sliders")
    vendors = relationship("Vendors", back_populates="sliders")
    payments = relationship("Payments", back_populates="sliders")
    categories = relationship("Categories", back_populates="sliders")
    sub_categories = relationship("SubCategories", back_populates="sliders")