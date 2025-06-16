from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from schemas.cart.cart import CartSchema
from crud.cart.cart import (
    create_cart,
    get_all_carts,
    get_cart_by_id,
    get_cart_by_user_id,
    delete_cart
)

router = APIRouter(
    prefix="/carts",tags=["Carts"])

@router.post("")
async def create_cart_route(cart: CartSchema, db: AsyncSession = Depends(get_db)):
    return await create_cart(db, cart)


@router.get("")
async def get_all_carts_route(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_all_carts(db, skip=skip, limit=limit)


@router.get("/{cart_id}")
async def get_cart_by_id_route(cart_id: int, db: AsyncSession = Depends(get_db)):
    cart = await get_cart_by_id(db, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


@router.get("/user/{user_id}")
async def get_cart_by_user_id_route(user_id: int, db: AsyncSession = Depends(get_db)):
    cart = await get_cart_by_user_id(db, user_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found for this user")
    return cart


@router.delete("/{cart_id}")
async def delete_cart_route(cart_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await delete_cart(db, cart_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cart not found")
    return deleted
