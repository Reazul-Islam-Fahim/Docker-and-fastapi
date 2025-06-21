from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import  Optional
from database.db import get_db
from schemas.inventory.inventory import InventorySchema
from crud.inventory.inventory import (
    create_inventory,
    get_all_inventories,
    get_inventory_by_id,
    update_inventory,
    delete_inventory,
)

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.post("")
async def create(data: InventorySchema, db: AsyncSession = Depends(get_db)):
    return await create_inventory(db, data)

@router.get("")
async def read_all(
    page: int = 0,
    limit: int = 10,
    product_id: Optional[int] = Query(None),
    vendor_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await get_all_inventories(db, page, limit, product_id, vendor_id)

@router.get("/{inventory_id}")
async def read_one(inventory_id: int, db: AsyncSession = Depends(get_db)):
    return await get_inventory_by_id(db, inventory_id)

@router.put("/{inventory_id}")
async def update(inventory_id: int, data: InventorySchema, db: AsyncSession = Depends(get_db)):
    return await update_inventory(db, inventory_id, data)

@router.delete("/{inventory_id}")
async def delete(inventory_id: int, db: AsyncSession = Depends(get_db)):
    return await delete_inventory(db, inventory_id)
