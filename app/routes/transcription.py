from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta, timezone
from app.core.database import get_mongo_collection
from app.core.auth import get_current_user
from app.schemas.transcription import TranscriptionOut, TranscriptionSummary, TranscriptionSummary2, TranscriptionAverages, TrancriptionTop3
from operator import itemgetter

router = APIRouter()

# 🔹 Transcripciones de todos los usuarios (para admin)
@router.get("/transcriptions", response_model=list[TranscriptionOut])
async def read_transcriptions(collection=Depends(get_mongo_collection)):
    print("🔍 Entrando al endpoint /transcriptions")
    trans = []
    async for user in collection.find({}):
        for t in user.get("transcriptions", []):
            trans.append(TranscriptionOut(
                _id=str(t["_id"]),  # Usamos el alias _id para id
                user_id=user["_id"],
                date=t["date"],
                time=t["time"],
                text=t["text"],
                emotion=t["emotion"],
                sentiment=t["sentiment"],
                emotionProbabilities=t["emotionProbabilities"],
                sentimentProbabilities=t["sentimentProbabilities"],
                topic=t.get("topic")
            ))
    print("✅ Transcripciones obtenidas:", trans)
    return trans

# 🔹 Promedio de transcripciones del usuario autenticado en los últimos 7 días
@router.get("/transcriptions/user/last-7-days", response_model=TranscriptionAverages)
async def get_last_7_days_transcriptions_average(
    user_id: str = Depends(get_current_user),
    collection=Depends(get_mongo_collection)
):
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=7)

    user = await collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    results = [
        t for t in user.get("transcriptions", [])
        if datetime.strptime(t["date"], "%Y-%m-%d").date() >= seven_days_ago
        and datetime.strptime(t["date"], "%Y-%m-%d").date() <= today
    ]

    if not results:
        raise HTTPException(status_code=404, detail="No hay transcripciones en los últimos 7 días")

    total = len(results)
    avg_emotions = {
        "emotion_probs_joy": sum(t["emotionProbabilities"]["joy"] for t in results) / total,
        "emotion_probs_anger": sum(t["emotionProbabilities"]["anger"] for t in results) / total,
        "emotion_probs_sadness": sum(t["emotionProbabilities"]["sadness"] for t in results) / total,
        "emotion_probs_disgust": sum(t["emotionProbabilities"]["disgust"] for t in results) / total,
        "emotion_probs_fear": sum(t["emotionProbabilities"]["fear"] for t in results) / total,
        "emotion_probs_neutral": sum(t["emotionProbabilities"]["neutral"] for t in results) / total,
        "emotion_probs_surprise": sum(t["emotionProbabilities"]["surprise"] for t in results) / total,
        "emotion_probs_trust": sum(t["emotionProbabilities"]["trust"] for t in results) / total,
        "emotion_probs_anticipation": sum(t["emotionProbabilities"]["anticipation"] for t in results) / total,
        "sentiment_probs_positive": sum(t["sentimentProbabilities"]["positive"] for t in results) / total,
        "sentiment_probs_negative": sum(t["sentimentProbabilities"]["negative"] for t in results) / total,
        "sentiment_probs_neutral": sum(t["sentimentProbabilities"]["neutral"] for t in results) / total,
    }

    return TranscriptionAverages(**avg_emotions)

# 🔹 Todas las transcripciones del usuario autenticado
@router.get("/transcriptions/user", response_model=list[TranscriptionSummary])
async def get_transcriptions_by_user(
    user_id: str = Depends(get_current_user),
    collection=Depends(get_mongo_collection)
):
    user = await collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    results = sorted(
        user.get("transcriptions", []),
        key=lambda x: datetime.strptime(x["date"], "%Y-%m-%d"),
        reverse=True
    )

    summaries = [
        TranscriptionSummary(
            transcription_id=str(t["_id"]),  # Coincide con el campo id de TranscriptionOut
            transcription_date=t["date"],
            transcription_time=t["time"]
        )
        for t in results
    ]

    return summaries

