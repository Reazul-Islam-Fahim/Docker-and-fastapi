from fastapi import APIRouter, Depends, HTTPException, Query, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from crud.slider.slider import get_all_sliders, create_slider, update_slider, get_slider_by_id, get_sliders_by_slider_type_id
from database.db import get_db
from schemas.slider.slider import SlidersSchema, UpdateSlidersSchema
from typing import Optional
import os
import shutil
import re

router = APIRouter(prefix="/sliders", tags=["Sliders"])

UPLOAD_DIR = "resources/sliders"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Slugify: replaces all unsafe characters and spaces with dashes
def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text

# Clean filename: remove unwanted characters and use dashes
def clean_file_name(file_name: str) -> str:
    file_name = file_name.lower()
    file_name = re.sub(r"[^\w\d.-]", "-", file_name)
    file_name = re.sub(r"[-]+", "-", file_name)
    return file_name.strip("-")


@router.get("")
async def get_all_sliders_data(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await get_all_sliders(db, page, limit, is_active)

@router.get("/{slider_id}")
async def read_slider_by_id(slider_id: int, db: AsyncSession = Depends(get_db)):
    return await get_slider_by_id(db, slider_id)

@router.get("/by-type/{slider_type_id}")
async def read_sliders_by_type(
    slider_type_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    db: AsyncSession = Depends(get_db)
):
    return await get_sliders_by_slider_type_id(db, slider_type_id, page, limit)

@router.post("")
async def create_slider_data(
    db: AsyncSession = Depends(get_db),
    image: Optional[UploadFile] = File(None),
    link: str = Form(...),
    expiration_date: str = Form(...),
    slider_type_id: int = Form(...),
    vendor_id: int = Form(...),
    payment_id: Optional[int] = Form(None),
    category_id: Optional[int] = Form(None),
    sub_category_id: Optional[int] = Form(None),
):
    slider_data = SlidersSchema(
        link=link,
        is_paid=False,
        expiration_date=expiration_date,
        slider_type_id=slider_type_id,
        vendor_id=vendor_id,
        payment_id=payment_id,
        category_id=category_id,
        sub_category_id=sub_category_id,
        created_at=None,
        updated_at=None
    )

    file_path = None

    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image.")

        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        slugified_name = slugify("slider")
        sanitized_filename = clean_file_name(image.filename)
        final_filename = f"{slugified_name}-{sanitized_filename}"

        file_path = os.path.join(UPLOAD_DIR, final_filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to save image: {str(e)}")
        finally:
            await image.close()

    return await create_slider(db, slider_data, file_path)

@router.patch("/{id}")
async def update_slider_info(
    id: int,
    db: AsyncSession = Depends(get_db),
    image: Optional[UploadFile] = File(None),
    link: Optional[str] = Form(None),
    expiration_date: Optional[str] = Form(None),
    slider_type_id: Optional[int] = Form(None),
    vendor_id: Optional[int] = Form(None),
    payment_id: Optional[int] = Form(None),
    category_id: Optional[int] = Form(None),
    sub_category_id: Optional[int] = Form(None),
):
    file_path = None
    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image.")

        filename = image.filename.replace(" ", "_")
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    slider_data = UpdateSlidersSchema(
        link=link,
        is_paid=False,
        expiration_date=expiration_date,
        slider_type_id=slider_type_id,
        vendor_id=vendor_id,
        payment_id=payment_id,
        category_id=category_id,
        sub_category_id=sub_category_id,
        created_at=None,
        updated_at=None
    )

    return await update_slider(db, id, slider_data, file_path)