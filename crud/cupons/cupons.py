import logging
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from models.cupons.cupons import Cupons
from schemas.cupons.cupons import CuponsSchema

logger = logging.getLogger(__name__)


async def create_cupon(db: AsyncSession, cupon_data: CuponsSchema):
    try:
        if cupon_data.expires_at <= datetime.now(timezone.utc):
            raise ValueError("expires_at must be a future datetime")

        db_cupon = Cupons(
            code=cupon_data.code,
            discount_percentage=cupon_data.discount_percentage,
            max_discount=cupon_data.max_discount,
            min_purchase=cupon_data.min_purchase,
            max_used=cupon_data.max_used,
            used_count=cupon_data.used_count if cupon_data.used_count is not None else 0,
            is_active=cupon_data.is_active,
            expires_at=cupon_data.expires_at
        )
        db.add(db_cupon)
        await db.commit()
        await db.refresh(db_cupon)
        return db_cupon
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating cupon: {e}")
        return None


async def get_cupon_by_id(db: AsyncSession, cupon_id: int):
    try:
        result = await db.execute(select(Cupons).where(Cupons.id == cupon_id))
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error fetching cupon by ID: {e}")
        return None


async def get_all_cupons(
    db: AsyncSession, 
    page: int = 1, 
    limit: int = 100,
    is_active: Optional[bool] = None
    ):
    page = max(page, 1)
    limit = max(limit, 1)
    offset = (page - 1) * limit
    query = select(Cupons).offset(offset).limit(limit)
    if is_active is not None:
        query = query.where(Cupons.is_active == is_active)
    
    try:
        total_result = await db.execute(select(func.count()).select_from(query.subquery()))
        total = total_result.scalar()

        result = await db.execute(
            query.offset(offset).limit(limit)
        )
        coupons = result.scalars().all()
        
        return {
        "data": [
            {
                "id": c.id,
                "code": c.code,
                "discount_percentage": c.discount_percentage,
                "max_discount": c.max_discount,
                "min_purchase": c.min_purchase,
                "max_used": c.max_used,
                "used_count": c.used_count,
                "expires_at": c.expires_at,
                "is_active": c.is_active,
                "created_at": c.created_at,
            }
            for c in coupons
        ],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    }
        
    except Exception as e:
        logger.error(f"Error fetching all cupons: {e}")
        return []


async def get_cupon_by_code(db: AsyncSession, code: str):
    try:
        result = await db.execute(select(Cupons).where(Cupons.code == code))
        return result.scalars().first()
    except Exception as e:
        logger.error(f"Error fetching cupon by code: {e}")
        return None


async def update_cupon(db: AsyncSession, cupon_id: int, cupon_data: CuponsSchema):
    try:
        result = await db.execute(select(Cupons).where(Cupons.id == cupon_id))
        cupon = result.scalars().first()
        if not cupon:
            return None

        if cupon_data.expires_at <= datetime.now(timezone.utc):
            raise ValueError("expires_at must be a future datetime")

        cupon.code = cupon_data.code
        cupon.discount_percentage = cupon_data.discount_percentage
        cupon.max_discount = cupon_data.max_discount
        cupon.min_purchase = cupon_data.min_purchase
        cupon.max_used = cupon_data.max_used
        cupon.used_count = cupon_data.used_count if cupon_data.used_count is not None else 0
        cupon.is_active = cupon_data.is_active
        cupon.expires_at = cupon_data.expires_at

        await db.commit()
        await db.refresh(cupon)
        return cupon
    except Exception as e:
        await db.rollback()
        logger.error(f"Error updating cupon: {e}")
        return None
