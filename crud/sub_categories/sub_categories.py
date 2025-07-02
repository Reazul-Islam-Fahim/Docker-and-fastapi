from typing import Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from models.products.products import Products
from models.sub_categories.sub_categories import SubCategories
from schemas.sub_categories.sub_categories import SubCategoriesSchema
from models.product_features.product_features import ProductFeatures
from sqlalchemy.orm import joinedload


async def get_sub_category_by_id(db: AsyncSession, id: int):
    try:
        result = await db.execute(
            select(SubCategories)
            .options(selectinload(SubCategories.product_features))
            .where(SubCategories.id == id)
        )
        sc = result.scalar_one_or_none()
        if not sc:
            raise HTTPException(status_code=404, detail="Sub category not found")

        return {
            "id": sc.id,
            "category_id": sc.category_id,
            "name": sc.name,
            "description": sc.description,
            "meta_title": sc.meta_title,
            "meta_description": sc.meta_description,
            "image": sc.image,
            "feature_ids": [f.id for f in sc.product_features],
            "is_active": sc.is_active
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")


# Get all sub-categories with pagination and filtering 
async def get_all_sub_categories(
    db: AsyncSession,
    page: int,
    limit: int,
    is_active: Optional[bool] = None
):
    try:
        page = max(page, 1)
        limit = max(limit, 1)
        offset = (page - 1) * limit

        base_query = select(SubCategories).options(selectinload(SubCategories.product_features))

        if is_active is not None:
            base_query = base_query.where(SubCategories.is_active == is_active)

        # Get total count
        total_result = await db.execute(select(func.count()).select_from(base_query.subquery()))
        total = total_result.scalar()

        # Get paginated results
        result = await db.execute(base_query.offset(offset).limit(limit))
        sub_categories = result.scalars().all()

        # Return in data + meta format
        return {
            "data": [
                {
                    "id": sc.id,
                    "category_id": sc.category_id,
                    "name": sc.name,
                    "description": sc.description,
                    "meta_title": sc.meta_title,
                    "meta_description": sc.meta_description,
                    "image": sc.image,
                    "feature_ids": [f.id for f in sc.product_features],
                    "is_active": sc.is_active,
                    "created_at": sc.created_at
                }
                for sc in sub_categories
            ],
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sub categories: {str(e)}")
    

#Get Products by sub-category ID
async def get_products_by_sub_category_id(db: AsyncSession, sub_category_id: int, page: int, limit: int):
    try:
        total_query = await db.execute(
            select(func.count(Products.id))
            .join(SubCategories)
            .where(SubCategories.id == sub_category_id)
        )
        total = total_query.scalar_one()

        result = await db.execute(
            select(Products)
            .join(SubCategories)
            .where(SubCategories.id == sub_category_id)
            .options(joinedload(Products.sub_categories))
            .offset((page - 1) * limit)
            .limit(limit)
        )
        products = result.scalars().all()

        return {
            "data": [
                {
                    "id": p.id,
                    "name": p.name,
                    "description": p.description,
                    "meta_title": p.meta_title,
                    "meta_description": p.meta_description,
                    "brand_id": p.brand_id,
                    "vendor_id": p.vendor_id,
                    "price": p.price,
                    "payable_price": p.payable_price,
                    "available_stock": p.available_stock,
                    "discount_type": p.discount_type,
                    "discount_amount": p.discount_amount,
                    "images": p.images,
                    "highlighted_image": p.highlighted_image,
                    "is_active": p.is_active,
                    "created_at": p.created_at,
                    "subcategory_id": p.sub_category_id
                }
                for p in products
            ],
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")


async def create_sub_category(
    db: AsyncSession,
    sub_category_data: SubCategoriesSchema,
    file_path: Optional[str] = None
):
    try:
        existing_check = await db.execute(
            select(SubCategories).where(SubCategories.name == sub_category_data.name)
        )
        if existing_check.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Sub category already exists")

        feature_query = await db.execute(
            select(ProductFeatures).where(ProductFeatures.id.in_(sub_category_data.features_id))
        )
        product_features = feature_query.scalars().all()

        new_sub_category = SubCategories(
            name=sub_category_data.name,
            category_id=sub_category_data.category_id,
            description=sub_category_data.description,
            meta_title=sub_category_data.meta_title,
            meta_description=sub_category_data.meta_description,
            image=file_path,
            is_active=sub_category_data.is_active,
            product_features=product_features
        )

        db.add(new_sub_category)
        await db.commit()
        await db.refresh(new_sub_category)
        return {
            "id": new_sub_category.id,
            "name": new_sub_category.name,
            "category_id": new_sub_category.category_id,
            "description": new_sub_category.description,
            "meta_title": new_sub_category.meta_title,
            "meta_description": new_sub_category.meta_description,
            "image": new_sub_category.image,
            "feature_ids": [f.id for f in new_sub_category.product_features],
            "is_active": new_sub_category.is_active
        }

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def update_sub_category(
    db: AsyncSession,
    id: int,
    update_data: dict,
    file_path: Optional[str] = None
):
    try:
        result = await db.execute(select(SubCategories).where(SubCategories.id == id))
        db_sub_category = result.scalar_one_or_none()

        if not db_sub_category:
            raise HTTPException(status_code=404, detail="Sub Category not found")

        # Update scalar fields dynamically
        for field, value in update_data.items():
            if field != "features_id":  # Handle separately
                setattr(db_sub_category, field, value)

        # Handle feature relationships
        if "features_id" in update_data:
            feature_query = await db.execute(
                select(ProductFeatures).where(ProductFeatures.id.in_(update_data["features_id"]))
            )
            db_sub_category.product_features = feature_query.scalars().all()

        # Update image if provided
        if file_path:
            db_sub_category.image = file_path

        await db.commit()
        await db.refresh(db_sub_category)

        return {
            "id": db_sub_category.id,
            "name": db_sub_category.name,
            "category_id": db_sub_category.category_id,
            "description": db_sub_category.description,
            "meta_title": db_sub_category.meta_title,
            "meta_description": db_sub_category.meta_description,
            "image": db_sub_category.image,
            "feature_ids": [f.id for f in db_sub_category.product_features],
            "is_active": db_sub_category.is_active
        }

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

