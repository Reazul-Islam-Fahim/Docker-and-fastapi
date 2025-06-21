from pydantic import BaseModel
from typing import Optional

class ReplySchema(BaseModel):
    user_id: int
    product_id: int
    review_id: int = None
    comment: Optional[str] = None
    is_active: bool = True
    
    class Config:
        orm_mode = True