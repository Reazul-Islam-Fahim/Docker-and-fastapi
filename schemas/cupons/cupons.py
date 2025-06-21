from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CuponsSchema(BaseModel):
    code: str
    discount_percentage: int
    max_discount: int
    min_purchase: int
    max_used: int
    used_count: Optional[int] = 0
    is_active: Optional[bool] = True
    expires_at: datetime 
        
    class Config:
        from_attributes = True