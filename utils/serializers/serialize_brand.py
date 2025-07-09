def serialize_brand(brand):
    return {
        "id": brand.id,
        "name": brand.name,
        "description": brand.description,
        "image": brand.image,
        "is_active": brand.is_active
    }