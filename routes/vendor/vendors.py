import json
from fastapi import APIRouter, Depends, HTTPException, Query, status, Form, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from crud.vendor.vendors import get_vendor_by_id, get_all_vendors, update_vendor, create_vendor
from database.db import get_db
from schemas.vendor.vendors import VendorsSchema
from models.vendor.vendors import Vendors 
from typing import Optional
import os
import shutil
from utils.slug import generate_unique_slug
from typing import List
from utils.save_files import save_file, UPLOAD_DIR as upload_dir


router = APIRouter(prefix="/vendors", tags=["Vendors"])

UPLOAD_DIR = os.path.join(upload_dir, "vendors")

os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("")
async def get_vendors(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    db: AsyncSession = Depends(get_db)
):
    return await get_all_vendors(db, skip, limit)

@router.get("/{id}")
async def get_vendor_by_id_data(id: int, db: AsyncSession = Depends(get_db)):
    vendor = await get_vendor_by_id(db, id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor is not found")
    return vendor

@router.put("/{id}")
async def update_sub_category_info(
    id: int,
    user_id: int = Form(...),
    store_name: Optional[str] = Form(None),
    documents: Optional[List[UploadFile]] = File(None),
    business_address: Optional[str] = Form(None),
    pick_address: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    is_verified: Optional[bool] = Form(None),
    is_shipping_enabled: Optional[bool] = Form(None),
    default_shipping_rate: Optional[int] = Form(None),
    free_shipping_threshold: Optional[int] = Form(None),
    total_sales: Optional[int] = Form(None),
    total_orders: Optional[int] = Form(None),
    last_order_date: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    try:
        image_path = await save_file(image, UPLOAD_DIR) if image else None

        document_paths = []
        if documents:
            for doc in documents:
                if not doc.content_type.startswith("image/") and not doc.content_type.startswith("application/"):
                    raise HTTPException(status_code=400, detail="Invalid document type.")
                doc_path = await save_file(doc, UPLOAD_DIR)
                document_paths.append(doc_path)

        vendor_data = VendorsSchema(
            user_id=user_id,
            vendor_slug=await generate_unique_slug(db, store_name, Vendors) if store_name else None,
            store_name=store_name,
            documents=document_paths or None,
            business_address=business_address,
            pick_address=pick_address,
            is_active=is_active,
            is_verified=is_verified,
            is_shipping_enabled=is_shipping_enabled,
            default_shipping_rate=default_shipping_rate,
            free_shipping_threshold=free_shipping_threshold,
            total_sales=total_sales,
            total_orders=total_orders,
            last_order_date=last_order_date
        )

        return await update_vendor(db, id, vendor_data, image_path)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.post("")
async def create_vendor_data(
    user_id: int = Form(...),
    store_name: str = Form(...),
    documents: Optional[List[UploadFile]] = File(None),
    business_address: Optional[str] = Form(None),
    pick_address: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(True),
    is_verified: Optional[bool] = Form(False),
    is_shipping_enabled: Optional[bool] = Form(False),
    default_shipping_rate: Optional[int] = Form(None),
    free_shipping_threshold: Optional[int] = Form(None),
    total_sales: Optional[int] = Form(0),
    total_orders: Optional[int] = Form(0),
    last_order_date: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db),
):
    try:
        image_path = await save_file(image, UPLOAD_DIR) if image else None

        document_paths = []
        if documents:
            for doc in documents:
                path = await save_file(doc, UPLOAD_DIR)
                document_paths.append(path)

        vendor_data = VendorsSchema(
            user_id=user_id,
            store_name=store_name,
            vendor_slug=await generate_unique_slug(db, store_name, Vendors),
            documents=document_paths,
            business_address=business_address,
            pick_address=pick_address,
            is_active=is_active,
            is_verified=is_verified,
            is_shipping_enabled=is_shipping_enabled,
            default_shipping_rate=default_shipping_rate,
            free_shipping_threshold=free_shipping_threshold,
            total_sales=total_sales,
            total_orders=total_orders,
            last_order_date=last_order_date
        )

        return await create_vendor(db, vendor_data, image_path)

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
