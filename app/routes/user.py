from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.schemas.user import UserOut
from app.core.database import get_db  # Aquí usaremos get_db para acceder a la DB
from app.core.auth import get_current_user

router = APIRouter()

# 🔹 Obtener todos los usuarios
@router.get("/users", response_model=list[UserOut])
def get_users(db = Depends(get_db)):  # db será la dependencia que se conecta a MongoDB
    # Consultar todos los usuarios
    users = db.users.find()  # Usamos la colección 'users' de la base de datos
    return [UserOut(**user) for user in users]  # Convertimos los resultados a los modelos UserOut

# 🔹 Obtener el usuario actual
@router.get("/users/me", response_model=UserOut)
async def get_current_user_info(db = Depends(get_db), user_id: str = Depends(get_current_user)):
    """Ruta que devuelve la información del usuario actual."""
    # Buscar el usuario en la base de datos usando el user_id
    user = db.users.find_one({"user_id": user_id})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserOut(**user)  # Convertir el resultado a un modelo Pydantic UserOut
