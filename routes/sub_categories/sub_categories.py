from fastapi import APIRouter, Depends, HTTPException, Query, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from crud.sub_categories.sub_categories import (
    get_sub_category_by_id,
    get_sub_category_by_id,
    get_all_sub_categories,
    update_sub_category,
    create_sub_category
)
from database.db import get_db
from schemas.sub_categories.sub_categories import SubCategoriesSchema
from typing import List, Optional
import os
import shutil
import re
import json

router = APIRouter(prefix="/sub-categories", tags=["Sub-Categories"])

UPLOAD_DIR = "resources/sub-categories"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def slugify(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text

def clean_file_name(file_name: str) -> str:
    file_name = file_name.lower()
    file_name = re.sub(r"[^\w\d.-]", "-", file_name)
    file_name = re.sub(r"[-]+", "-", file_name)
    return file_name.strip("-")


@router.get("")
async def get_sub_categories(
    page: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: AsyncSession = Depends(get_db)
):
    return await get_all_sub_categories(db, page, limit)


@router.get("/{id}")
async def get_sub_category_by_id_data(id: int, db: AsyncSession = Depends(get_db)):
    return await get_sub_category_by_id(db, id)


@router.put("/{id}")
async def update_sub_category_info(
    id: int,
    name: Optional[str] = Form(None),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    product_feature_ids: Optional[str] = Form(None),  # JSON string list from client
    is_active: Optional[bool] = Form(True),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        feature_ids_list = json.loads(product_feature_ids) if product_feature_ids else []
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid format for product_feature_ids")

    sub_category_data = SubCategoriesSchema(
        name=name,
        category_id=category_id,
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
        features_id=feature_ids_list,
        is_active=is_active
    )

    file_path = None
    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image.")
        filename = f"{slugify(name)}_{clean_file_name(image.filename)}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    return await update_sub_category(db, id, sub_category_data, file_path)


@router.post("")
async def create_sub_category_data(
    name: str = Form(...),
    category_id: Optional[int] = Form(None),
    description: Optional[str] = Form(None),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    product_feature_ids: Optional[List[int]] = Form(None),
    is_active: bool = Form(True),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    sub_category_data = SubCategoriesSchema(
        name=name,
        category_id=category_id,
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
        features_id=product_feature_ids if product_feature_ids else [],
        is_active=is_active
    )

    file_path = None
    if image:
        if not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image.")
        filename = f"{slugify(name)}_{clean_file_name(image.filename)}"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

    return await create_sub_category(db, sub_category_data, file_path)


@router.get("/{sub_category_id}/products")
async def get_products_by_sub_category(
    sub_category_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await get_sub_category_by_id(db, sub_category_id)