# 🔹 Última transcripción del usuario autenticado
@router.get("/transcriptions/user/latest", response_model=TranscriptionSummary2)
async def get_latest_transcription_by_user(
    user_id: str = Depends(get_current_user),
    collection=Depends(get_mongo_collection)
):
    user = await collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    results = user.get("transcriptions", [])
    if not results:
        raise HTTPException(status_code=404, detail="No se encontró ninguna transcripción para este usuario")

    result = max(
        results,
        key=lambda x: datetime.strptime(f"{x['date']} {x['time']}", "%Y-%m-%d %H:%M:%S")
    )

    return TranscriptionSummary2(
        transcription_id=str(result["_id"]),
        transcription_date=result["date"],
        transcription_time=result["time"],
        emotion=result["emotion"],
        sentiment=result["sentiment"],
        emotion_probs_joy=result["emotionProbabilities"]["joy"],
        emotion_probs_anger=result["emotionProbabilities"]["anger"],
        emotion_probs_sadness=result["emotionProbabilities"]["sadness"],
        emotion_probs_disgust=result["emotionProbabilities"]["disgust"],
        emotion_probs_fear=result["emotionProbabilities"]["fear"],
        emotion_probs_neutral=result["emotionProbabilities"]["neutral"],
        emotion_probs_surprise=result["emotionProbabilities"]["surprise"],
        emotion_probs_trust=result["emotionProbabilities"]["trust"],
        emotion_probs_anticipation=result["emotionProbabilities"]["anticipation"],
        sentiment_probs_positive=result["sentimentProbabilities"]["positive"],
        sentiment_probs_negative=result["sentimentProbabilities"]["negative"],
        sentiment_probs_neutral=result["sentimentProbabilities"]["neutral"],
    )

# 🔹 Top 3 emociones y top 1 sentimiento de la última semana
@router.get("/transcriptions/user/last-week/top-emotions-sentiments", response_model=TrancriptionTop3)
async def get_top_emotions_and_sentiments(
    user_id: str = Depends(get_current_user),
    collection=Depends(get_mongo_collection)
):
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=7)

    user = await collection.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    results = [
        t for t in user.get("transcriptions", [])
        if datetime.strptime(t["date"], "%Y-%m-%d").date() >= seven_days_ago
        and datetime.strptime(t["date"], "%Y-%m-%d").date() <= today
    ]

    if not results:
        raise HTTPException(status_code=404, detail="No hay transcripciones en los últimos 7 días")

    total = len(results)
    avg_emotions = {
        "joy": sum(t["emotionProbabilities"]["joy"] for t in results) / total,
        "anger": sum(t["emotionProbabilities"]["anger"] for t in results) / total,
        "sadness": sum(t["emotionProbabilities"]["sadness"] for t in results) / total,
        "disgust": sum(t["emotionProbabilities"]["disgust"] for t in results) / total,
        "fear": sum(t["emotionProbabilities"]["fear"] for t in results) / total,
        "neutral": sum(t["emotionProbabilities"]["neutral"] for t in results) / total,
        "surprise": sum(t["emotionProbabilities"]["surprise"] for t in results) / total,
        "trust": sum(t["emotionProbabilities"]["trust"] for t in results) / total,
        "anticipation": sum(t["emotionProbabilities"]["anticipation"] for t in results) / total,
    }

    avg_sentiments = {
        "positive": sum(t["sentimentProbabilities"]["positive"] for t in results) / total,
        "negative": sum(t["sentimentProbabilities"]["negative"] for t in results) / total,
        "neutral": sum(t["sentimentProbabilities"]["neutral"] for t in results) / total,
    }

    top_emotions = sorted(avg_emotions.items(), key=itemgetter(1), reverse=True)[:3]
    top_sentiments = sorted(avg_sentiments.items(), key=itemgetter(1), reverse=True)[:1]

    return TrancriptionTop3(
        emotion_probs_top1=top_emotions[0][0],
        emotion_probs_top2=top_emotions[1][0],
        emotion_probs_top3=top_emotions[2][0],
        sentiment_probs_top1=top_sentiments[0][0]
    )