from fastapi import APIRouter, Depends, HTTPException, Query, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from crud.sub_categories.sub_categories import (
    get_sub_category_by_id,
    get_all_sub_categories,
    update_sub_category,
    create_sub_category,
    get_products_by_sub_category_id
)
from database.db import get_db
from schemas.sub_categories.sub_categories import SubCategoriesSchema
from typing import Optional
from utils.save_files import save_file, UPLOAD_DIR as upload_dir
import os

router = APIRouter(prefix="/sub-categories", tags=["Sub-Categories"])

UPLOAD_DIR = os.path.join(upload_dir, "sub-categories")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("")
async def get_sub_categories(
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
    db: AsyncSession = Depends(get_db)
):
    return await get_all_sub_categories(db, page, limit)

@router.get("/{id}")
async def get_sub_category_by_id_data(id: int, db: AsyncSession = Depends(get_db)):
    return await get_sub_category_by_id(db, id)

@router.patch("/{id}")
async def patch_sub_category_info(
    id: int,
    name: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    product_feature_ids: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    update_data = {}

    if name is not None:
        update_data["name"] = name
    if category_id is not None:
        update_data["category_id"] = category_id
    if description is not None:
        update_data["description"] = description
    if meta_title is not None:
        update_data["meta_title"] = meta_title
    if meta_description is not None:
        update_data["meta_description"] = meta_description
    if is_active is not None:
        update_data["is_active"] = is_active

    if product_feature_ids:
        try:
            feature_ids_list = [int(f.strip()) for f in product_feature_ids.split(",") if f.strip().isdigit()]
            update_data["features_id"] = feature_ids_list
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid format for product_feature_ids. Must be comma-separated integers.")

    file_path = None
    if image:
        try:
            file_path = await save_file(image, folder=UPLOAD_DIR)
        finally:
            await image.close()

    return await update_sub_category(db, id, update_data, file_path)

@router.post("")
async def create_sub_category_data(
    name: str = Form(...),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    product_feature_ids: Optional[str] = Form(None),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        feature_ids = []
        if product_feature_ids:
            feature_ids = [int(f.strip()) for f in product_feature_ids.split(",") if f.strip().isdigit()]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid format for product_feature_ids")

    sub_category_data = SubCategoriesSchema(
        name=name,
        category_id=category_id,
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
        features_id=feature_ids,
        is_active=is_active
    )

    file_path = None
    if image:
        try:
            file_path = await save_file(image, folder=UPLOAD_DIR)
        finally:
            await image.close()

    return await create_sub_category(db, sub_category_data, file_path)

@router.get("/{sub_category_id}/products")
async def get_products_by_sub_category(
    sub_category_id: int,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1),
):
    return await get_products_by_sub_category_id(db, sub_category_id, page, limit)
