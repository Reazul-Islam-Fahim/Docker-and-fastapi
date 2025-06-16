from pydantic import BaseModel

class WishlistSchema(BaseModel):
    user_id: int
    product_id: int
    
    class Config:
        orm_mode = True
        
class WishlistItemResponse(BaseModel):
    id: int
    product_id: int
    created_at: str

    class Config:
        orm_mode = True