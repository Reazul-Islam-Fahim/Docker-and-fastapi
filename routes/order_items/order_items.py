from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from schemas.order_items.order_items import OrderItemsSchema
from crud.order_items import order_items as order_items_crud
from typing import List

router = APIRouter(
    prefix="/order-items",
    tags=["Order Items"]
)

@router.post("", response_model=dict)
async def create_order_item(
    order_item_data: OrderItemsSchema,
    db: AsyncSession = Depends(get_db)
):
    order_item = await order_items_crud.create_order_item(db, order_item_data)
    return {"detail": "Order item created successfully", "data": order_item}


@router.get("/{order_id}")
async def get_order_items(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    order_items = await order_items_crud.get_order_items(db, order_id)
    return order_items