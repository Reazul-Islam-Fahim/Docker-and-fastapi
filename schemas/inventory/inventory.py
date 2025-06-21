from pydantic import BaseModel, Field
from typing import Optional
from models.inventory.inventory import InventoryTypeEnum

    
class InventorySchema(BaseModel):
    unit_price: float
    total_quantity: int
    total_price: Optional[float] = 0
    inventory_type: InventoryTypeEnum
    invoice_number: str
    notes: Optional[str] = Field(None, max_length=511)
    product_id: int
    vendor_id: int