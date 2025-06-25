from pydantic import BaseModel
from models.orders.orders import OrderStatus, DeliveryStatus

class OrdersSchema(BaseModel)  :
    user_id: int
    user_addresses_id: int
    delivery_charge: int
    status: OrderStatus = OrderStatus.PENDING
    delivery_status: DeliveryStatus = DeliveryStatus.PENDING
    is_paid: bool = False
    
    class Config:
        orm_mode = True 