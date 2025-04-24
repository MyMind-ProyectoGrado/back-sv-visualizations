from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserOut
from app.core.database import get_db
from app.core.auth import get_current_user
from fastapi import HTTPException
router = APIRouter()

@router.get("/users", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    # Consulta todos los usuarios
    users = db.query(User).all()
    return users

@router.get("/users/me", response_model=UserOut)
async def get_current_user_info(db: Session = Depends(get_db), user_id: str = Depends(get_current_user)):
    """Ruta que devuelve la información del usuario actual."""
    # Buscamos el usuario en la base de datos con el user_id extraído del token
    user = db.query(User).filter(User.user_id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user