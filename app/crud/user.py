from typing import List, Optional
from pymongo import ASCENDING
from app.models.user import User  # si lo necesitas para validación
from app.schemas.user import UserOut  # opcional, si quieres usar Pydantic

# 🔹 Obtener todos los usuarios con paginación
async def get_users(db, skip: int = 0, limit: int = 10) -> List[dict]:
    cursor = db.users.find().sort("user_id", ASCENDING).skip(skip).limit(limit)
    return await cursor.to_list(length=limit)

# 🔹 Obtener un usuario por ID
async def get_user_by_id(db, user_id: str) -> Optional[dict]:
    return await db.users.find_one({"_id": user_id})
