from pydantic import BaseModel

class PaymentMethodSchema(BaseModel):
    name: str
    is_active: bool = True

    class Config:
        orm_mode = True