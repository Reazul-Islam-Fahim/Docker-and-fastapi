from http.client import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.reviews.reviews import Reviews
from schemas.reviews.reviews import ReviewsSchema


async def create_review(db: AsyncSession, review_data: ReviewsSchema, image_url: str):
    comment_content = {
        "comment": review_data.comment,
        "image": image_url
    }
    
    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")


    new_review = Reviews(
        rating=review_data.rating,
        content=comment_content,
        is_active=review_data.is_active,
        user_id=review_data.user_id,
        product_id=review_data.product_id
    )
    db.add(new_review)
    await db.commit()
    await db.refresh(new_review)
    return new_review


async def get_review_by_id(db: AsyncSession, review_id: int):
    result = await db.execute(select(Reviews).where(Reviews.id == review_id))
    return result.scalar_one_or_none()

async def get_reviews_by_product_id(db: AsyncSession, product_id: int, skip: int = 0, limit: int = 10):
    result = await db.execute(
        select(Reviews).where(Reviews.product_id == product_id).offset(skip).limit(limit)
    )
    return result.scalars().all()


async def get_all_reviews(db: AsyncSession, skip: int = 0, limit: int = 10):
    result = await db.execute(select(Reviews).offset(skip).limit(limit))
    return result.scalars().all()


async def update_review(db: AsyncSession, review_id: int, review_data: ReviewsSchema, image_url: str):
    existing_review = await db.get(Reviews, review_id)

    if not existing_review:
        raise HTTPException(status_code=404, detail="Review not found")

    if review_data.rating < 1 or review_data.rating > 5:
        raise HTTPException(status_code=400, detail="Rating must be between 1 and 5.")

    existing_review.rating = review_data.rating
    existing_review.content = {
        "comment": review_data.comment,
        "image": image_url
    }
    existing_review.is_active = review_data.is_active

    await db.commit()
    await db.refresh(existing_review)

    return existing_review



