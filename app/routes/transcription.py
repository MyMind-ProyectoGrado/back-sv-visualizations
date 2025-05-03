from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, timezone
from app.models import transcription as models
from app.schemas.transcription import TranscriptionOut, TranscriptionSummary, TranscriptionSummary2, TranscriptionAverages, TrancriptionTop3
from app.core.database import get_db
from app.crud import transcription as crud_transcription
from app.core.auth import get_current_user
import jwt
from operator import itemgetter


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


# 🔹 Promedio de transcripciones del usuario autenticado en los últimos 7 días
@router.get("/transcriptions/user/last-7-days", response_model=TranscriptionAverages)
async def get_last_7_days_transcriptions_average(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=7)
    yesterday = today - timedelta(days=1)

    results = (
        db.query(models.Transcription)
        .filter(models.Transcription.user_id == user_id)
        .filter(func.date(models.Transcription.transcription_date) >= seven_days_ago)
        .filter(func.date(models.Transcription.transcription_date) <= yesterday)
        .order_by(models.Transcription.transcription_date.asc())
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail="No hay transcripciones en los últimos 7 días")

    # Calcular promedios
    total = len(results)
    avg_emotions = {
        "emotion_probs_joy": sum(r.emotion_probs_joy for r in results) / total,
        "emotion_probs_anger": sum(r.emotion_probs_anger for r in results) / total,
        "emotion_probs_sadness": sum(r.emotion_probs_sadness for r in results) / total,
        "emotion_probs_disgust": sum(r.emotion_probs_disgust for r in results) / total,
        "emotion_probs_fear": sum(r.emotion_probs_fear for r in results) / total,
        "emotion_probs_neutral": sum(r.emotion_probs_neutral for r in results) / total,
        "emotion_probs_surprise": sum(r.emotion_probs_surprise for r in results) / total,
        "emotion_probs_trust": sum(r.emotion_probs_trust for r in results) / total,
        "emotion_probs_anticipation": sum(r.emotion_probs_anticipation for r in results) / total,
        "sentiment_probs_positive": sum(r.sentiment_probs_positive for r in results) / total,
        "sentiment_probs_negative": sum(r.sentiment_probs_negative for r in results) / total,
        "sentiment_probs_neutral": sum(r.sentiment_probs_neutral for r in results) / total,
    }

    return TranscriptionAverages(**avg_emotions)


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
            transcription_id=t.transcription_id,
            transcription_date=t.transcription_date,
            transcription_time=t.transcription_time
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
        transcription_id=result.transcription_id,
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

@router.get("/transcriptions/user/last-week/top-emotions-sentiments", response_model=TrancriptionTop3)
async def get_top_emotions_and_sentiments(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=7)
    yesterday = today - timedelta(days=1)

    results = (
        db.query(models.Transcription)
        .filter(models.Transcription.user_id == user_id)
        .filter(func.date(models.Transcription.transcription_date) >= seven_days_ago)
        .filter(func.date(models.Transcription.transcription_date) <= yesterday)
        .order_by(models.Transcription.transcription_date.asc())
        .all()
    )

    if not results:
        raise HTTPException(status_code=404, detail="No hay transcripciones en los últimos 7 días")

    # Calcular promedios
    total = len(results)
    avg_emotions = {
        "joy": sum(r.emotion_probs_joy for r in results) / total,
        "anger": sum(r.emotion_probs_anger for r in results) / total,
        "sadness": sum(r.emotion_probs_sadness for r in results) / total,
        "disgust": sum(r.emotion_probs_disgust for r in results) / total,
        "fear": sum(r.emotion_probs_fear for r in results) / total,
        "neutral": sum(r.emotion_probs_neutral for r in results) / total,
        "surprise": sum(r.emotion_probs_surprise for r in results) / total,
        "trust": sum(r.emotion_probs_trust for r in results) / total,
        "anticipation": sum(r.emotion_probs_anticipation for r in results) / total,
    }

    avg_sentiments = {
        "positive": sum(r.sentiment_probs_positive for r in results) / total,
        "negative": sum(r.sentiment_probs_negative for r in results) / total,
        "neutral": sum(r.sentiment_probs_neutral for r in results) / total,
    }

    # Obtener las 3 emociones con mayor valor
    top_emotions = sorted(avg_emotions.items(), key=itemgetter(1), reverse=True)[:3]
    top_sentiments = sorted(avg_sentiments.items(), key=itemgetter(1), reverse=True)[:1]  # Solo el top 1 sentimiento

    # Preparar la respuesta con el esquema solicitado
    return TrancriptionTop3(
        emotion_probs_top1=f"{top_emotions[0][0]}",
        emotion_probs_top2=f"{top_emotions[1][0]}",
        emotion_probs_top3=f"{top_emotions[2][0]}",
        sentiment_probs_top1=f"{top_sentiments[0][0]}"
    )
