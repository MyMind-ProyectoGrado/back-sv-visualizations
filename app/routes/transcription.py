from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from app.models import transcription as models
from app.schemas.transcription import TranscriptionOut, TranscriptionSummary, TranscriptionSummary2
from app.core.database import get_db
from app.crud import transcription as crud_transcription
from app.core.auth import get_current_user
import jwt


router = APIRouter()


# Dependency para extraer user_id desde el token
async def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token faltante o inválido")

    token = auth_header.split(" ")[1]
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Estructura de token inválida")
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Formato de token inválido")


# 🔹 Transcripciones de todos los usuarios (si eres admin, por ejemplo)
@router.get("/transcriptions", response_model=list[TranscriptionOut])
def read_transcriptions(db: Session = Depends(get_db)):
    print("🔍 Entrando al endpoint /transcriptions")
    trans = crud_transcription.get_all_transcriptions(db)
    print("✅ Transcripciones obtenidas:", trans)
    return trans


# 🔹 Transcripciones del usuario autenticado en los últimos 7 días
@router.get("/transcriptions/ultimos-7-dias", response_model=list[TranscriptionSummary2])
async def get_last_7_days_transcriptions(
    user_id: str = Depends(get_current_user),
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

    # Convertir los resultados a la estructura resumida
    return [
        TranscriptionSummary2(
            transcription_id=r.id,
            transcription_date=r.transcription_date,
            transcription_time=r.transcription_time,
            emotion=r.emotion,
            sentiment=r.sentiment,
            emotion_probs_joy=r.emotion_probs_joy,
            emotion_probs_anger=r.emotion_probs_anger,
            emotion_probs_sadness=r.emotion_probs_sadness,
            emotion_probs_disgust=r.emotion_probs_disgust,
            emotion_probs_fear=r.emotion_probs_fear,
            emotion_probs_neutral=r.emotion_probs_neutral,
            emotion_probs_surprise=r.emotion_probs_surprise,
            emotion_probs_trust=r.emotion_probs_trust,
            emotion_probs_anticipation=r.emotion_probs_anticipation,
            sentiment_probs_positive=r.sentiment_probs_positive,
            sentiment_probs_negative=r.sentiment_probs_negative,
            sentiment_probs_neutral=r.sentiment_probs_neutral,
        )
        for r in results
    ]


# 🔹 Todas las transcripciones del usuario autenticado
@router.get("/transcriptions/user", response_model=list[TranscriptionSummary])
async def get_transcriptions_by_user(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = (
        db.query(models.Transcription)
        .filter(models.Transcription.user_id == user_id)
        .order_by(models.Transcription.transcription_date.desc())
        .all()
    )

    # Extraer solo los campos necesarios (ID, fecha, hora)
    summaries = [
        TranscriptionSummary(
            transcription_id=t.id,
            transcription_date=t.transcription_date,
            transcription_time=t.transcription_date.time()
        )
        for t in results
    ]

    return summaries



# 🔹 Última transcripción del usuario autenticado (fecha + hora)
@router.get("/transcriptions/user/latest", response_model=TranscriptionSummary2)
async def get_latest_transcription_by_user(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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

    # Construir el objeto con solo los campos deseados
    return TranscriptionSummary2(
        transcription_id=result.id,
        transcription_date=result.transcription_date,
        transcription_time=result.transcription_time,
        emotion=result.emotion,
        sentiment=result.sentiment,
        emotion_probs_joy=result.emotion_probs_joy,
        emotion_probs_anger=result.emotion_probs_anger,
        emotion_probs_sadness=result.emotion_probs_sadness,
        emotion_probs_disgust=result.emotion_probs_disgust,
        emotion_probs_fear=result.emotion_probs_fear,
        emotion_probs_neutral=result.emotion_probs_neutral,
        emotion_probs_surprise=result.emotion_probs_surprise,
        emotion_probs_trust=result.emotion_probs_trust,
        emotion_probs_anticipation=result.emotion_probs_anticipation,
        sentiment_probs_positive=result.sentiment_probs_positive,
        sentiment_probs_negative=result.sentiment_probs_negative,
        sentiment_probs_neutral=result.sentiment_probs_neutral,
    )
