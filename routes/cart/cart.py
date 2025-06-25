from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from schemas.cart.cart import CartSchema
from crud.cart.cart import (
    create_cart_with_items,
    get_cart_with_items_by_id,
    get_cart_with_items_by_user_id,
    get_all_carts_with_items,
    delete_cart_with_items,
    update_cart_with_items
)

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.post("")
async def create_cart(
    cart_data: CartSchema,
    db: AsyncSession = Depends(get_db)
):
    return await create_cart_with_items(db, cart_data)


@router.get("/{cart_id}")
async def get_cart_by_id(
    cart_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await get_cart_with_items_by_id(db, cart_id)


@router.get("/user/{user_id}")
async def get_cart_by_user_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await get_cart_with_items_by_user_id(db, user_id)


@router.get("")
async def list_carts(
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    return await get_all_carts_with_items(db, page, limit)


@router.put("/{cart_id}")
async def update_cart(
    cart_id: int,
    cart_data: CartSchema,
    db: AsyncSession = Depends(get_db)
):
    return await update_cart_with_items(db, cart_id, cart_data)


@router.delete("/{cart_id}")
async def delete_cart(
    cart_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await delete_cart_with_items(db, cart_id)


