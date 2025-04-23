from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.schemas.transcription import TranscriptionOut
from app.crud import transcription as crud_transcription
from app.core.database import SessionLocal
from app.models.user import User



router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



@router.get("/transcriptions", response_model=list[TranscriptionOut])
def read_transcriptions(db: Session = Depends(get_db)):
    print("🔍 Entrando al endpoint /transcriptions")
    trans = crud_transcription.get_all_transcriptions(db)
    print("✅ Transcripciones obtenidas:", trans)
    return trans
