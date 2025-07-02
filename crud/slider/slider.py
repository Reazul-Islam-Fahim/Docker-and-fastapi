from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from models.slider.slider import Sliders
from schemas.slider.slider import SlidersSchema, UpdateSlidersSchema
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func
from typing import Optional

#Create Sliders
async def create_slider(
    db: AsyncSession,
    slider_data: SlidersSchema,
    file_path: Optional[str] = None
):
    try:
        # Determine is_paid and is_active based on payments_id
        is_paid = True if slider_data.payment_id else False
        is_active = True if slider_data.payment_id else False

        new_slider = Sliders(
            link=slider_data.link,
            is_paid=is_paid,
            is_active=is_active,
            expiration_date=slider_data.expiration_date,
            slider_type_id=slider_data.slider_type_id,
            vendor_id=slider_data.vendor_id,
            payment_id=slider_data.payment_id,
            category_id=slider_data.category_id,
            sub_category_id=slider_data.sub_category_id,
            image=file_path,
            created_at=slider_data.created_at or func.now(),
            updated_at=slider_data.updated_at or func.now(),
        )

        db.add(new_slider)
        await db.commit()
        await db.refresh(new_slider)

        return new_slider

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

        
# Get all Sliderss
async def get_all_sliders(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    is_active: Optional[bool] = None
):
    page = max(page, 1)
    limit = max(limit, 1)
    offset = (page - 1) * limit
    query = select(Sliders).options(
        selectinload(Sliders.slider_type),
        selectinload(Sliders.vendors),
        selectinload(Sliders.payments),
        selectinload(Sliders.categories),
        selectinload(Sliders.sub_categories)
    )
    if is_active is not None:
        query = query.where(Sliders.is_active == is_active)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    result = await db.execute(
        query.offset(offset).limit(limit)
    )

    sliders = result.scalars().all()

    return {
        "data": [
            {
                "id": c.id,
                "image": c.image,
                "link": c.link,
                "is_paid": c.is_paid,
                "is_active": c.is_active,
                "expiration_date": c.expiration_date,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "slider_type_id": c.slider_type_id,
                "vendor_id": c.vendor_id,
                "payment_id": c.payment_id,
                "category_id": c.category_id,
                "sub_category_id": c.sub_category_id,
                "slider_type": {
                    "id": c.slider_type.id,
                    "type": c.slider_type.type,
                    "description": c.slider_type.description,
                    "rate": c.slider_type.rate,
                    "height": c.slider_type.height,
                    "width": c.slider_type.width,
                    "is_active": c.slider_type.is_active,
                } if c.slider_type else None,
                "vendors": {
                    "id": c.vendors.id,
                    "user_id": c.vendors.user_id,
                    "store_name": c.vendors.store_name,
                    "is_active": c.vendors.is_active,
                } if c.vendors else None,
                "payments": {
                    "id": c.payments.id,
                    "method": c.payments.method,
                } if c.payments else None,
                "categories": {
                    "id": c.categories.id,
                    "name": c.categories.name,
                } if c.categories else None,
                "sub_categories": {
                    "id": c.sub_categories.id,
                    "name": c.sub_categories.name,
                } if c.sub_categories else None,
            }
            for c in sliders
        ],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    }
    
#Get Slider By ID
async def get_slider_by_id(db: AsyncSession, id: int):
    result = await db.execute(
        select(Sliders).options(
            selectinload(Sliders.slider_type),
            selectinload(Sliders.vendors),
            selectinload(Sliders.payments),
            selectinload(Sliders.categories),
            selectinload(Sliders.sub_categories)
        ).where(Sliders.id == id)
    )
    slider = result.scalar_one_or_none()
    if not slider:
        raise HTTPException(status_code=404, detail="Slider not found")
    return slider


#Get Sliders by slider_type_id with pagination
async def get_sliders_by_slider_type_id(db: AsyncSession, slider_type_id: int, page: int = 1, limit: int = 20):
    offset = (page - 1) * limit

    query = select(Sliders).where(Sliders.slider_type_id == slider_type_id).options(
        selectinload(Sliders.slider_type),
        selectinload(Sliders.vendors),
        selectinload(Sliders.payments),
        selectinload(Sliders.categories),
        selectinload(Sliders.sub_categories)
    )

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    result = await db.execute(query.offset(offset).limit(limit))
    sliders = result.scalars().all()

    return {
        "data": [
            {
                "id": c.id,
                "image": c.image,
                "link": c.link,
                "is_paid": c.is_paid,
                "is_active": c.is_active,
                "expiration_date": c.expiration_date,
                "created_at": c.created_at,
                "updated_at": c.updated_at,
                "slider_type_id": c.slider_type_id,
                "vendor_id": c.vendor_id,
                "payment_id": c.payment_id,
                "category_id": c.category_id,
                "sub_category_id": c.sub_category_id,
                "slider_type": {
                    "id": c.slider_type.id,
                    "type": c.slider_type.type,
                    "description": c.slider_type.description
                } if c.slider_type else None
            } for c in sliders
        ],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    }

#Update Sliders
async def update_slider(
    db: AsyncSession,
    id: int,
    slider_data: UpdateSlidersSchema,
    filePath: Optional[str] = None
):
    try:
        result = await db.execute(select(Sliders).where(Sliders.id == id))
        db_slider = result.scalar_one_or_none()

        if not db_slider:
            raise HTTPException(status_code=404, detail="Slider is not found")

        # Update only provided fields
        if slider_data.link is not None:
            db_slider.link = slider_data.link

        if slider_data.expiration_date is not None:
            db_slider.expiration_date = slider_data.expiration_date

        if slider_data.slider_type_id is not None:
            db_slider.slider_type_id = slider_data.slider_type_id

        if slider_data.vendor_id is not None:
            db_slider.vendor_id = slider_data.vendor_id

        if slider_data.payment_id is not None:
            db_slider.payment_id = slider_data.payment_id
            db_slider.is_paid = True
            db_slider.is_active = True
        else:
            db_slider.payment_id = None
            db_slider.is_paid = False
            db_slider.is_active = False

        if slider_data.category_id is not None:
            db_slider.category_id = slider_data.category_id

        if slider_data.sub_category_id is not None:
            db_slider.sub_category_id = slider_data.sub_category_id

        db_slider.updated_at = func.now()

        if filePath:
            db_slider.image = filePath

        await db.commit()
        await db.refresh(db_slider)

        return db_slider

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")