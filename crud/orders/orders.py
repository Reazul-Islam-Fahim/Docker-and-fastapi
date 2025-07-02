from typing import Optional
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, func
from models.orders.orders import Orders
from models.order_items.order_items import OrderItems
from models.products.products import Products
from schemas.orders.orders import OrdersSchema
from schemas.order_items.order_items import OrderItemsSchema
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError


async def create_order_with_items(
    db: AsyncSession, 
    order_data: OrdersSchema, 
    items_data: list[OrderItemsSchema]
):
    try:
        db_order = Orders(
            user_id=order_data.user_id,
            shipping_address_id=order_data.user_addresses_id,
            total_amount=0, 
            delivery_charge=order_data.delivery_charge,
            status=order_data.status,
            delivery_status=order_data.delivery_status,
            is_paid=order_data.is_paid
        )
        db.add(db_order)
        await db.flush()  

        total_amount = 0
        created_items = []

        for item_data in items_data:
            result = await db.execute(
                select(Products).where(Products.id == item_data.product_id)
            )
            product = result.scalar_one_or_none()

            if not product:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Product with ID {item_data.product_id} not found"
                )

            cost = item_data.quantity * product.payable_price
            total_amount += cost

            order_item = OrderItems(
                order_id=db_order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                cost=cost
            )
            db.add(order_item)
            created_items.append(order_item)

        db_order.total_amount = total_amount + db_order.delivery_charge

        await db.commit()
        await db.refresh(db_order)

        return {
            "order": db_order,
            "order_items": created_items
        }

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create order: {str(e)}"
        )


async def get_order_with_items(db: AsyncSession, order_id: int):
    try:
        result = await db.execute(
            select(Orders).where(Orders.id == order_id)
        )
        order = result.scalar_one_or_none()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        item_result = await db.execute(
            select(OrderItems).where(OrderItems.order_id == order.id)
        )
        order_items = item_result.scalars().all()

        return {
            "order": order,
            "order_items": order_items
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching order with items: {str(e)}"
        )


async def update_order_status_fields(
    db: AsyncSession,
    order_id: int,
    status: str,
    delivery_status: str,
    page: int = 1,
    limit: int = 10
):
    try:
        page = max(page, 1)
        limit = max(limit, 1)
        offset = (page - 1) * limit

        result = await db.execute(select(Orders).where(Orders.id == order_id))
        db_order = result.scalar_one_or_none()

        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")

        db_order.status = status
        db_order.delivery_status = delivery_status
        db_order.is_paid = False if status == "pending" else True

        await db.commit()
        await db.refresh(db_order)

        count_query = select(func.count()).select_from(
            select(OrderItems).where(OrderItems.order_id == order_id).subquery()
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        items_result = await db.execute(
            select(OrderItems)
            .where(OrderItems.order_id == order_id)
            .offset(offset)
            .limit(limit)
        )
        order_items = items_result.scalars().all()

        return {
            "order": {
                "id": db_order.id,
                "total_amount": db_order.total_amount,
                "is_paid": db_order.is_paid,
                "status": db_order.status,
                "delivery_status": db_order.delivery_status,
                "delivery_charge": db_order.delivery_charge,
                "placed_at": db_order.placed_at,
                "user_id": db_order.user_id,
                "shipping_address_id": db_order.shipping_address_id,
            },
            "order_items": [
                {
                    "id": item.id,
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.price,
                }
                for item in order_items
            ],
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error updating order status: {str(e)}"
        )


async def delete_order_with_items(db: AsyncSession, order_id: int):
    try:
        result = await db.execute(select(Orders).where(Orders.id == order_id))
        order = result.scalar_one_or_none()

        if not order:
            raise HTTPException(status_code=404, detail="Order not found")

        if order.status != "pending":
            raise HTTPException(
                status_code=400,
                detail="Only pending orders can be deleted"
            )

        await db.execute(
            OrderItems.__table__.delete().where(OrderItems.order_id == order_id)
        )

        await db.delete(order)
        await db.commit()

        return {"message": "Order and associated items deleted successfully"}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting order: {str(e)}"
        ) 
        
    
async def get_orders_with_optional_filters(
    db: AsyncSession,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    delivery_status: Optional[str] = None,
    page: int = 1,
    limit: int = 30
):
    try:
        offset = (page - 1) * limit
        filters = []

        if user_id is not None:
            filters.append(Orders.user_id == user_id)
        if status is not None:
            filters.append(Orders.status == status)
        if delivery_status is not None:
            filters.append(Orders.delivery_status == delivery_status)

        # Base query with filters
        base_query = select(Orders).options(selectinload(Orders.order_items))
        if filters:
            base_query = base_query.where(and_(*filters))

        # Total count query
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        # Paginated query
        result = await db.execute(
            base_query.offset(offset).limit(limit)
        )
        orders = result.scalars().all()

        response_data = []
        for order in orders:
            response_data.append({
                "order": {
                    "id": order.id,
                    "total_amount": order.total_amount,
                    "is_paid": order.is_paid,
                    "status": order.status,
                    "delivery_status": order.delivery_status,
                    "delivery_charge": order.delivery_charge,
                    "placed_at": order.placed_at,
                    "user_id": order.user_id,
                    "shipping_address_id": order.shipping_address_id,
                },
                "order_items": [
                    {
                        "id": item.id,
                        "product_id": item.product_id,
                        "quantity": item.quantity
                    }
                    for item in order.order_items
                ]
            })

        return {
            "data": response_data,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching orders: {str(e)}"
        )