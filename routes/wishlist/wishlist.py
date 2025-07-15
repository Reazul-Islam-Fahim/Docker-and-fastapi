from fastapi import APIRouter, Depends, HTTPException, Query, status, Form
from sqlalchemy.ext.asyncio import AsyncSession
from crud.wishlist.wishlist import get_wishlists_by_user_id, create_wishlist, delete_wishlist_item
from database.db import get_db
from schemas.wishlist.wishlist import WishlistSchema, WishlistItemResponse

router = APIRouter(prefix="/wishlist", tags=["Wishlist"])

# create wishlist 
@router.post("/", response_model=WishlistItemResponse)
async def add_to_wishlist(
    wishlist_data: WishlistSchema, 
    db: AsyncSession = Depends(get_db)
):
    return await create_wishlist(db, wishlist_data)

# Get all wishlist by userID 
@router.get("/{user_id}")
async def get_wishlist_by_user_id_data(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1),
):
    return await get_wishlists_by_user_id(db, user_id, page, limit)

# Delete the wishlist by wishlist ID
@router.delete("/{wishlist_id}")
async def delete_wishlist(wishlist_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_wishlist_item(wishlist_id, db)