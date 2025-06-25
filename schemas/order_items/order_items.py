from pydantic import BaseModel

class OrderItemsSchema(BaseModel):
    product_id: int
    quantity: int
    
    class Config:
        orm_mode = True 