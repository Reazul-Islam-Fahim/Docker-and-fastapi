from fastapi import APIRouter, Depends, HTTPException, Query, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from crud.categories.categories import get_products_by_category_id, get_category_by_id, get_all_categories, get_sub_category_by_category_id, update_category, create_category
from database.db import get_db
from schemas.categories.categories import CategoriesSchema
from typing import Optional
import os
import shutil
import re

router = APIRouter(prefix="/categories", tags=["Categories"])

UPLOAD_DIR = "resources/categories"

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
async def get_categories(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await get_all_categories(db, page, limit, is_active)


@router.get("/{id}")
async def get_category_by_id_data(id: int, db: AsyncSession = Depends(get_db)):
    return await get_category_by_id(db, id)


@router.get("/get_sub_categories/{category_id}")
async def read_subcategories_by_category(category_id: int, db: AsyncSession = Depends(get_db)):
    return await get_sub_category_by_category_id(db, category_id)



@router.get("/{category_id}/products")
async def get_products_by_category(
    category_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await get_products_by_category_id(db, category_id)


@router.put("/{id}")
async def update_category_info(
    id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    category_data = CategoriesSchema(
        name=name,
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
        is_active=is_active
    )
    
    if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image.")

    filename = f"{name}_{image.filename.replace(' ', '_')}"
    file_path = os.path.join(UPLOAD_DIR, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    return await update_category(db, id, category_data, file_path)

@router.post("")
async def create_category_data(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    category_data = CategoriesSchema(
        name=name,
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
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

    return await create_category(db, category_data, file_path)