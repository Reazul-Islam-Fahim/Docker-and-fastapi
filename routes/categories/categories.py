from fastapi import APIRouter, Depends, HTTPException, Query, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from crud.categories.categories import (
    get_products_by_category_id,
    get_category_by_id,
    get_all_categories,
    get_sub_category_by_category_id,
    update_category,
    create_category
)
from database.db import get_db
from schemas.categories.categories import CategoriesSchema
from typing import Optional
from utils.save_files import save_file, UPLOAD_DIR as upload_dir
import os

router = APIRouter(prefix="/categories", tags=["Categories"])

UPLOAD_DIR = os.path.join(upload_dir, "categories")
os.makedirs(UPLOAD_DIR, exist_ok=True)

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
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1)
):
    return await get_products_by_category_id(db, category_id, page, limit)


@router.patch("/{id}")
async def update_category_info(
    id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    data = {}

    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if meta_title is not None:
        data["meta_title"] = meta_title
    if meta_description is not None:
        data["meta_description"] = meta_description
    if is_active is not None:
        data["is_active"] = is_active

    file_path = None
    if image:
        try:
            file_path = await save_file(image, folder=UPLOAD_DIR)
        finally:
            await image.close()

    return await update_category(db, id, data, file_path)


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
        try:
            file_path = await save_file(image, folder=UPLOAD_DIR)
        finally:
            await image.close()

    return await create_category(db, category_data, file_path)
