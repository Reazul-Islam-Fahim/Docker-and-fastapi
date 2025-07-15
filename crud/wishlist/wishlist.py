from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from models.wishlist.wishlist import Wishlist
from schemas.wishlist.wishlist import WishlistSchema
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

#Create Wishlist
async def create_wishlist(
    db: AsyncSession, 
    wishlist_data: WishlistSchema,
):
    try:
        new_item = Wishlist(
            user_id=wishlist_data.user_id,
            product_id=wishlist_data.product_id
        )
        db.add(new_item)
        await db.commit()
        await db.refresh(new_item)
        return new_item

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


# Get All wishlist by userIDD
async def get_wishlists_by_user_id(
    db: AsyncSession,
    user_id: int,
    page: int = 1,
    limit: int = 30
):
    try:
        offset = (page - 1) * limit

        base_query = (
            select(Wishlist)
            .options(joinedload(Wishlist.products))
            .where(Wishlist.user_id == user_id)
        )

        # Total count for meta
        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar_one()

        # Paginated results
        result = await db.execute(base_query.offset(offset).limit(limit))
        wishlists = result.scalars().all()

        data = [
            {
                "id": item.id,
                "product_id": item.product_id,
                "name": item.products.name if item.products else None,
                "price": item.products.payable_price if item.products else None,
                "image": item.products.highlighted_image if item.products else None,
                "created_at": item.created_at,
            }
            for item in wishlists
        ]

        return {
            "data": data,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit,
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving wishlist: {str(e)}")

    
# Delete the wishlist by ID
async def delete_wishlist_item(wishlist_id: int, db: AsyncSession):
    try:
        result = await db.execute(
            select(Wishlist).where(Wishlist.id == wishlist_id)
        )
        wishlist_item = result.scalar_one_or_none()

        if not wishlist_item:
            raise HTTPException(status_code=404, detail="Wishlist item not found")

        await db.delete(wishlist_item)
        await db.commit()

        return {"message": "Wishlist item deleted successfully"}

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database error during deletion: {str(e)}"
        )
