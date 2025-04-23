from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserOut
from app.core.database import get_db

router = APIRouter()

@router.get("/users", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    # Consulta todos los usuarios
    users = db.query(User).all()
    return users
