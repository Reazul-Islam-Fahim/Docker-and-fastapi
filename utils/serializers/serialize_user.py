from models.users.users import Users


def serialize_user(user: Users) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "dob": user.dob,
        "gender": getattr(user, "gender", None),
        "image": user.image,
        "role": user.role,
        "status": getattr(user, "is_active", None),
        "isActive": getattr(user, "is_active", None),
        "created_at": getattr(user, "created_at", None),
    }
