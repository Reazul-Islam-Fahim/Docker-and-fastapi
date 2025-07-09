from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException
from utils.serializers.serialize_user import serialize_user
from models.users.users import Users
from schemas.users.users import UpdateUserSchema
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import or_, and_
from datetime import datetime
from typing import Optional
from sqlalchemy import func


async def get_user(db: AsyncSession, id: int):
    result = await db.execute(select(Users).where(Users.id == id))
    db_user = result.scalar_one_or_none()

    if not db_user:
        return None

    return serialize_user(db_user)


async def get_users(
    db: AsyncSession,
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    user_id: Optional[int] = None,
    status: Optional[bool] = None,
    created_from: Optional[datetime] = None,
    created_to: Optional[datetime] = None,
    sort_by: str = "created_at",
    sort_order: str = "desc"
):
    offset = (page - 1) * limit
    base_query = select(Users)

    filters = []
    if user_id:
        filters.append(Users.id == user_id)
    if status is not None:
        filters.append(Users.is_active == status)
    if created_from:
        filters.append(Users.created_at >= created_from)
    if created_to:
        filters.append(Users.created_at <= created_to)
    if search:
        filters.append(
            or_(
                Users.name.ilike(f"%{search}%"),
                Users.email.ilike(f"%{search}%"),
                Users.phone.ilike(f"%{search}%")
            )
        )
    
    if filters:
        base_query = base_query.where(and_(*filters))

    count_query = select(func.count()).select_from(Users)
    if filters:
        count_query = count_query.where(and_(*filters))
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    sort_column = getattr(Users, sort_by, Users.created_at)
    if sort_order.lower() == "desc":
        base_query = base_query.order_by(sort_column.desc())
    else:
        base_query = base_query.order_by(sort_column.asc())

    base_query = base_query.offset(offset).limit(limit)
    result = await db.execute(base_query)
    users = result.scalars().all()

    return {
        "data": [serialize_user(user) for user in users],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    }




async def update_user(
    db: AsyncSession, 
    id: int, 
    user: UpdateUserSchema, 
    filePath: Optional[str] = None
):
    try: 
        result = await db.execute(select(Users).where(Users.id == id))
        db_user = result.scalar_one_or_none()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")

        db_user.name = user.name
        db_user.phone = user.phone
        db_user.dob = user.dob
        db_user.gender = user.gender
        if filePath:
            db_user.image = filePath

        await db.commit()
        await db.refresh(db_user)

        return serialize_user(db_user)

    except HTTPException:
        raise

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
