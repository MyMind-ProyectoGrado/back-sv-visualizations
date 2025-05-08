from datetime import datetime, timedelta, timezone
from typing import List, Optional
from pymongo import DESCENDING, ASCENDING
from app.models.transcription import Transcription

# 🔹 Obtener todas las transcripciones
async def get_all_transcriptions(db) -> List[dict]:
    return await db.transcriptions.find().to_list(length=None)

# 🔹 Obtener transcripción por ID
async def get_transcription_by_id(db, transcription_id: str) -> Optional[dict]:
    return await db.transcriptions.find_one({"_id": transcription_id})

# 🔹 Obtener transcripciones de los últimos 7 días (excluyendo hoy)
async def get_transcriptions_last_7_days(db) -> List[dict]:
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=7)
    yesterday = today - timedelta(days=1)

    return await db.transcriptions.find({
        "transcription_date": {
            "$gte": datetime.combine(seven_days_ago, datetime.min.time()),
            "$lte": datetime.combine(yesterday, datetime.max.time())
        }
    }).sort("transcription_date", ASCENDING).to_list(length=None)

# 🔹 Obtener todas las transcripciones de un usuario
async def get_transcriptions_by_user(db, user_id: str) -> List[dict]:
    return await db.transcriptions.find({"user_id": user_id}).sort("transcription_date", DESCENDING).to_list(length=None)

# 🔹 Obtener la transcripción más reciente de un usuario
async def get_latest_transcription_by_user(db, user_id: str) -> Optional[dict]:
    return await db.transcriptions.find_one({"user_id": user_id}, sort=[("transcription_date", DESCENDING)])
