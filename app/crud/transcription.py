# app/crud/transcription.py

from sqlalchemy.orm import Session
from app.models.transcription import Transcription

def get_all_transcriptions(db: Session):
    return db.query(Transcription).all()

