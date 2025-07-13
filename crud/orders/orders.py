from typing import Optional
from sqlalchemy.orm import selectinload
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models.notifications.notifications import NotificationType
from models import *
from schemas.orders.orders import OrdersSchema
from schemas.order_items.order_items import OrderItemsSchema
from crud.notifications.notifications import create_notification
from schemas.notifications.notifications import NotificationsSchema
from utils.serializers.serialize_order import serialize_order_item, serialize_order

async def create_order_with_items(
    db: AsyncSession,
    order_data: OrdersSchema,
    items_data: list[OrderItemsSchema],
    socket_manager=None
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
        vendor_user_ids = set()

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

            if product.vendor_id:
                vendor_result = await db.execute(
                    select(Vendors.user_id).where(Vendors.id == product.vendor_id)
                )
                vendor_user_id = vendor_result.scalar_one_or_none()
                if vendor_user_id:
                    vendor_user_ids.add(vendor_user_id)

        db_order.total_amount = total_amount + db_order.delivery_charge

        await db.commit()
        await db.refresh(db_order)

        customer_notification = NotificationsSchema(
            user_id=db_order.user_id,
            message=f"Your order #{db_order.id} has been successfully placed.",
            type=NotificationType.PUSH,
            is_read=False
        )
        await create_notification(db=db, notification=customer_notification, socket_manager=socket_manager)

        for vendor_user_id in vendor_user_ids:
            vendor_notification = NotificationsSchema(
                user_id=vendor_user_id,
                message=f"One or more of your products were included in Order #{db_order.id}.",
                type=NotificationType.PUSH,
                is_read=False
            )
            await create_notification(db=db, notification=vendor_notification, socket_manager=socket_manager)

        return {
            "message": "Order created successfully",
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
            select(OrderItems)
            .where(OrderItems.order_id == order.id)
            .options(selectinload(OrderItems.products))  
        )
        order_items = item_result.scalars().all()

        return {
            "order": serialize_order(order),
            "order_items": [serialize_order_item(item) for item in order_items]
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching order with items: {str(e)}"
        )

async def update_order_status_fields(
    db: AsyncSession,
    order_id: int,
    status: Optional[str] = None,
    delivery_status: Optional[str] = None,
    page: int = 1,
    limit: int = 10,
    socket_manager=None
):
    try:
        page = max(page, 1)
        limit = max(limit, 1)
        offset = (page - 1) * limit

        result = await db.execute(
            select(Orders).where(Orders.id == order_id)
        )
        db_order = result.scalar_one_or_none()

        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")

        if status is not None:
            db_order.status = status
            db_order.is_paid = False if status == "pending" else True  
            
        if delivery_status is not None:
            db_order.delivery_status = delivery_status

        await db.commit()
        await db.refresh(db_order)

        notification = NotificationsSchema(
            user_id=db_order.user_id,
            message=f"Your order #{db_order.id} status has been updated to "
                    f"'{db_order.status}' with delivery status '{db_order.delivery_status}'.",
            type=NotificationType.PUSH,
            is_read=False
        )
        await create_notification(db=db, notification=notification, socket_manager=socket_manager)

        count_query = select(func.count()).select_from(
            select(OrderItems).where(OrderItems.order_id == order_id).subquery()
        )
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        items_result = await db.execute(
            select(OrderItems)
            .where(OrderItems.order_id == order_id)
            .options(selectinload(OrderItems.products)) 
            .offset(offset)
            .limit(limit)
        )
        order_items = items_result.scalars().all()

        return {
            "order": serialize_order(db_order),
            "order_items": [serialize_order_item(item) for item in order_items],
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

        base_query = (
            select(Orders)
            .options(
                selectinload(Orders.order_items)
                .selectinload(OrderItems.products)
            )
        )

        if filters:
            base_query = base_query.where(and_(*filters))

        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        result = await db.execute(
            base_query.offset(offset).limit(limit)
        )
        orders = result.scalars().all()

        response_data = []
        for order in orders:
            response_data.append({
                "order": serialize_order(order),
                "order_items": [serialize_order_item(item) for item in order.order_items]
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