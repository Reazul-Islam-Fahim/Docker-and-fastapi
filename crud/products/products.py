from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from models.products.products import Products
from models.sub_categories.sub_categories import SubCategories
from schemas.products.products import ProductsSchema
from utils.slug import generate_unique_slug
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError
from models.product_features.product_features import ProductFeatures
from sqlalchemy.orm import joinedload, selectinload


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


async def create_product(
    db: AsyncSession,
    product_data: ProductsSchema,
    highlighted_image_path: Optional[str] = None,
    image_paths: Optional[List[str]] = None
):
    try:
        new_slug = await generate_unique_slug(db, product_data.name, Products)

        payable_price = calc_payable_price(
            product_data.price,
            product_data.discount_type.value if product_data.discount_type else None,
            product_data.discount_amount
        )

        features = []
        if product_data.product_specific_features:
            result = await db.execute(
                select(ProductFeatures).where(ProductFeatures.id.in_(product_data.product_specific_features))
            )
            features = result.scalars().all()

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
            highlighted_image=highlighted_image_path,
            images=image_paths or [],
            product_specific_features=features
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


async def get_product_by_id(db: AsyncSession, product_id: int):
    result = await db.execute(
        select(Products)
        .options(
            joinedload(Products.sub_categories),
            joinedload(Products.product_specific_features)
        )
        .where(Products.id == product_id)
    )
    product = result.unique().scalar_one_or_none()

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
        "slug": product.slug,
        "images": product.images,
        "highlighted_image": product.highlighted_image,
        "total_stock": product.total_stock,
        "available_stock": product.available_stock,
        "quantity_sold": product.quantity_sold,
        "created_at": product.created_at,
        "updated_at": product.updated_at,
        "product_specific_features": [feature.id for feature in product.product_specific_features],
    }


# This function applies filters to the product query based on the provided conditions.
def apply_product_filters(query, filters):
    for condition in filters:
        query = query.where(condition)
    return query

async def get_all_products(
    db: AsyncSession,
    page: int,
    limit: int,
    is_active: Optional[bool] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    meta_title: Optional[str] = None,
    meta_description: Optional[str] = None,
    sub_category_id: Optional[int] = None,
    category_id: Optional[int] = None,
    brand_id: Optional[int] = None,
    vendor_id: Optional[int] = None,
    discount_type: Optional[str] = None,
    product_feature_name: Optional[str] = None,
):
    try:
        filters = []

        if is_active is not None:
            filters.append(Products.is_active == is_active)
        if name:
            filters.append(Products.name.ilike(f"%{name}%"))
        if description:
            filters.append(Products.description.ilike(f"%{description}%"))
        if meta_title:
            filters.append(Products.meta_title.ilike(f"%{meta_title}%"))
        if meta_description:
            filters.append(Products.meta_description.ilike(f"%{meta_description}%"))
        if sub_category_id:
            filters.append(Products.sub_category_id == sub_category_id)
        if category_id:
            filters.append(Products.sub_categories.has(SubCategories.category_id == category_id))
        if brand_id:
            filters.append(Products.brand_id == brand_id)
        if vendor_id:
            filters.append(Products.vendor_id == vendor_id)
        if discount_type:
            filters.append(Products.discount_type == discount_type)
        if product_feature_name:
            filters.append(
                Products.product_specific_features.any(
                    ProductFeatures.name.ilike(f"%{product_feature_name}%")
                )
            )

        query = select(Products).options(
            joinedload(Products.sub_categories),
            selectinload(Products.product_specific_features)
        )

        query = apply_product_filters(query, filters)

        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar_one()

        offset = (page - 1) * limit
        result = await db.execute(query.offset(offset).limit(limit))
        products = result.unique().scalars().all()

        data = []
        for product in products:
            category_id_value = (
                product.sub_categories.category_id
                if product.sub_categories and product.sub_categories.category_id
                else None
            )

            data.append({
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
                "category_id": category_id_value,
                "brand_id": product.brand_id,
                "vendor_id": product.vendor_id,
                "slug": product.slug,
                "images": product.images,
                "highlighted_image": product.highlighted_image,
                "product_specific_features": [
                    {"id": f.id, "name": f.name, "unit": f.unit, "value": f.value}
                    for f in product.product_specific_features
                ],
            })

        return {
            "data": data,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving products: {str(e)}")


async def get_products_by_vendor(
    db: AsyncSession,
    vendor_id: int,
    page: int = 1,
    limit: int = 10,
    is_active: Optional[bool] = None
):
    try:
        query = (
            select(Products)
            .options(
                joinedload(Products.sub_categories),
                joinedload(Products.product_specific_features)
            )
            .where(Products.vendor_id == vendor_id)
        )

        if is_active is not None:
            query = query.where(Products.is_active == is_active)

        total_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(total_query)
        total = total_result.scalar_one()

        result = await db.execute(query.offset((page - 1) * limit).limit(limit))
        products = result.scalars().all()

        data = []
        for product in products:
            category_id = (
                product.sub_categories.category_id
                if product.sub_categories and product.sub_categories.category_id
                else None
            )

            data.append({
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
                "highlighted_image": product.highlighted_image,
                "total_stock": product.total_stock,
                "available_stock": product.available_stock,
                "quantity_sold": product.quantity_sold,
                "created_at": product.created_at,
                "updated_at": product.updated_at,
                "product_specific_features": [f.id for f in product.product_specific_features],
            })

        return {
            "data": data,
            "meta": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving vendor products: {str(e)}")


async def update_product_by_vendor_id(
    db: AsyncSession,
    product_id: int,
    product_data: ProductsSchema,
    vendor_id: int,
    highlighted_image_path: Optional[str] = None,
    image_paths: Optional[List[str]] = None
):
    try:
        result = await db.execute(
            select(Products)
            .where(Products.id == product_id)
            .options(joinedload(Products.product_specific_features))
        )
        product = result.scalar_one_or_none()

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
            product_data.discount_type.value if product_data.discount_type else None,
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

        if highlighted_image_path:
            product.highlighted_image = highlighted_image_path
        if image_paths:
            product.images = image_paths

        if product_data.product_specific_features is not None:
            result = await db.execute(
                select(ProductFeatures).where(ProductFeatures.id.in_(product_data.product_specific_features))
            )
            product.product_specific_features.clear()  # ✅ Prevent duplication
            product.product_specific_features = result.scalars().all()

        await db.commit()
        await db.refresh(product)
        return product

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


async def update_product_by_id(
    db: AsyncSession,
    product_id: int,
    product_data: ProductsSchema,
    highlighted_image_path: Optional[str] = None,
    image_paths: Optional[List[str]] = None
):
    try:
        result = await db.execute(
            select(Products)
            .where(Products.id == product_id)
            .options(joinedload(Products.product_specific_features))
        )
        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        new_slug = await generate_unique_slug(db, product_data.name, Products)

        payable_price = calc_payable_price(
            product_data.price,
            product_data.discount_type.value if product_data.discount_type else None,
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
        product.vendor_id = product_data.vendor_id

        if highlighted_image_path:
            product.highlighted_image = highlighted_image_path
        if image_paths:
            product.images = image_paths

        if product_data.product_specific_features is not None:
            result = await db.execute(
                select(ProductFeatures).where(ProductFeatures.id.in_(product_data.product_specific_features))
            )
            product.product_specific_features.clear()  # ✅ Prevent duplication
            product.product_specific_features = result.scalars().all()

        await db.commit()
        await db.refresh(product)
        return product

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
