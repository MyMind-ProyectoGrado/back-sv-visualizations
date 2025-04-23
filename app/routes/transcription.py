from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta, timezone
from app.models import transcription as models
from app.schemas.transcription import TranscriptionOut
from app.core.database import get_db
from app.crud import transcription as crud_transcription

router = APIRouter()


@router.get("/transcriptions", response_model=list[TranscriptionOut])
def read_transcriptions(db: Session = Depends(get_db)):
    print("🔍 Entrando al endpoint /transcriptions")
    trans = crud_transcription.get_all_transcriptions(db)
    print("✅ Transcripciones obtenidas:", trans)
    return trans


@router.get("/transcriptions/ultimos-7-dias", response_model=list[TranscriptionOut])
def get_last_7_days_transcriptions(db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=7)
    yesterday = today - timedelta(days=1)

    print(f"🧪 Rango de fechas: {seven_days_ago} → {yesterday}")

    results = (
        db.query(models.Transcription)
        .filter(func.date(models.Transcription.transcription_date) >= seven_days_ago)
        .filter(func.date(models.Transcription.transcription_date) <= yesterday)
        .order_by(models.Transcription.transcription_date.asc())
        .all()
    )
    return results