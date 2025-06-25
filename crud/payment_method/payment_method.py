from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import SQLAlchemyError
from models.payment_method.payment_method import PaymentMethod
from schemas.payment_method.payment_method import PaymentMethodSchema


async def create_payment_method(db: AsyncSession, payment_method: PaymentMethodSchema):
    try:
        db_payment_method = PaymentMethod(
            name=payment_method.name,
            is_active=payment_method.is_active
        )
        db.add(db_payment_method)
        await db.commit()
        await db.refresh(db_payment_method)
        return db_payment_method
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Failed to create payment method: {e}")
        raise


async def get_payment_method(db: AsyncSession, payment_method_id: int):
    try:
        result = await db.execute(select(PaymentMethod).filter(PaymentMethod.id == payment_method_id))
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        print(f"Failed to get payment method with id {payment_method_id}: {e}")
        raise



async def get_all_payment_methods(
    db: AsyncSession,
    page: int,
    limit: int,
    is_active: bool | None = None
    
):
    try:
        query = select(PaymentMethod)

        if is_active is not None:
            query = query.where(PaymentMethod.is_active == is_active)

        total = await db.scalar(select(func.count()).select_from(query.subquery()))

        offset = (page - 1) * limit
        result = await db.execute(query.offset(offset).limit(limit))
        payment_methods = result.scalars().all()

        return {
            "data": payment_methods,
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
            detail=f"Database error: {str(e)}"
        )

async def update_payment_method(db: AsyncSession, payment_method_id: int, payment_method: PaymentMethodSchema):
    try:
        result = await db.execute(select(PaymentMethod).filter(PaymentMethod.id == payment_method_id))
        db_payment_method = result.scalar_one_or_none()
        
        if not db_payment_method:
            return None

        db_payment_method.name = payment_method.name
        db_payment_method.is_active = payment_method.is_active

        await db.commit()
        await db.refresh(db_payment_method)
        return db_payment_method
    except SQLAlchemyError as e:
        await db.rollback()
        print(f"Failed to update payment method {payment_method_id}: {e}")
        raise
