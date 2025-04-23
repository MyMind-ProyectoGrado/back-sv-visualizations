# app/crud/transcription.py

from sqlalchemy.orm import Session
from app.models.transcription import Transcription

def get_all_transcriptions(db: Session):
    return db.query(Transcription).all()

# Función para obtener un usuario por su ID
def get_transcription_by_id(db: Session, transcription_id: str):
    return db.query(Transcription).filter(Transcription.transcription_id == transcription_id).first()
