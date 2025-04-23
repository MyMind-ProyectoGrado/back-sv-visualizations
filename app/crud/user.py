from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserOut

# Función para obtener todos los usuarios
def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(User).offset(skip).limit(limit).all()

# Función para obtener un usuario por su ID
def get_user_by_id(db: Session, user_id: str):
    return db.query(User).filter(User.user_id == user_id).first()
