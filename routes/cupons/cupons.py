from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db
from schemas.cupons.cupons import CuponsSchema
from crud.cupons.cupons import (
    create_cupon,
    get_cupon_by_id,
    get_all_cupons,
    get_cupon_by_code,
    update_cupon
)

router = APIRouter(prefix="/cupons", tags=["Cupons"])

@router.post("",)
async def create_new_cupon(cupon_data: CuponsSchema, db: AsyncSession = Depends(get_db)):
    cupon = await create_cupon(db, cupon_data)
    if not cupon:
        raise HTTPException(status_code=400, detail="Error creating cupon")
    return cupon


@router.get("")
async def read_all_cupons(
    db: AsyncSession = Depends(get_db),
    page: int = 1, 
    limit: int = 100, 
    is_active: Optional[bool] = Query(None),
    ):
    return await get_all_cupons(db, page, limit, is_active)


@router.get("/{cupon_id}")
async def read_cupon_by_id(cupon_id: int, db: AsyncSession = Depends(get_db)):
    cupon = await get_cupon_by_id(db, cupon_id)
    if not cupon:
        raise HTTPException(status_code=404, detail="Cupon not found")
    return cupon


@router.get("/code/{code}")
async def read_cupon_by_code(code: str, db: AsyncSession = Depends(get_db)):
    cupon = await get_cupon_by_code(db, code)
    if not cupon:
        raise HTTPException(status_code=404, detail="Cupon not found")
    return cupon


@router.put("/{cupon_id}")
async def update_existing_cupon(cupon_id: int, cupon_data: CuponsSchema, db: AsyncSession = Depends(get_db)):
    cupon = await update_cupon(db, cupon_id, cupon_data)
    if not cupon:
        raise HTTPException(status_code=404, detail="Cupon not found or update failed")
    return cupon
