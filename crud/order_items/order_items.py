from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models import *
from schemas.order_items.order_items import OrderItemsSchema
from fastapi import HTTPException, status


async def create_order_item(db: AsyncSession, order_item_data: OrderItemsSchema):
    try:
        result = await db.execute(
            select(Products).where(Products.id == order_item_data.product_id)
        )
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {order_item_data.product_id} not found"
            )

        cost = order_item_data.quantity * product.payable_price

        new_order_item = OrderItems(
            order_id=order_item_data.order_id,
            product_id=order_item_data.product_id,
            quantity=order_item_data.quantity,  
            cost=cost
        )

        db.add(new_order_item)
        await db.commit()
        await db.refresh(new_order_item)

        return new_order_item

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
        
async def get_order_items(db: AsyncSession, order_id: int):
    try:
        result = await db.execute(
            select(OrderItems).where(OrderItems.order_id == order_id)
        )
        order_items = result.scalars().all()

        if not order_items:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No order items found for order ID {order_id}"
            )

        return order_items

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
        
