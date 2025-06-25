from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy import delete, func
from models.cart.cart import Cart
from models.cart_items.cart_items import CartItems
from models.products.products import Products  
from schemas.cart.cart import CartSchema



async def create_cart_with_items(
    db: AsyncSession,
    cart_data: CartSchema
):
    try:
        db_cart = Cart(user_id=cart_data.user_id)
        db.add(db_cart)
        await db.flush()  

        created_items = []

        for item in cart_data.cart_items or []:
            result = await db.execute(select(Products).where(Products.id == item.product_id))
            product = result.scalar_one_or_none()

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with ID {item.product_id} not found"
                )

            cart_item = CartItems(
                cart_id=db_cart.id,
                product_id=item.product_id,
                quantity=item.quantity or 1,
                cost=item.cost or 0
            )
            db.add(cart_item)
            created_items.append(cart_item)

        await db.commit()
        await db.refresh(db_cart)

        return {
            "cart": db_cart,
            "cart_items": created_items
        }

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create cart: {str(e)}"
        )




async def get_cart_with_items_by_id(db: AsyncSession, cart_id: int):
    try:
        result = await db.execute(
            select(Cart)
            .options(selectinload(Cart.cart_items))
            .where(Cart.id == cart_id)
        )
        cart = result.scalar_one_or_none()

        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        return {
            "cart": cart,
            "cart_items": cart.cart_items
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching cart: {str(e)}"
        )




async def get_cart_with_items_by_user_id(db: AsyncSession, user_id: int):
    try:
        result = await db.execute(
            select(Cart)
            .options(selectinload(Cart.cart_items))
            .where(Cart.user_id == user_id)
        )
        cart = result.scalar_one_or_none()

        if not cart:
            raise HTTPException(status_code=404, detail="Cart for user not found")

        return {
            "cart": cart,
            "cart_items": cart.cart_items
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching cart: {str(e)}"
        )




async def get_all_carts_with_items(db: AsyncSession, page: int = 1, limit: int = 10):
    try:
        offset = (page - 1) * limit
        query = select(Cart).options(selectinload(Cart.cart_items))

        total_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar()

        result = await db.execute(query.offset(offset).limit(limit))
        carts = result.scalars().all()

        return {
            "data": [
                {
                    "cart": cart,
                    "cart_items": cart.cart_items
                } for cart in carts
            ],
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
            detail=f"Error fetching carts: {str(e)}"
        )




async def delete_cart_with_items(db: AsyncSession, cart_id: int):
    try:
        result = await db.execute(select(Cart).where(Cart.id == cart_id))
        cart = result.scalar_one_or_none()

        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        await db.delete(cart) 
        await db.commit()

        return {"message": "Cart and items deleted successfully"}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting cart: {str(e)}"
        )




async def update_cart_with_items(
    db: AsyncSession,
    cart_id: int,
    updated_cart_data: CartSchema
):
    try:
        result = await db.execute(select(Cart).where(Cart.id == cart_id))
        db_cart = result.scalar_one_or_none()

        if not db_cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        db_cart.user_id = updated_cart_data.user_id 

        await db.execute(
            delete(CartItems).where(CartItems.cart_id == cart_id)
        )
        new_items = []
        for item_data in updated_cart_data.cart_items or []:
            result = await db.execute(select(Products).where(Products.id == item_data.product_id))
            product = result.scalar_one_or_none()

            if not product:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product with ID {item_data.product_id} not found"
                )

            cart_item = CartItems(
                cart_id=cart_id,
                product_id=item_data.product_id,
                quantity=item_data.quantity or 1,
                cost=item_data.cost or 0
            )
            db.add(cart_item)
            new_items.append(cart_item)

        await db.commit()
        await db.refresh(db_cart)

        return {
            "cart": db_cart,
            "cart_items": new_items
        }

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update cart: {str(e)}"
        )
