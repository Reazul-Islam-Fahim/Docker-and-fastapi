from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select
from models.slider_type.slider_type import SliderType
from schemas.slider_type.slider_type import SliderTypeSchema

async def create_slider_type(
    db: AsyncSession,
    slider_data: SliderTypeSchema,
):
    try:
        new_slider = SliderType(
            type=slider_data.type,
            description=slider_data.description,
            rate=slider_data.rate,
            height=slider_data.height,
            width=slider_data.width,
            is_active=slider_data.is_active,
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
        
async def get_slider_types(
    db: AsyncSession,
    is_active: bool | None = None,
    page: int = 1,
    limit: int = 10,
):
    try:
        query = select(SliderType)

        if is_active is not None:
            query = query.where(SliderType.is_active == is_active)

        total = await db.scalar(select(func.count()).select_from(query.subquery()))

        offset = (page - 1) * limit
        result = await db.execute(query.offset(offset).limit(limit))

        slider_types = result.scalars().all()

        return {
            "data": slider_types,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit,
            }
        }

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )

async def get_slider_type_by_id(
    db: AsyncSession,
    slider_type_id: int
):
    try:
        result = await db.execute(
            select(SliderType).where(SliderType.id == slider_type_id)
        )
        slider_type = result.scalar_one_or_none()

        if not slider_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slider type not found"
            )

        return slider_type

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
        
async def update_slider_type(
    db: AsyncSession,
    slider_type_id: int,
    slider_data: SliderTypeSchema
):
    try:
        result = await db.execute(
            select(SliderType).where(SliderType.id == slider_type_id)
        )
        db_slider_type = result.scalar_one_or_none()

        if not db_slider_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slider type not found"
            )

        db_slider_type.type = slider_data.type
        db_slider_type.description = slider_data.description
        db_slider_type.rate = slider_data.rate
        db_slider_type.height = slider_data.height
        db_slider_type.width = slider_data.width
        db_slider_type.is_active = slider_data.is_active

        await db.commit()
        await db.refresh(db_slider_type)

        return db_slider_type

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )