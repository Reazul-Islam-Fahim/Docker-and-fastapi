from pydantic import BaseModel
from typing import Optional

class CartItemsSchema(BaseModel):
    product_id: int
    cart_id: int
    quantity: Optional[int] = 1
    cost: Optional[int] = 0
    
    class Config:
        orm_mode = True