from fastapi import APIRouter, Depends, HTTPException, Query, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from crud.wishlist.wishlist import get_wishlists_by_user_id, create_wishlist, delete_wishlist_item
from database.db import get_db
from schemas.wishlist.wishlist import WishlistSchema, WishlistItemResponse

router = APIRouter(prefix="/wishlist", tags=["wishlist"])

@router.post("/", response_model=WishlistItemResponse)
async def add_to_wishlist(
    wishlist_data: WishlistSchema, 
    db: AsyncSession = Depends(get_db)
):
    return await create_wishlist(db, wishlist_data)

@router.get("/{user_id}")
async def get_wishlist_by_user_id_data(user_id: int, db: AsyncSession = Depends(get_db)):
    wishlists_by_user = await get_wishlists_by_user_id(db, user_id)
    if not wishlists_by_user:
        raise HTTPException(status_code=404, detail="Wishlist not found")
    return {"data": wishlists_by_user}

@router.delete("/{wishlist_id}")
async def delete_wishlist(wishlist_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_wishlist_item(wishlist_id, db)