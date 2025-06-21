from pydantic import BaseModel

class UserAddressesSchema(BaseModel):
    user_id: int
    address_line: str
    city: str
    state: str
    postal_code: str
    country: str
    is_default: bool = False
    
    class Config:
        orm_mode = True
