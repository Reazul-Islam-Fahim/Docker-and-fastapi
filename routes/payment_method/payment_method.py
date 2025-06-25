from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from database.db import get_db 
from schemas.payment_method.payment_method import PaymentMethodSchema
from crud.payment_method.payment_method import (
    create_payment_method,
    get_payment_method,
    get_all_payment_methods,
    update_payment_method,
)

router = APIRouter(
    prefix="/payment-methods",
    tags=["Payment Methods"]
)

@router.post("")
async def create(payment_method: PaymentMethodSchema, db: AsyncSession = Depends(get_db)):
    return await create_payment_method(db, payment_method)


@router.get("/{payment_method_id}")
async def read(payment_method_id: int, db: AsyncSession = Depends(get_db)):
    result = await get_payment_method(db, payment_method_id)
    if not result:
        raise HTTPException(status_code=404, detail="Payment method not found")
    return result


@router.get("")
async def read_all(is_active: bool | None = Query(default=None), page: int = 1, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await get_all_payment_methods(db, page=page, limit=limit, is_active=is_active)


@router.put("/{payment_method_id}")
async def update(payment_method_id: int, payment_method: PaymentMethodSchema, db: AsyncSession = Depends(get_db)):
    updated = await update_payment_method(db, payment_method_id, payment_method)
    if not updated:
        raise HTTPException(status_code=404, detail="Payment method not found")
    return updated
