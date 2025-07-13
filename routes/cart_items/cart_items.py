from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.cart_items.cart_items import CartItemsSchema
from database.db import get_db
from crud.cart_items.cart_items import (
    create_cart_item,
    get_cart_items,
    get_cart_item_by_id,
    update_cart_item,
    delete_cart_item,
    get_cart_items_by_cart_id
)

router = APIRouter(
    prefix="/cart-items",tags=["Cart Items"])

@router.post("")
async def create_cart_items(cart_item: CartItemsSchema, db: AsyncSession = Depends(get_db)):
    try:
        return await create_cart_item(db, cart_item)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("")
async def read_cart_items(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_cart_items(db, skip=skip, limit=limit)

@router.get("/{cart_item_id}")
async def read_cart_item(cart_item_id: int, db: AsyncSession = Depends(get_db)):
    cart_item = await get_cart_item_by_id(db, cart_item_id)
    if not cart_item:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return cart_item

@router.get("/cart/{cart_id}")
async def get_cart_items_by_cart_id_route(cart_id: int, db: AsyncSession = Depends(get_db)):
    items = await get_cart_items_by_cart_id(db, cart_id)
    return items

@router.put("/{cart_item_id}")
async def update_cart_item_by_id(cart_item_id: int, cart_item: CartItemsSchema, db: AsyncSession = Depends(get_db)):
    try:
        updated = await update_cart_item(db, cart_item_id, cart_item)
        if not updated:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return updated
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{cart_item_id}")
async def delete_cart_item_by_id(cart_item_id: int, db: AsyncSession = Depends(get_db)):
    deleted = await delete_cart_item(db, cart_item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return deleted
