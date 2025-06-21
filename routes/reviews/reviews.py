from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from database.db import get_db
from crud.reviews import reviews as review_crud
from schemas.reviews.reviews import ReviewsSchema
import os
import shutil

router = APIRouter(prefix="/reviews", tags=["Reviews"])

UPLOAD_DIR = "resources/reviews"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("")
async def create_review(
    rating: int = Form(None),
    comment: str = Form(None),
    user_id: int = Form(...),
    product_id: int = Form(...),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    image_url = None
    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image.")
        filename = f"user{user_id}_{image.filename.replace(' ', '_')}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/{UPLOAD_DIR}/{filename}"

    review_data = ReviewsSchema(
        rating=rating,
        comment=comment,
        user_id=user_id,
        product_id=product_id,
        is_active=is_active
    )
    return await review_crud.create_review(db, review_data, image_url)


@router.get("/{review_id}")
async def get_review(review_id: int, db: AsyncSession = Depends(get_db)):
    review = await review_crud.get_review_by_id(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review

@router.get("/product/{product_id}")
async def get_reviews_by_product_id(
    product_id: int,
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    reviews = await review_crud.get_reviews_by_product_id(db, product_id, skip=skip, limit=limit)
    if not reviews:
        raise HTTPException(status_code=404, detail="No reviews found for this product")
    return reviews


@router.get("")
async def list_reviews(skip: int = Query(0), limit: int = Query(10), db: AsyncSession = Depends(get_db)):
    return await review_crud.get_all_reviews(db, skip, limit)


@router.put("/{review_id}")
async def update_review(
    review_id: int,
    rating: int = Form(None),
    comment: str = Form(None),
    user_id: int = Form(None),
    product_id: int = Form(None),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    image_url = None
    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image.")
        filename = f"user{user_id}_{image.filename.replace(' ', '_')}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/{UPLOAD_DIR}/{filename}"

    review_data = ReviewsSchema(
        rating=rating,
        comment=comment,
        user_id=user_id,
        product_id=product_id,
        is_active=is_active
    )
    return await review_crud.update_review(db, review_id, review_data, image_url)


