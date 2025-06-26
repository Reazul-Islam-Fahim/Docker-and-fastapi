from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from database.db import get_db
from crud.search.search import search_products as search_products_crud

router = APIRouter()

@router.get("/products/search")
async def search_products(
    q: str = Query(..., min_length=3),
    brand_id: Optional[int] = None,
    subcategory_id: Optional[int] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    sort_by: Optional[str] = None,
    order: Optional[str] = "asc",
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    total, products = await search_products_crud(
        db=db,
        q=q,
        brand_id=brand_id,
        subcategory_id=subcategory_id,
        min_price=min_price,
        max_price=max_price,
        sort_by=sort_by,
        order=order,
        page=page,
        limit=limit
    )

    return {
        "page": page,
        "limit": limit,
        "total": total,
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "price": float(p.price),
                "payable_price": float(p.payable_price),
                "available_stock": p.available_stock,
                "brand": p.brand.name if p.brand else None,
                "subcategory": p.subcategory.name if p.subcategory else None,
                "slug": p.slug,
                "highligthed_image": p.highligthed_image or [],
            } for p in products
        ]
    }
