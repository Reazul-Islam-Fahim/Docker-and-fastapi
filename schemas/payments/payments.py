from pydantic import BaseModel

class PaymentsSchema(BaseModel):
    user_id: int
    order_id: int
    payment_method_id: int
    amount: int

    class Config:
        orm_mode = True
