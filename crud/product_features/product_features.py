import math
from typing import Optional
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from models.product_features.product_features import ProductFeatures
from schemas.product_features.product_features import ProductFeaturesSchema
from sqlalchemy.orm import selectinload


async def get_product_feature_by_id(db: AsyncSession, id: int):
    try:
        result = await db.execute(select(ProductFeatures).where(ProductFeatures.id == id))
        db_feature = result.scalar_one_or_none()

        if not db_feature:
            raise HTTPException(status_code=404, detail="Product feature not found.")

        return db_feature

    except HTTPException:
        raise  
    except Exception as e:
        print("DB Error (Get by ID):", repr(e))
        raise HTTPException(status_code=500, detail="Error retrieving product feature.")


async def get_all_product_features(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    id: Optional[int] = None,
    name: Optional[str] = None,
    unit: Optional[str] = None,
    value: Optional[str] = None,
    is_active: Optional[bool] = None,
    sub_category_id: Optional[int] = None
):
    try:
        filters = []

        if id is not None:
            filters.append(ProductFeatures.id == id)
        if name is not None:
            filters.append(ProductFeatures.name.ilike(f"%{name}%"))
        if unit is not None:
            filters.append(ProductFeatures.unit.ilike(f"%{unit}%"))
        if value is not None:
            filters.append(ProductFeatures.value == value)
        if is_active is not None:
            filters.append(ProductFeatures.is_active == is_active)
        if sub_category_id is not None:
            filters.append(ProductFeatures.sub_categories.any(id=sub_category_id))

        base_query = select(ProductFeatures).options(selectinload(ProductFeatures.sub_categories))
        if filters:
            base_query = base_query.where(and_(*filters))

        # Count total
        count_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        offset = (page - 1) * limit
        result = await db.execute(base_query.offset(offset).limit(limit))
        features = result.scalars().all()

        data = []
        for f in features:
            data.append({
                "id": f.id,
                "name": f.name,
                "unit": f.unit,
                "value": f.value,
                "is_active": f.is_active,
                "sub_categories": [{"id": sc.id, "name": sc.name} for sc in f.sub_categories]
            })

        return {
            "data": data,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": math.ceil(total / limit) if limit else 1
            }
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


async def create_product_feature(db: AsyncSession, feature: ProductFeaturesSchema):
    try:
        new_feature = ProductFeatures(
            name=feature.name,
            unit=feature.unit,
            value=feature.value,
            is_active=feature.is_active
        )
        db.add(new_feature)
        await db.commit()
        await db.refresh(new_feature)

        return new_feature

    except SQLAlchemyError as e:
        await db.rollback()
        print("DB Error (Create):", repr(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during creation: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        print("Unexpected Error (Create):", repr(e))
        raise HTTPException(status_code=500, detail="Unexpected error while creating product feature.")


async def update_product_feature(db: AsyncSession, id: int, feature: ProductFeaturesSchema):
    try:
        result = await db.execute(select(ProductFeatures).where(ProductFeatures.id == id))
        db_feature = result.scalar_one_or_none()

        if not db_feature:
            raise HTTPException(status_code=404, detail="Product feature not found.")

        db_feature.name = feature.name
        db_feature.unit = feature.unit
        db_feature.value = feature.value
        db_feature.is_active = feature.is_active

        await db.commit()
        await db.refresh(db_feature)

        return db_feature

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        print("DB Error (Update):", repr(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error during update: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        print("Unexpected Error (Update):", repr(e))
        raise HTTPException(status_code=500, detail="Unexpected error while updating product feature.")


async def get_feature_with_sub_categories(db: AsyncSession, id: int):
    try:
        result = await db.execute(
            select(ProductFeatures).where(ProductFeatures.id == id)
        )
        feature = result.scalar_one_or_none()

        if not feature:
            raise HTTPException(status_code=404, detail="Product feature not found.")

        return {
            "id": feature.id,
            "name": feature.name,
            "type": feature.unit,
            "value": feature.value,
            "is_active": feature.is_active,
            "sub_categories": [
                {"id": sc.id, "name": sc.name}
                for sc in feature.sub_categories
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching feature details: {str(e)}")
