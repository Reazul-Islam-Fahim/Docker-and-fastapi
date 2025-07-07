from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from crud.products.products import (
    create_product,
    get_product_by_id,
    get_all_products,
    get_products_by_vendor_id,
    update_product_by_id,
    update_product_by_vendor_id,
)
from schemas.products.products import ProductsSchema
from database.db import get_db
from models.products.products import DiscountTypeEnum
import os
import shutil
import uuid

router = APIRouter(prefix="/products", tags=["Products"])

UPLOAD_DIR = "resources/products"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_file(file: UploadFile, folder: str = UPLOAD_DIR) -> str:
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image.")
    os.makedirs(folder, exist_ok=True)
    ext = os.path.splitext(file.filename)[-1]
    filename = f"{uuid.uuid4().hex}{ext}"
    path = os.path.join(folder, filename)
    with open(path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return path


# This function applies filters to the product query based on the provided conditions.
@router.get("")
async def list_products(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1),
    is_active: Optional[bool] = Query(None),
    name: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    meta_title: Optional[str] = Query(None),
    meta_description: Optional[str] = Query(None),
    sub_category_id: Optional[int] = Query(None),
    category_id: Optional[int] = Query(None),
    brand_id: Optional[int] = Query(None),
    vendor_id: Optional[int] = Query(None),
    discount_type: Optional[DiscountTypeEnum] = Query(None),
    product_feature_name: Optional[str] = Query(None),
):
    return await get_all_products(
        db=db,
        page=page,
        limit=limit,
        is_active=is_active,
        name=name,
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
        sub_category_id=sub_category_id,
        category_id=category_id,
        brand_id=brand_id,
        vendor_id=vendor_id,
        discount_type=discount_type,
        product_feature_name=product_feature_name,
    )


@router.get("/{product_id}")
async def get_product(product_id: int, db: AsyncSession = Depends(get_db)):
    return await get_product_by_id(db, product_id)


@router.post("")
async def create_product_endpoint(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    price: float = Form(...),
    discount_type: DiscountTypeEnum = Form(...),
    discount_amount: Optional[float] = Form(None),
    is_active: bool = Form(True),
    sub_category_id: int = Form(...),
    brand_id: int = Form(...),
    vendor_id: int = Form(...),
    product_specific_features: Optional[List[int]] = Form(None),
    highlighted_image: Optional[UploadFile] = File(None),
    images: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_db),
):
    highlighted_image_path = save_file(highlighted_image) if highlighted_image else None
    image_paths = [save_file(img) for img in images] if images else []

    product_data = ProductsSchema(
        name=name,
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
        price=price,
        discount_type=discount_type,
        discount_amount=discount_amount,
        is_active=is_active,
        sub_category_id=sub_category_id,
        brand_id=brand_id,
        vendor_id=vendor_id,
        product_specific_features=product_specific_features
    )
    return await create_product(db, product_data, highlighted_image_path, image_paths)


@router.put("/{product_id}")
async def update_product_endpoint(
    product_id: int,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    price: float = Form(...),
    discount_type: DiscountTypeEnum = Form(...),
    discount_amount: Optional[float] = Form(None),
    is_active: bool = Form(True),
    sub_category_id: int = Form(...),
    brand_id: int = Form(...),
    vendor_id: int = Form(...),
    product_specific_features: Optional[List[int]] = Form(None),
    highlighted_image: Optional[UploadFile] = File(None),
    images: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_db),
):
    highlighted_image_path = save_file(highlighted_image) if highlighted_image else None
    image_paths = [save_file(img) for img in images] if images else []

    product_data = ProductsSchema(
        name=name,
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
        price=price,
        discount_type=discount_type,
        discount_amount=discount_amount,
        is_active=is_active,
        sub_category_id=sub_category_id,
        brand_id=brand_id,
        vendor_id=vendor_id,
        product_specific_features=product_specific_features
    )

    return await update_product_by_id(db, product_id, product_data, highlighted_image_path, image_paths)


@router.get("/vendor/{vendor_id}")
async def list_products_by_vendor_id(
    vendor_id: int,
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await get_products_by_vendor_id(db, vendor_id, page, limit, is_active)


@router.put("/vendor/{product_id}")
async def update_specific_product_by_vendor_id(
    product_id: int,
    current_vendor_id: int = Form(...),
    name: str = Form(...),
    description: Optional[str] = Form(None),
    meta_title: Optional[str] = Form(None),
    meta_description: Optional[str] = Form(None),
    price: float = Form(...),
    discount_type: DiscountTypeEnum = Form(...),
    discount_amount: Optional[float] = Form(None),
    is_active: bool = Form(True),
    sub_category_id: int = Form(...),
    brand_id: int = Form(...),
    product_specific_features: Optional[List[int]] = Form(None),
    highlighted_image: Optional[UploadFile] = File(None),
    images: Optional[List[UploadFile]] = File(None),
    db: AsyncSession = Depends(get_db),
):
    highlighted_image_path = save_file(highlighted_image) if highlighted_image else None
    image_paths = [save_file(img) for img in images] if images else []

    product_data = ProductsSchema(
        name=name,
        description=description,
        meta_title=meta_title,
        meta_description=meta_description,
        price=price,
        discount_type=discount_type,
        discount_amount=discount_amount,
        is_active=is_active,
        sub_category_id=sub_category_id,
        brand_id=brand_id,
        vendor_id=current_vendor_id,
        product_specific_features=product_specific_features
    )

    return await update_product_by_vendor_id(
        db=db,
        product_id=product_id,
        product_data=product_data,
        vendor_id=current_vendor_id,
        highligthed_image_path=highlighted_image_path,
        image_paths=image_paths,
    )
