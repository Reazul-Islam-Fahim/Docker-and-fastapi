from typing import Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from utils.serializers.serialize_brand import serialize_brand
from models.brands.brands import Brands
from schemas.brands.brands import BrandSchema
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.exc import SQLAlchemyError


async def get_brands_by_id(db: AsyncSession, id: int):
    try:
        result = await db.execute(select(Brands).where(Brands.id == id))
        db_brand = result.scalar_one_or_none()

        if not db_brand:
            raise HTTPException(status_code=404, detail="Brand not found")

        return serialize_brand(db_brand)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching brand: {str(e)}")


async def get_all_brands(
    db: AsyncSession,
    page: int,
    limit: int,
    is_active: Optional[bool] = None
):
    try:
        base_query = select(Brands)

        if is_active is not None:
            base_query = base_query.where(Brands.is_active == is_active)

        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar_one()

        result = await db.execute(
            base_query.offset((page-1) * limit).limit(limit)
        )
        all_brands = result.scalars().all()

        return {
            "data": [serialize_brand(brand) for brand in all_brands],
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


async def update_brand(
    db: AsyncSession,
    id: int,
    update_data: dict,
    file_path: Optional[str] = None
):
    try:
        result = await db.execute(select(Brands).where(Brands.id == id))
        db_brand = result.scalar_one_or_none()

        if not db_brand:
            raise HTTPException(status_code=404, detail="Brand not found")

        for field, value in update_data.items():
            setattr(db_brand, field, value)

        if file_path:
            db_brand.image = file_path

        await db.commit()
        await db.refresh(db_brand)

        return serialize_brand(db_brand)

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=500, detail=f"Unexpected error: {str(e)}"
        )

async def create_brand(
    db: AsyncSession, 
    brand_data: BrandSchema,
    filePath: str
):
    try:
        result = await db.execute(
            select(Brands).where(Brands.name == brand_data.name)
        )
        existing_brand = result.scalar_one_or_none()
        
        if existing_brand:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Brand with this name already exists"
            )

        new_brand = Brands(
            name=brand_data.name,
            description=brand_data.description,
            image=filePath,
            is_active=brand_data.is_active
        )
        
        db.add(new_brand)
        await db.commit()
        await db.refresh(new_brand)
        
        return serialize_brand(new_brand)

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )