from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, Query
from models.inventory.inventory import Inventory, InventoryTypeEnum
from schemas.inventory.inventory import InventorySchema
from sqlalchemy.orm import joinedload
from models.vendor.vendors import Vendors
from models.products.products import Products


async def create_inventory(db: AsyncSession, data: InventorySchema):
    try:
        # Step 1: Validate Product Exists
        product_query = await db.execute(select(Products).where(Products.id == data.product_id))
        product = product_query.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Step 2: Extract inventory type
        inv_type = data.inventory_type
        quantity = data.total_quantity

        # Step 3: Create Inventory Instance
        new_inventory = Inventory(
            unit_price=data.unit_price,
            total_quantity=quantity,
            total_price=data.unit_price * quantity,
            inventory_type=inv_type,
            invoice_number=data.invoice_number,
            notes=data.notes,
            product_id=data.product_id,
            vendor_id=data.vendor_id,
        )
        db.add(new_inventory)

        # Step 4: Update Product Fields Based on Inventory Type
        if inv_type in [InventoryTypeEnum.purchase, InventoryTypeEnum.returrn, InventoryTypeEnum.restock]:
            product.total_stock += quantity
            product.available_stock += quantity
        elif inv_type in [InventoryTypeEnum.sell, InventoryTypeEnum.damage, InventoryTypeEnum.adjustment]:
            if product.available_stock < quantity:
                raise HTTPException(status_code=400, detail="Insufficient available stock")
            product.available_stock -= quantity
            product.quantity_sold += quantity
        else:
            raise HTTPException(status_code=400, detail="Invalid inventory type")

        # Step 5: Commit Changes
        await db.commit()
        await db.refresh(new_inventory)

        print(f"Creating inventory for product_id={data.product_id} with type={data.inventory_type}")
        return new_inventory

    except HTTPException as e:
        print(f"HTTPException: {e.detail}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def get_all_inventories(
    db: AsyncSession,
    page: int = 0,
    limit: int = 10,
    product_id: int = Query(None),
    vendor_id: int = Query(None),
):
    query = select(Inventory).options(
        joinedload(Inventory.products),
        joinedload(Inventory.vendors).joinedload(Vendors.users),
    )

    if product_id:
        query = query.where(Inventory.product_id == product_id)
    if vendor_id:
        query = query.where(Inventory.vendor_id == vendor_id)

    result = await db.execute(query.offset(page * limit).limit(limit))
    return result.scalars().all()


async def get_inventory_by_id(db: AsyncSession, inventory_id: int):
    result = await db.execute(
        select(Inventory)
        .where(Inventory.id == inventory_id)
        .options(
            joinedload(Inventory.products),
            joinedload(Inventory.vendors),
        )
    )
    inventory = result.scalar_one_or_none()
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory

async def update_inventory(db: AsyncSession, inventory_id: int, data: InventorySchema):
    inventory = await get_inventory_by_id(db, inventory_id)
    
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    
    product_query = await db.execute(select(Products).where(Products.id == data.product_id))
    product = product_query.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    inv_type = data.inventory_type
    quantity = data.total_quantity
     
    inventory.unit_price = data.unit_price
    inventory.total_quantity = data.total_quantity
    inventory.total_price = data.unit_price * data.total_quantity
    inventory.inventory_type = data.inventory_type
    inventory.invoice_number = data.invoice_number
    inventory.notes = data.notes    
    
    if inv_type in [InventoryTypeEnum.purchase, InventoryTypeEnum.returrn, InventoryTypeEnum.restock]:
            product.total_stock += quantity
            product.available_stock += quantity
    elif inv_type in [InventoryTypeEnum.sell, InventoryTypeEnum.damage, InventoryTypeEnum.adjustment]:
        if product.available_stock < quantity:
            raise HTTPException(status_code=400, detail="Insufficient available stock")
        product.available_stock -= quantity
        product.quantity_sold += quantity
    else:
        raise HTTPException(status_code=400, detail="Invalid inventory type")
        
    await db.commit()
    await db.refresh(inventory)
    return inventory

async def delete_inventory(db: AsyncSession, inventory_id: int):
    inventory = await get_inventory_by_id(db, inventory_id)
    await db.delete(inventory)
    await db.commit()
    return {"message": "Inventory deleted successfully"}
