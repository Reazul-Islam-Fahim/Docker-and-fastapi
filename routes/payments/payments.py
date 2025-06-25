from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from database.db import get_db
from schemas.payments.payments import PaymentsSchema
from crud.payments.payments import (
    create_payment,
    get_payment,
    get_all_payments
)

router = APIRouter(
    prefix="/payments",
    tags=["Payments"]
)


@router.post("",)
async def create(payment: PaymentsSchema, db: AsyncSession = Depends(get_db)):
    return await create_payment(db, payment)


@router.get("/search")
async def read_payment(
    payment_id: Optional[int] = Query(None),
    transaction_id: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    order_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    payment = await get_payment(
        db,
        payment_id=payment_id,
        transaction_id=transaction_id,
        user_id=user_id,
        order_id=order_id
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment


@router.get("")
async def read_all(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1),
    is_active: Optional[bool] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    return await get_all_payments(db, page=page, limit=limit, is_active=is_active)


