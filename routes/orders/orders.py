from fastapi import APIRouter, Body, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from database.db import get_db
from schemas.orders.orders import OrdersSchema
from schemas.order_items.order_items import OrderItemsSchema
from models.orders.orders import OrderStatus, DeliveryStatus
from crud.orders.orders import (
    create_order_with_items,
    get_order_with_items,
    update_order_status_fields,
    delete_order_with_items,
    get_orders_with_optional_filters,
)

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("")
async def create_order(
    order_data: OrdersSchema,
    items_data: List[OrderItemsSchema],
    db: AsyncSession = Depends(get_db),
):
    return await create_order_with_items(db, order_data, items_data)


@router.get("/orders")
async def get_orders_with_filtering(
    user_id: Optional[int] = Query(None),
    status: Optional[OrderStatus] = Query(None),
    delivery_status: Optional[DeliveryStatus] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1),
    db: AsyncSession = Depends(get_db)
):
    return await get_orders_with_optional_filters(
        db=db,
        user_id=user_id,
        status=status,
        delivery_status=delivery_status,
        page=page,
        limit=limit
    )

@router.get("/{order_id}")
async def read_order(order_id: int, db: AsyncSession = Depends(get_db)):
    return await get_order_with_items(db, order_id)


@router.put("/{order_id}/status")
async def update_order_status_endpoint(
    order_id: int,
    order_status: Optional[OrderStatus] = None,
    delivery_status: Optional[DeliveryStatus] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    db: AsyncSession = Depends(get_db)
):
    return await update_order_status_fields(db, order_id, order_status, delivery_status, page, limit)


@router.delete("/{order_id}")
async def delete_order(
    order_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await delete_order_with_items(db, order_id)
