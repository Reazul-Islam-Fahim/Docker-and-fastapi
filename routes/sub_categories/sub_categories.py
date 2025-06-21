from fastapi import APIRouter, Depends, HTTPException, Query, status, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from crud.sub_categories.sub_categories import get_sub_category_by_id, get_all_sub_categories, update_sub_category, create_sub_category
from database.db import get_db
from schemas.sub_categories.sub_categories import SubCategoriesSchema
from typing import Optional
import os
import shutil
import re

router = APIRouter(prefix="/sub-categories", tags=["Sub-Categories"])

UPLOAD_DIR = "resources/sub-categories"

os.makedirs(UPLOAD_DIR, exist_ok=True)

# Slugify: replaces all unsafe characters and spaces with dashes
def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)         # remove special characters (commas, etc.)
    text = re.sub(r"\s+", "-", text.strip())     # replace spaces with dash
    return text

# Clean filename: remove unwanted characters and use dashes
def clean_file_name(file_name: str) -> str:
    file_name = file_name.lower()
    file_name = re.sub(r"[^\w\d.-]", "-", file_name)  # replace anything that's not alphanum, dot, or dash with dash
    file_name = re.sub(r"[-]+", "-", file_name)       # collapse multiple dashes into one
    return file_name.strip("-")

@router.get("")
async def get_sub_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: AsyncSession = Depends(get_db)
):
    return await get_all_sub_categories(db, skip, limit)

@router.get("/{id}")
async def get_sub_category_by_id_data(id: int, db: AsyncSession = Depends(get_db)):
    sub_category = await get_sub_category_by_id(db, id)
    if not sub_category:
        raise HTTPException(status_code=404, detail="Sub Category is not found")
    return sub_category


@router.put("/{id}")
async def update_sub_category_info(
    id: int,
    name: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(True),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    sub_category_data = SubCategoriesSchema(
        name=name,
        category_id=category_id,
        description=description,
        is_active=is_active
    )
    
    if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image.")

    filename = f"{name}_{image.filename.replace(' ', '_')}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    return await update_sub_category(db, id, sub_category_data, file_path)

@router.post("")
async def create_sub_category_data(
    name: str = Form(...),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    sub_category_data = SubCategoriesSchema(
        name=name,
        category_id=category_id,
        description=description,
        is_active=is_active
    )

    file_path = None

    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image.")

        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)

        slugified_name = slugify(name)
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

    return await create_sub_category(db, sub_category_data, file_path)