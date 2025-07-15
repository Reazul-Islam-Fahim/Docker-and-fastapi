from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.user_addresses.user_addresses import UserAddressesSchema
from crud.user_addresses.user_addresses import (
    create_user_address,
    get_user_addresses_by_user_id,
    get_user_address_by_id,
    update_user_address,
    set_default_address
)
from database.db import get_db

router = APIRouter(prefix="/user-addresses", tags=["User Addresses"])

@router.post("")
async def create_address(
    address_data: UserAddressesSchema,
    db: AsyncSession = Depends(get_db)
):
    return await create_user_address(db, address_data)


@router.get("/user/{user_id}")
async def get_addresses_by_user_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
):
    return await get_user_addresses_by_user_id(db, user_id)


@router.get("/{address_id}")
async def get_address_by_id(
    address_id: int,
    db: AsyncSession = Depends(get_db)
):
    address = await get_user_address_by_id(db, address_id)
    if not address:
        raise HTTPException(status_code=404, detail="Address not found")
    return address


@router.put("/{address_id}")
async def update_address(
    address_id: int,
    address_data: UserAddressesSchema,
    db: AsyncSession = Depends(get_db)
):
    updated = await update_user_address(db, address_id, address_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Address not found")
    return updated


@router.post("/{user_id}/set-default/{address_id}")
async def set_default_user_address(
    user_id: int,
    address_id: int,
    db: AsyncSession = Depends(get_db)
):
    success = await set_default_address(db, user_id, address_id)
    if success:
        return {"message": "Default address updated successfully"}
    raise HTTPException(status_code=400, detail="Could not set default address")
