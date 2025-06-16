from pydantic import BaseModel

class CartSchema(BaseModel):
    user_id : int
    
    class Config:
        orm_mode = True