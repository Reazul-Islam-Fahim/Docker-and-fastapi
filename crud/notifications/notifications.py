import math
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from models.notifications.notifications import Notifications
from schemas.notifications.notifications import NotificationsSchema


async def create_notification(db: AsyncSession, notification: NotificationsSchema):
    try:
        db_notification = Notifications(
            user_id=notification.user_id,
            message=notification.message,
            type=notification.type,
            is_read=notification.is_read
        )
        db.add(db_notification)
        await db.commit()
        await db.refresh(db_notification)
        return db_notification
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Failed to create notification: {e}")


async def get_notifications_by_user(
    db: AsyncSession,
    user_id: int,
    page: int,
    limit: int
):
    try:
        page = max(page, 1)
        skip = (page - 1) * limit

        count_result = await db.execute(
            select(func.count()).select_from(Notifications).where(Notifications.user_id == user_id)
        )
        total = count_result.scalar_one()
        total_pages = math.ceil(total / limit) if limit else 1

        result = await db.execute(
            select(Notifications)
            .where(Notifications.user_id == user_id)
            .order_by(Notifications.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        items = result.scalars().all()

        return {
            "data": [
                {
                    "id": n.id,
                    "message": n.message,
                    "type": n.type,
                    "is_read": n.is_read,
                    "created_at": n.created_at,
                    "user_id": n.user_id,
                }
                for n in items
            ],
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": total_pages
            }
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch paginated notifications: {e}")


async def get_notification_by_id(db: AsyncSession, notification_id: int):
    try:
        result = await db.execute(
            select(Notifications).where(Notifications.id == notification_id)
        )
        return result.scalar_one_or_none()
    except SQLAlchemyError as e:
        raise Exception(f"Failed to get notification by ID: {e}")


async def mark_notification_as_read(db: AsyncSession, notification_id: int):
    try:
        result = await db.execute(
            select(Notifications).where(Notifications.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if not notification:
            return None
        notification.is_read = True
        await db.commit()
        await db.refresh(notification)
        return notification
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Failed to mark notification as read: {e}")


async def delete_notification(db: AsyncSession, notification_id: int):
    try:
        result = await db.execute(
            select(Notifications).where(Notifications.id == notification_id)
        )
        notification = result.scalar_one_or_none()
        if not notification:
            return None
        await db.delete(notification)
        await db.commit()
        return notification
    except SQLAlchemyError as e:
        await db.rollback()
        raise Exception(f"Failed to delete notification: {e}")


async def get_unread_notifications(db: AsyncSession, user_id: int):
    try:
        result = await db.execute(
            select(Notifications)
            .where(Notifications.user_id == user_id, Notifications.is_read == False)
        )
        return result.scalars().all()
    except SQLAlchemyError as e:
        raise Exception(f"Failed to get unread notifications: {e}")


async def count_unread_notifications(db: AsyncSession, user_id: int):
    try:
        result = await db.execute(
            select(func.count()).select_from(Notifications).where(
                Notifications.user_id == user_id,
                Notifications.is_read == False
            )
        )
        return result.scalar()
    except SQLAlchemyError as e:
        raise Exception(f"Failed to count unread notifications: {e}")
