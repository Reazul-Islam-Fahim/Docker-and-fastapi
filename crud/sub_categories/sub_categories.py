from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from models.sub_categories.sub_categories import SubCategories
from schemas.sub_categories.sub_categories import SubCategoriesSchema
from models.product_features.product_features import ProductFeatures
from models.products.products import Products


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
    

async def get_sub_category_by_id(db: AsyncSession, id: int):
    try:
        result = await db.execute(select(SubCategories).where(SubCategories.id == id))
        db_sub_category = result.scalar_one_or_none()

        if not db_sub_category:
            raise HTTPException(status_code=404, detail="Sub category not found")

        return {
            "id": db_sub_category.id,
            "category_id": db_sub_category.category_id,
            "name": db_sub_category.name,
            "description": db_sub_category.description,
            "meta_title": db_sub_category.meta_title,
            "meta_description": db_sub_category.meta_description,
            "image": db_sub_category.image,
            "feature_ids": [f.id for f in db_sub_category.product_features],
            "is_active": db_sub_category.is_active
        }

    except Exception as e:
        print("DB Error:", e)
        raise HTTPException(status_code=500, detail="Sub category not found")



async def get_all_sub_categories(db: AsyncSession, skip: int = 0, limit: int = 10):
    try:
        result = await db.execute(
            select(SubCategories)
            .options(selectinload(SubCategories.product_features))
            .offset(skip)
            .limit(limit)
        )
        sub_categories = result.scalars().all()

        return [
            {
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
            for sc in sub_categories
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving sub categories: {str(e)}")


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
    sub_category_data: SubCategoriesSchema,
    file_path: Optional[str] = None
):
    try:
        result = await db.execute(select(SubCategories).where(SubCategories.id == id))
        db_sub_category = result.scalar_one_or_none()

        if not db_sub_category:
            raise HTTPException(status_code=404, detail="Sub Category not found")

        # Fetch related product features again
        feature_query = await db.execute(
            select(ProductFeatures).where(ProductFeatures.id.in_(sub_category_data.features_id))
        )
        product_features = feature_query.scalars().all()

        db_sub_category.name = sub_category_data.name
        db_sub_category.category_id = sub_category_data.category_id
        db_sub_category.description = sub_category_data.description
        db_sub_category.meta_title = sub_category_data.meta_title
        db_sub_category.meta_description = sub_category_data.meta_description
        db_sub_category.image = file_path
        db_sub_category.is_active = sub_category_data.is_active
        db_sub_category.product_features = product_features

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
