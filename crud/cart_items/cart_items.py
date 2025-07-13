from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from schemas.cart_items.cart_items import CartItemsSchema
from models import *


async def create_cart_item(db: AsyncSession, cart_item: CartItemsSchema):
    result = await db.execute(
        select(Products).where(Products.id == cart_item.product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise ValueError(f"Product with ID {cart_item.product_id} not found")

    payable_price = product.payable_price
    quantity = cart_item.quantity or 1
    cost = payable_price * quantity

    db_cart_item = CartItems(
        product_id=cart_item.product_id,
        cart_id=cart_item.cart_id,
        quantity=quantity,
        cost=cost
    )

    db.add(db_cart_item)
    await db.commit()
    await db.refresh(db_cart_item)
    return db_cart_item


async def get_cart_items(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(CartItems).offset(skip).limit(limit))
    return result.scalars().all()


async def get_cart_item_by_id(db: AsyncSession, cart_item_id: int):
    result = await db.execute(select(CartItems).where(CartItems.id == cart_item_id))
    return result.scalar_one_or_none()


async def get_cart_items_by_cart_id(db: AsyncSession, cart_id: int):
    result = await db.execute(select(CartItems).where(CartItems.cart_id == cart_id))
    return result.scalars().all()


async def update_cart_item(db: AsyncSession, cart_item_id: int, cart_item_update: CartItemsSchema):
    result = await db.execute(select(CartItems).where(CartItems.id == cart_item_id))
    db_cart_item = result.scalar_one_or_none()
    if not db_cart_item:
        return None

    product_result = await db.execute(
        select(Products).where(Products.id == db_cart_item.product_id)
    )
    product = product_result.scalar_one_or_none()

    if not product:
        raise ValueError(f"Product with ID {db_cart_item.product_id} not found")

    quantity = cart_item_update.quantity or 1
    db_cart_item.quantity = quantity
    db_cart_item.cost = product.payable_price * quantity

    await db.commit()
    await db.refresh(db_cart_item)
    return db_cart_item


async def delete_cart_item(db: AsyncSession, cart_item_id: int):
    result = await db.execute(select(CartItems).where(CartItems.id == cart_item_id))
    db_cart_item = result.scalar_one_or_none()
    if not db_cart_item:
        return None

    await db.delete(db_cart_item)
    await db.commit()
    return db_cart_item
