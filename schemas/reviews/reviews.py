from pydantic import BaseModel
from typing import Optional

class ReviewsSchema(BaseModel):
    rating: Optional[int] = 4
    comment: Optional[str] = None
    image: Optional[str] = None
    user_id: Optional[int]
    product_id: Optional[int]
    is_active: bool = True
    
    class Config:
        orm_mode = True