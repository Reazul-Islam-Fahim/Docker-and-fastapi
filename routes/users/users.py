from typing import Optional
from fastapi import APIRouter, Form, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from models.users.users import genders
from crud.users.users import get_user, get_users, update_user
from database.db import get_db
from schemas.users.users import UpdateUserSchema
from utils.save_files import save_file, UPLOAD_DIR as upload_dir
from datetime import datetime
import os

router = APIRouter(prefix="/users", tags=["Users"])

# Create users-specific upload folder
UPLOAD_DIR = os.path.join(upload_dir, "users")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.get("")
async def get_all_users(
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(30, ge=1),
    search: Optional[str] = None,
    user_id: Optional[int] = None,
    status: Optional[bool] = None,
    created_from: Optional[datetime] = Query(None),
    created_to: Optional[datetime] = Query(None),
    sort_by: str = Query("created_at", enum=["created_at", "name"]),
    sort_order: str = Query("desc", enum=["asc", "desc"])
):
    return await get_users(
        db=db,
        page=page,
        limit=limit,
        search=search,
        user_id=user_id,
        status=status,
        created_from=created_from,
        created_to=created_to,
        sort_by=sort_by,
        sort_order=sort_order
    )


@router.get("/{user_id}")
async def get_user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}")
async def patch_user_info(
    user_id: int,
    name: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    dob: Optional[str] = Form(None),
    gender: Optional[genders] = Form(None),
    image: Optional[UploadFile] = File(None),
    db: AsyncSession = Depends(get_db)
):
    user_data = UpdateUserSchema(
        name=name,
        phone=phone,
        dob=dob,
        gender=gender
    )

    file_path = None
    if image:
        try:
            file_path = save_file(image, folder=UPLOAD_DIR)
        finally:
            await image.close()

    return await update_user(db, user_id, user_data, file_path)
