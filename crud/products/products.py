from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from models.products.products import Products
from schemas.products.products import ProductsSchema
from utils.slug import generate_unique_slug
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

def calc_payable_price(
    price: float,
    discount_type: str,
    discount_amount: Optional[float] = None
) -> float:
    if discount_type == "percentage" and discount_amount is not None and 0 < discount_amount <= 100:
        return price * (1 - discount_amount / 100)
    elif discount_type == "fixed" and discount_amount is not None and 0 < discount_amount <= price:
        return price - discount_amount
    else:
        return price

async def get_product_by_id(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(Products)
        .options(joinedload(Products.sub_categories))
        .where(Products.id == product_id)
    )
    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")

    category_id = (
        product.sub_categories.category_id
        if product.sub_categories and product.sub_categories.category_id
        else None
    )

    return {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "meta_title": product.meta_title,
        "meta_description": product.meta_description,
        "brand_id": product.brand_id,
        "vendor_id": product.vendor_id,
        "price": product.price,
        "payable_price": product.payable_price,
        "discount_type": product.discount_type.value if product.discount_type else None,
        "discount_amount": product.discount_amount,
        "is_active": product.is_active,
        "sub_category_id": product.sub_category_id,
        "category_id": category_id,
        "brand_id": product.brand_id,
        "vendor_id": product.vendor_id,
        "slug": product.slug,
        "images": product.images,
        "highligthed_image": product.highligthed_image,
        "total_stock": product.total_stock,
        "available_stock": product.available_stock,
        "quantity_sold": product.quantity_sold,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
    }


async def get_all_products(
    db: AsyncSession,
    page: int = 1,
    limit: int = 10,
    is_active: Optional[bool] = None
):
    
    try:
        base_query = select(Products).options(joinedload(Products.sub_categories))

        if is_active is not None:
            base_query = base_query.where(Products.is_active == is_active)

        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar_one()

        offset = (page - 1) * limit
        result = await db.execute(base_query.offset(offset).limit(limit))
        products = result.scalars().all()

        product_data = []
        for product in products:
            category_id = (
                product.sub_categories.category_id
                if product.sub_categories and product.sub_categories.category_id
                else None
            )
            product_data.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "meta_title": product.meta_title,
                "meta_description": product.meta_description,
                "price": product.price,
                "payable_price": product.payable_price,
                "discount_type": product.discount_type.value if product.discount_type else None,
                "discount_amount": product.discount_amount,
                "is_active": product.is_active,
                "sub_category_id": product.sub_category_id,
                "category_id": category_id,
                "brand_id": product.brand_id,
                "vendor_id": product.vendor_id,
                "slug": product.slug,
                "images": product.images,
                "highligthed_image": product.highligthed_image,
            })

        return {
            "data": product_data,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



async def create_product(
    db: AsyncSession,
    product_data: ProductsSchema,
    highligthed_image_path: Optional[str] = None,
    image_paths: Optional[List[str]] = None
):
    try:
        new_slug = await generate_unique_slug(db, product_data.name, Products)

        payable_price = calc_payable_price(
            product_data.price,
            product_data.discount_type.value,
            product_data.discount_amount
        )

        new_product = Products(
            name=product_data.name,
            description=product_data.description,
            meta_title=product_data.meta_title,
            meta_description=product_data.meta_description,
            price=product_data.price,
            payable_price=payable_price,
            discount_type=product_data.discount_type,
            discount_amount=product_data.discount_amount,
            slug=new_slug,
            is_active=product_data.is_active,
            sub_category_id=product_data.sub_category_id,
            brand_id=product_data.brand_id,
            vendor_id=product_data.vendor_id,
            highligthed_image=highligthed_image_path,
            images=image_paths or [],
        )

        db.add(new_product)
        await db.commit()
        await db.refresh(new_product)
        return new_product

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

async def update_product(
    db: AsyncSession,
    product_id: int,
    product_data: ProductsSchema,
    highligthed_image_path: Optional[str] = None,
    image_paths: Optional[List[str]] = None
):
    try:
        new_slug = await generate_unique_slug(db, product_data.name, Products)
        product = await get_product_by_id(db, product_id)

        payable_price = calc_payable_price(
            product_data.price,
            product_data.discount_type.value,
            product_data.discount_amount
        )

        product.name = product_data.name
        product.description = product_data.description
        product.meta_title = product_data.meta_title
        product.meta_description = product_data.meta_description
        product.price = product_data.price
        product.payable_price = payable_price
        product.discount_type = product_data.discount_type
        product.discount_amount = product_data.discount_amount
        product.is_active = product_data.is_active
        product.sub_category_id = product_data.sub_category_id
        product.brand_id = product_data.brand_id
        product.vendor_id = product_data.vendor_id
        product.slug = new_slug

        if highligthed_image_path:
            product.highligthed_image = highligthed_image_path
        if image_paths:
            product.images = image_paths

        await db.commit()
        await db.refresh(product)
        return product

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


async def get_products_by_vendor(
    db: AsyncSession, 
    vendor_id: int, 
    page: int = 1,
    limit: int = 10,
    is_active: Optional[bool] = None
):
    try:
        base_query = (
            select(Products)
            .options(joinedload(Products.sub_categories))
            .where(Products.vendor_id == vendor_id)
        )

        if is_active is not None:
            base_query = base_query.where(Products.is_active == is_active)

        total_query = select(func.count()).select_from(base_query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar_one()

        result = await db.execute(
            base_query.offset((page - 1) * limit).limit(limit)
        )
        products = result.scalars().all()

        product_data = []
        for product in products:
            category_id = (
                product.sub_categories.category_id
                if product.sub_categories and product.sub_categories.category_id
                else None
            )
            product_data.append({
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "meta_title": product.meta_title,
                "meta_description": product.meta_description,
                "price": product.price,
                "payable_price": product.payable_price,
                "discount_type": product.discount_type.value if product.discount_type else None,
                "discount_amount": product.discount_amount,
                "is_active": product.is_active,
                "sub_category_id": product.sub_category_id,
                "category_id": category_id,
                "brand_id": product.brand_id,
                "vendor_id": product.vendor_id,
                "slug": product.slug,
                "images": product.images,
                "highligthed_image": product.highligthed_image,
                "total_stock": product.total_stock,
                "available_stock": product.available_stock,
                "quantity_sold": product.quantity_sold,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
            })

        return {
            "data": product_data,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }

    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


async def update_product_by_vendor_id(
    db: AsyncSession,
    product_id: int,
    product_data: ProductsSchema,
    vendor_id: int,
    highligthed_image_path: Optional[str] = None,
    image_paths: Optional[List[str]] = None
):
    try:
        product = await get_product_by_id(db, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if product.vendor_id != vendor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You are not authorized to update this product"
            )

        new_slug = await generate_unique_slug(db, product_data.name, Products)

        payable_price = calc_payable_price(
            product_data.price,
            product_data.discount_type.value,
            product_data.discount_amount
        )

        product.name = product_data.name
        product.description = product_data.description
        product.meta_title = product_data.meta_title
        product.meta_description = product_data.meta_description
        product.price = product_data.price
        product.payable_price = payable_price
        product.discount_type = product_data.discount_type
        product.discount_amount = product_data.discount_amount
        product.slug = new_slug
        product.is_active = product_data.is_active
        product.sub_category_id = product_data.sub_category_id
        product.brand_id = product_data.brand_id

        if highligthed_image_path:
            product.highligthed_image = highligthed_image_path
        if image_paths:
            product.images = image_paths

        await db.commit()
        await db.refresh(product)
        return product

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")