from pydantic import BaseModel
from typing import Optional, List
from models.products.products import DiscountTypeEnum

class ProductsSchema(BaseModel):
    name: str
    description: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    price: float
    discount_type: Optional[DiscountTypeEnum] = None 
    discount_amount: Optional[int] = 0
    highlighted_image: Optional[str] = None
    images: Optional[List[str]] = None
    is_active: bool = True
    sub_category_id: int
    brand_id: int
    vendor_id: int
    product_specific_features: list[int]

    class Config:
        orm_mode = True
