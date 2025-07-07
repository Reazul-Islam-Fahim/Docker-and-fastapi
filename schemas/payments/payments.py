from pydantic import BaseModel
from typing import Optional

class PaymentsSchema(BaseModel):
    user_id: int
    order_id: Optional[int] = None
    payment_method_id: int
    amount: int

    class Config:
        orm_mode = True