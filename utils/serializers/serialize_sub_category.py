from models.sub_categories.sub_categories import SubCategories

def serialize_sub_category(sc: SubCategories) -> dict:
    return {
        "id": sc.id,
        "category_id": sc.category_id,
        "name": sc.name,
        "description": sc.description,
        "meta_title": sc.meta_title,
        "meta_description": sc.meta_description,
        "image": sc.image,
        "feature_ids": [f.id for f in sc.product_features],
        "is_active": sc.is_active,
        "created_at": getattr(sc, "created_at", None)  # in case created_at is not always loaded
    }
