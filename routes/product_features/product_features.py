from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from crud.product_features.product_features import (
    get_product_feature_by_id,
    get_all_product_features,
    create_product_feature,
    update_product_feature,
    get_feature_with_sub_categories
)
from database.db import get_db
from schemas.product_features.product_features import ProductFeaturesSchema
from typing import List, Optional

router = APIRouter(prefix="/product-features", tags=["Product-Features"])


@router.get("")
async def read_all_product_features(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(100, le=100),
    id: Optional[int] = Query(None),
    name: Optional[str] = Query(None),
    unit: Optional[str] = Query(None),
    value: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    sub_category_id: Optional[int] = Query(None)
):
    return await get_all_product_features(
        db=db,
        page=page,
        limit=limit,
        id=id,
        name=name,
        unit=unit,
        value=value,
        is_active=is_active,
        sub_category_id=sub_category_id
    )


@router.get("/{feature_id}")
async def read_product_feature_by_id(
    feature_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await get_product_feature_by_id(db, feature_id)


@router.post("")
async def create_feature(
    feature: ProductFeaturesSchema,
    db: AsyncSession = Depends(get_db)
):
    return await create_product_feature(db, feature)


@router.put("/{feature_id}")
async def update_feature(
    feature_id: int,
    feature: ProductFeaturesSchema,
    db: AsyncSession = Depends(get_db)
):
    return await update_product_feature(db, feature_id, feature)


@router.get("/{feature_id}/sub-categories")
async def get_feature_details_with_sub_categories(
    feature_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await get_feature_with_sub_categories(db, feature_id)
