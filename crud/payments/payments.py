from typing import Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status
from models.payments.payments import Payments
from schemas.payments.payments import PaymentsSchema
from utils.transaction import generate_transaction_id

async def create_payment(db: AsyncSession, payment: PaymentsSchema):
    try:
        db_payment = Payments(
            user_id=payment.user_id,
            order_id=payment.order_id,
            payment_method_id=payment.payment_method_id,
            amount=payment.amount,
            transaction_id=generate_transaction_id(),
    )
        db.add(db_payment)
        await db.commit()
        await db.refresh(db_payment)
        return db_payment
    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while creating payment: {str(e)}"
        )


async def get_payment(
    db: AsyncSession,
    payment_id: Optional[int] = None,
    transaction_id: Optional[str] = None,
    user_id: Optional[int] = None,
    order_id: Optional[int] = None,
):
    try:
        query = select(Payments)

        if payment_id is not None:
            query = query.where(Payments.id == payment_id)
        elif transaction_id is not None:
            query = query.where(Payments.transaction_id == transaction_id)
        elif user_id is not None:
            query = query.where(Payments.user_id == user_id)
        elif order_id is not None:
            query = query.where(Payments.order_id == order_id)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one filter (id, transaction_id, user_id, or order_id) must be provided"
            )

        result = await db.execute(query)
        return result.scalars().first()

    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while fetching payment: {str(e)}"
        )


async def get_all_payments(
    db: AsyncSession,
    page: int,
    limit: int,
    is_active: Optional[bool] = None
):
    try:
        page = max(1, page)
        limit = max(1, limit)
        offset = (page - 1) * limit

        query = select(Payments)

        if is_active is not None:
            query = query.where(Payments.is_active == is_active)

        total = await db.scalar(select(func.count()).select_from(query.subquery()))

        result = await db.execute(query.offset(offset).limit(limit))
        payments = result.scalars().all()

        return {
            "data": payments,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit,
            }
        }
    except SQLAlchemyError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error while fetching payments: {str(e)}"
        )
