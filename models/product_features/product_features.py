from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from database.db import Base
from models.associations import sub_category_features  

class ProductFeatures(Base):
    __tablename__ = 'product_features'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(String, nullable=False)  
    value = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    sub_categories = relationship(
        "SubCategories",
        secondary=sub_category_features,
        back_populates="product_features"
    )
