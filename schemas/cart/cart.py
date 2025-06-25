from typing import List, Optional
from pydantic import BaseModel
from schemas.cart_items.cart_items import CartItemsSchema

class CartSchema(BaseModel):
    user_id : int
    cart_items: Optional[List[CartItemsSchema]]
    
    class Config:
        orm_mode = True