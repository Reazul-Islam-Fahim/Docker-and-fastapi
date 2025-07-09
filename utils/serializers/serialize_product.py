from models.products.products import Products

def serialize_product(product: Products) -> dict:
    return {
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
        "category_id": (
            product.sub_categories.category_id
            if product.sub_categories and product.sub_categories.category_id
            else None
        ),
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
        "product_specific_features": [
            {
                "id": f.id,
                "name": f.name,
                "unit": f.unit,
                "value": f.value
            }
            for f in product.product_specific_features
        ],
    }

