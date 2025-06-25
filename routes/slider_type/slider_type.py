from click import group
from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from crud.slider_type.slider_type import (
    create_slider_type,
    get_slider_type_by_id,
    get_slider_types,
    update_slider_type,
)
from database.db import get_db
from schemas.slider_type.slider_type import SliderTypeSchema
from typing import Optional

router = APIRouter(prefix="/slider_type", tags=["Slider Type"])

@router.post("")
async def create_slider_type_data(
    type: str = Form(...),
    description: Optional[str] = Form(None),  # Description is optional
    rate: float = Form(...),
    height: int = Form(...),
    width: int = Form(...),
    is_active: bool = Form(True),
    db: AsyncSession = Depends(get_db),
):
    slider_data = SliderTypeSchema(
        type=type,
        description=description,  # Description is optional and can be set later
        rate=rate,
        height=height,
        width=width,
        is_active=is_active
    )

    return await create_slider_type(db, slider_data)

@router.get("")
async def get_slider_types_data(
    db: AsyncSession = Depends(get_db),
    is_active: bool | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
):
    return await get_slider_types(db=db, is_active=is_active, page=page, limit=limit)

@router.get("/{slider_type_id}")
async def get_slider_type_data(
    slider_type_id: int,
    db: AsyncSession = Depends(get_db)
):
    slider_type = await get_slider_type_by_id(db, slider_type_id)
    if not slider_type:
        raise HTTPException(status_code=404, detail="Slider Type not found")
    return slider_type

@router.put("/{slider_type_id}")
async def update_slider_type_data(
    slider_type_id: int,
    type: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    rate: Optional[float] = Form(None),
    height: Optional[int] = Form(None),
    width: Optional[int] = Form(None),
    is_active: Optional[bool] = Form(True),
    db: AsyncSession = Depends(get_db)
):
    slider_data = SliderTypeSchema(
        type=type,
        description=description,
        rate=rate,
        height=height,
        width=width,
        is_active=is_active
    )

    slider_type = await get_slider_type_by_id(db, slider_type_id)
    if not slider_type:
        raise HTTPException(status_code=404, detail="Slider Type not found")

    # Update the fields that are provided
    for key, value in slider_data.dict(exclude_unset=True).items():
        setattr(slider_type, key, value)

    db.add(slider_type)
    await db.commit()
    await db.refresh(slider_type)

    return slider_type