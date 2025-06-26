from sqlalchemy.future import select
from sqlalchemy import or_, func
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from models.products.products import Products

async def search_products(
    db: AsyncSession,
    q: str,
    brand_id: int = None,
    subcategory_id: int = None,
    min_price: float = None,
    max_price: float = None,
    sort_by: str = None,
    order: str = "asc",
    page: int = 1,
    limit: int = 20,
):
    # Start building the query
    query = select(Products).options(
        joinedload(Products.brands),
        joinedload(Products.sub_categories)
    )

    if len(q) >= 3:
        q_like = f"%{q.lower()}%"
        query = query.where(
            or_(
                Products.name.ilike(q_like),
                Products.slug.ilike(q_like),
                Products.description.ilike(q_like)
            )
        )

    query = query.where(
        Products.is_active == True,
        Products.available_stock > 0
    )

    if brand_id:
        query = query.where(Products.brand_id == brand_id)
    if subcategory_id:
        query = query.where(Products.subcategory_id == subcategory_id)
    if min_price is not None:
        query = query.where(Products.payable_price >= min_price)
    if max_price is not None:
        query = query.where(Products.payable_price <= max_price)

    sort_column = {
        "price": Products.payable_price,
        "name": Products.name
    }.get(sort_by, Products.id)

    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())

    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)

    result = await db.execute(query.offset((page - 1) * limit).limit(limit))
    products = result.unique().scalars().all()

    return total or 0, products
