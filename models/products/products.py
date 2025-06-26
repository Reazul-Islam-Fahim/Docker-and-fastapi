from sqlalchemy import Column, Integer, String, Boolean, Float, ARRAY, Enum as sa_enum, ForeignKey, func
from sqlalchemy.orm import relationship
from database.db import Base
from enum import Enum
from models.associations import product_specific_features

class DiscountTypeEnum(Enum):
    fixed = "fixed"
    percentage = "percentage"

class Products(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=True, unique=True)
    description = Column(String(511), nullable=True)
    meta_title = Column(String(255), nullable=True)
    meta_description = Column(String(511), nullable=True)
    price = Column(Float, nullable=False)
    payable_price = Column(Float, nullable=False)
    discount_type = Column(sa_enum(DiscountTypeEnum), nullable=False)
    discount_amount = Column(Float, nullable=True, default=0.0)
    highlighted_image = Column(String(255), nullable=True)
    images = Column(ARRAY(String(255)), nullable=True)
    total_stock = Column(Integer, nullable=False, default=0)
    available_stock = Column(Integer, nullable=False, default=0)
    quantity_sold = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(String(50), nullable=False, server_default=func.now())
    updated_at = Column(String(50), nullable=False, server_default=func.now(), onupdate=func.now())

    sub_category_id = Column(Integer, ForeignKey("sub_categories.id"), nullable=False)
    brand_id = Column(Integer, ForeignKey("brands.id"), nullable=False)
    vendor_id = Column(Integer, ForeignKey("vendors.id"), nullable=False)

    sub_categories = relationship("SubCategories", back_populates="products")
    brands = relationship("Brands", back_populates="products")
    vendors = relationship("Vendors", back_populates="products")

    wishlist = relationship("Wishlist", back_populates="products")
    cart_items = relationship("CartItems", back_populates="products")
    inventory = relationship("Inventory", back_populates="products")
    reviews = relationship("Reviews", back_populates="products")
    reply = relationship("Reply", back_populates="products")
    order_items = relationship("OrderItems", back_populates="products")

    product_specific_features = relationship(
        "ProductFeatures",
        secondary=product_specific_features,
        back_populates="products",
        lazy="selectin"
    )
