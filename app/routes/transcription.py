from fastapi import APIRouter, Depends,  HTTPException, Path
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

@router.get("/transcriptions/user/{user_id}", response_model=list[TranscriptionOut])
def get_transcriptions_by_user(user_id: str, db: Session = Depends(get_db)):
    results = (
        db.query(models.Transcription)
        .filter(models.Transcription.user_id == user_id)
        .order_by(models.Transcription.transcription_date.desc())
        .all()
    )
    return results



@router.get("/transcriptions/user/{user_id}/latest", response_model=TranscriptionOut)
def get_latest_transcription_by_user(user_id: str, db: Session = Depends(get_db)):
    result = (
        db.query(models.Transcription)
        .filter(models.Transcription.user_id == user_id)
        .order_by(
            models.Transcription.transcription_date.desc(),
            models.Transcription.transcription_time.desc()
        )
        .first()
    )

    if result is None:
        raise HTTPException(status_code=404, detail="No se encontró ninguna transcripción para este usuario")

    return result



@router.get("/transcriptions/user/{user_id}/ultimos-7-dias", response_model=list[TranscriptionOut])
def get_last_7_days_transcriptions_by_user(
    user_id: str = Path(..., description="ID del usuario"),
    db: Session = Depends(get_db)
):
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=7)
    yesterday = today - timedelta(days=1)

    print(f"🧪 Rango de fechas para usuario {user_id}: {seven_days_ago} → {yesterday}")

    results = (
        db.query(models.Transcription)
        .filter(models.Transcription.user_id == user_id)
        .filter(func.date(models.Transcription.transcription_date) >= seven_days_ago)
        .filter(func.date(models.Transcription.transcription_date) <= yesterday)
        .order_by(models.Transcription.transcription_date.asc())
        .all()
    )

    return results

