from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.cart.cart import Cart
from schemas.cart.cart import CartSchema


async def create_cart(db: AsyncSession, cart_data: CartSchema):
    db_cart = Cart(user_id=cart_data.user_id)
    db.add(db_cart)
    await db.commit()
    await db.refresh(db_cart)
    return db_cart


async def get_all_carts(db: AsyncSession, skip: int = 0, limit: int = 100):
    result = await db.execute(select(Cart).offset(skip).limit(limit))
    return result.scalars().all()


async def get_cart_by_id(db: AsyncSession, cart_id: int):
    result = await db.execute(select(Cart).where(Cart.id == cart_id))
    return result.scalar_one_or_none()


async def get_cart_by_user_id(db: AsyncSession, user_id: int):
    result = await db.execute(select(Cart).where(Cart.user_id == user_id))
    return result.scalar_one_or_none()


async def delete_cart(db: AsyncSession, cart_id: int):
    result = await db.execute(select(Cart).where(Cart.id == cart_id))
    db_cart = result.scalar_one_or_none()
    if not db_cart:
        return None
    await db.delete(db_cart)
    await db.commit()
    return db_cart
