from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class SlidersSchema(BaseModel):
    link: str
    expiration_date: datetime
    slider_type_id: int
    vendor_id: int
    payment_id: Optional[int] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class UpdateSlidersSchema(BaseModel):
    link: Optional[str] = None
    expiration_date: Optional[datetime] = None
    slider_type_id: Optional[int] = None
    vendor_id: Optional[int] = None
    payment_id: Optional[int] = None
    category_id: Optional[int] = None
    sub_category_id: Optional[int] = None
    is_active: Optional[bool] = True
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True