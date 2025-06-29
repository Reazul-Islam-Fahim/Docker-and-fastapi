from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from models.sub_categories.sub_categories import SubCategories
from models.categories.categories import Categories
from schemas.categories.categories import CategoriesSchema
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import selectinload
from models.products.products import Products
from models.sub_categories.sub_categories import SubCategories
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload
from typing import Optional

async def get_products_by_category_id(db: AsyncSession, category_id: int):
    try:
        result = await db.execute(
            select(Products)
            .join(SubCategories)
            .where(SubCategories.category_id == category_id)
            .options(joinedload(Products.sub_categories))
        )
        products = result.scalars().all()

        return [
            {
                "id": p.id,
                "name": p.name,
                "description": p.description,
                "meta_title": p.meta_title,
                "meta_description": p.meta_description,
                "brand_id": p.brand_id,
                "vendor_id": p.vendor_id,
                "price": p.price,
                "payable_price": p.payable_price,
                "available_stock": p.available_stock,
                "discount_type": p.discount_type,
                "discount_amount": p.discount_amount,
                "images": p.images,
                "highlighted_image": p.highligthed_image,
                "is_active": p.is_active,
                "created_at": p.created_at,
                "subcategory_id": p.sub_category_id
            }
            for p in products
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")



async def get_category_by_id(db: AsyncSession, id: int):
    result = await db.execute(
        select(Categories).where(Categories.id == id).options(selectinload(Categories.sub_categories))
    )
    db_category = result.scalar_one_or_none()

    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    return db_category  


# Get all Categories with the sub-categories
async def get_all_categories(
    db: AsyncSession,
    page: int = 1,
    limit: int = 20,
    is_active: Optional[bool] = None
):
    page = max(page, 1)
    limit = max(limit, 1)
    offset = (page - 1) * limit
    query = select(Categories).options(selectinload(Categories.sub_categories))

    if is_active is not None:
        query = query.where(Categories.is_active == is_active)

    total_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = total_result.scalar()

    result = await db.execute(
        query.offset(offset).limit(limit)
    )

    categories = result.scalars().all()

    return {
        "data": [
            {
                "id": c.id,
                "name": c.name,
                "description": c.description,
                "meta_title": c.meta_title,
                "meta_description": c.meta_description,
                "is_active": c.is_active,
                "image": c.image,
                "created_at": c.created_at,
                "sub_categories": [
                    {
                        "id": sub.id,
                        "name": sub.name,
                        "image": sub.image,
                        "created_at": sub.created_at,
                    }
                    for sub in c.sub_categories
                ]
            }
            for c in categories
        ],
        "meta": {
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit
        }
    }

# Get all sub-Categories by categories id
async def get_sub_category_by_category_id(db: AsyncSession, category_id: int):
    try:
        result = await db.execute(
            select(SubCategories).where(SubCategories.category_id == category_id)
        )
        sub_categories = result.scalars().all()

        if not sub_categories:
            raise HTTPException(status_code=404, detail="No subcategories found for this category.")

        return sub_categories

    except HTTPException:
        raise

    except Exception as e:
        print("DB Error:", e)
        raise HTTPException(status_code=500, detail="Error retrieving subcategories.")

# Update Categories
async def update_category(
    db: AsyncSession,
    id: int,
    category_data: CategoriesSchema,
    filePath: str
):
    try:
        result = await db.execute(select(Categories).where(Categories.id == id))
        db_category = result.scalar_one_or_none()

        if not db_category:
            raise HTTPException(status_code=404, detail="Category not found")

        db_category.name = category_data.name
        db_category.description = category_data.description
        db_category.is_active = category_data.is_active
        db_category.meta_title = category_data.meta_title
        db_category.meta_description = category_data.meta_description
        db_category.image = filePath

        await db.commit()
        await db.refresh(db_category)

        category_response = {
            "name": db_category.name,
            "image": db_category.image,
            "description": db_category.description,
            "is_active": db_category.is_active,
            "meta_title": db_category.meta_title,
            "meta_description": db_category.meta_description
        }

        return category_response

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )

# Create Categories
async def create_category(
    db: AsyncSession,
    category_data: CategoriesSchema,
    file_path: Optional[str] = None
):
    try:
        result = await db.execute(
            select(Categories).where(Categories.name == category_data.name)
        )
        existing_category = result.scalar_one_or_none()

        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category with this name already exists"
            )

        new_category = Categories(
            name=category_data.name,
            description=category_data.description,
            meta_title=category_data.meta_title,
            meta_description=category_data.meta_description,
            is_active=category_data.is_active,
            image=file_path
        )

        db.add(new_category)
        await db.commit()
        await db.refresh(new_category)

        return new_category

    except SQLAlchemyError as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )