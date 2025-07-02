from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from crud.notifications import notifications as notification_crud
from schemas.notifications.notifications import NotificationsSchema
from database.db import get_db  
from utils.sockets import socket_manager

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

@router.post("")
async def create_notification(notification: NotificationsSchema, db: AsyncSession = Depends(get_db)):
    try:
        created = await notification_crud.create_notification(db, notification)

        await socket_manager.emit(
            "new_notification",
            {
                "id": created.id,
                "user_id": created.user_id,
                "message": created.message,
                "type": created.type,
                "is_read": created.is_read,
                "created_at": str(created.created_at)
            },
            room=str(created.user_id) 
        )

        return created
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/user/{user_id}")
async def get_notifications_by_user(
    user_id: int, 
    page: int = 1, 
    limit: int = 30, 
    db: AsyncSession = Depends(get_db)
    ):
    try:
        return await notification_crud.get_notifications_by_user(db, user_id, page, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{notification_id}")
async def get_notification_by_id(notification_id: int, db: AsyncSession = Depends(get_db)):
    try:
        notification = await notification_crud.get_notification_by_id(db, notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return notification
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{notification_id}/read")
async def mark_notification_as_read(notification_id: int, db: AsyncSession = Depends(get_db)):
    try:
        notification = await notification_crud.mark_notification_as_read(db, notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")

        await socket_manager.emit(
            "notification_read",
            {"notification_id": notification_id},
            room=str(notification.user_id)
        )

        return notification
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{notification_id}")
async def delete_notification(notification_id: int, db: AsyncSession = Depends(get_db)):
    try:
        notification = await notification_crud.delete_notification(db, notification_id)
        if not notification:
            raise HTTPException(status_code=404, detail="Notification not found")
        return notification
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/unread")
async def get_unread_notifications(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await notification_crud.get_unread_notifications(db, user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/unread/count")
async def count_unread_notifications(user_id: int, db: AsyncSession = Depends(get_db)):
    try:
        count = await notification_crud.count_unread_notifications(db, user_id)
        return {"user_id": user_id, "unread_count": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
