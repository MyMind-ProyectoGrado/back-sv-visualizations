import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch
from datetime import datetime, timedelta, timezone
from app.routes.transcription import (
    get_transcription_by_audio_id,
    get_last_7_days_transcriptions_average,
    get_transcriptions_by_user,
    get_latest_transcription_by_user,
    get_top_emotions_and_sentiments
)
from app.schemas.transcription import (
    TranscriptionSummary,
    TranscriptionSummary2,
    TranscriptionAverages,
    TrancriptionTop3
)

# Datos de prueba reutilizables
MOCK_USER_ID = "auth0|67ec68c74000acd49b9bfec7"
MOCK_TRANSCRIPTION = {
    "_id": "6817d4ae6cad195648dad37d",
    "date": "2025-05-04",
    "time": "15:57:18",
    "text": "hoy hable con la persona que me gusta...",
    "emotion": "fear",
    "emotionProbabilities": {
        "joy": 0.0263, "anger": 0.0566, "sadness": 0.0271, "disgust": 0.0519,
        "fear": 0.5277, "neutral": 0.0376, "surprise": 0.0492, "trust": 0.0846,
        "anticipation": 0.139
    },
    "sentiment": "positive",
    "sentimentProbabilities": {
        "positive": 0.9115, "negative": 0.008, "neutral": 0.0805
    },
    "topic": None
}

# 1. Pruebas para /transcriptions/user/audio/{audio_id}
@pytest.mark.asyncio
async def test_get_transcription_by_audio_id_success():
    mock_collection = AsyncMock()
    mock_user = {
        "_id": MOCK_USER_ID,
        "transcriptions": [MOCK_TRANSCRIPTION]
    }
    mock_collection.find_one.return_value = mock_user

    with patch("app.routes.transcription.get_mongo_collection", return_value=mock_collection), \
         patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        response = await get_transcription_by_audio_id(
            audio_id=MOCK_TRANSCRIPTION["_id"],
            user_id=MOCK_USER_ID,
            collection=mock_collection
        )

    assert isinstance(response, TranscriptionSummary2)
    assert response.transcription_id == MOCK_TRANSCRIPTION["_id"]
    assert response.transcription_date == MOCK_TRANSCRIPTION["date"]
    assert response.emotion == MOCK_TRANSCRIPTION["emotion"]
    assert response.sentiment == MOCK_TRANSCRIPTION["sentiment"]
    assert response.emotion_probs_joy == MOCK_TRANSCRIPTION["emotionProbabilities"]["joy"]
    assert response.sentiment_probs_positive == MOCK_TRANSCRIPTION["sentimentProbabilities"]["positive"]

@pytest.mark.asyncio
async def test_get_transcription_by_audio_id_user_not_found():
    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = None

    with patch("app.routes.transcription.get_mongo_collection", return_value=mock_collection), \
         patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        with pytest.raises(HTTPException) as exc:
            await get_transcription_by_audio_id(
                audio_id=MOCK_TRANSCRIPTION["_id"],
                user_id=MOCK_USER_ID,
                collection=mock_collection
            )
        assert exc.value.status_code == 404
        assert exc.value.detail == "Usuario no encontrado"

@pytest.mark.asyncio
async def test_get_transcription_by_audio_id_transcription_not_found():
    mock_collection = AsyncMock()
    mock_user = {
        "_id": MOCK_USER_ID,
        "transcriptions": []
    }
    mock_collection.find_one.return_value = mock_user

    with patch("app.routes.transcription.get_mongo_collection", return_value=mock_collection), \
         patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        with pytest.raises(HTTPException) as exc:
            await get_transcription_by_audio_id(
                audio_id=MOCK_TRANSCRIPTION["_id"],
                user_id=MOCK_USER_ID,
                collection=mock_collection
            )
        assert exc.value.status_code == 404
        assert exc.value.detail == f"No se encontró ninguna transcripción con el ID de audio: {MOCK_TRANSCRIPTION['_id']}"

# 2. Pruebas para /transcriptions/user/last-7-days
@pytest.mark.asyncio
async def test_get_last_7_days_transcriptions_average_success():
    mock_collection = AsyncMock()
    today = datetime.now(timezone.utc).date()
    mock_user = {
        "_id": MOCK_USER_ID,
        "transcriptions": [
            {**MOCK_TRANSCRIPTION, "date": today.strftime("%Y-%m-%d")},
            {**MOCK_TRANSCRIPTION, "date": today.strftime("%Y-%m-%d"),
             "emotionProbabilities": {k: v * 2 for k, v in MOCK_TRANSCRIPTION["emotionProbabilities"].items()},
             "sentimentProbabilities": {k: v * 2 for k, v in MOCK_TRANSCRIPTION["sentimentProbabilities"].items()}}
        ]
    }
    mock_collection.find_one.return_value = mock_user
    
    with patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        response = await get_last_7_days_transcriptions_average(user_id=MOCK_USER_ID, collection=mock_collection)
    
    assert isinstance(response, TranscriptionAverages)
    assert response.emotion_probs_joy == (0.0263 + 0.0263 * 2) / 2
    assert response.sentiment_probs_positive == (0.9115 + 0.9115 * 2) / 2

@pytest.mark.asyncio
async def test_get_last_7_days_transcriptions_average_user_not_found():
    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = None
    
    with patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        with pytest.raises(HTTPException) as exc:
            await get_last_7_days_transcriptions_average(user_id=MOCK_USER_ID, collection=mock_collection)
        assert exc.value.status_code == 404
        assert exc.value.detail == "Usuario no encontrado"

@pytest.mark.asyncio
async def test_get_last_7_days_transcriptions_average_no_transcriptions():
    mock_collection = AsyncMock()
    mock_user = {"_id": MOCK_USER_ID, "transcriptions": []}
    mock_collection.find_one.return_value = mock_user
    
    with patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        with pytest.raises(HTTPException) as exc:
            await get_last_7_days_transcriptions_average(user_id=MOCK_USER_ID, collection=mock_collection)
        assert exc.value.status_code == 404
        assert exc.value.detail == "No hay transcripciones en los últimos 7 días"

# 3. Pruebas para /transcriptions/user
@pytest.mark.asyncio
async def test_get_transcriptions_by_user_success():
    mock_collection = AsyncMock()
    mock_user = {
        "_id": MOCK_USER_ID,
        "transcriptions": [
            MOCK_TRANSCRIPTION,
            {**MOCK_TRANSCRIPTION, "_id": "another_id", "date": "2025-05-03"}
        ]
    }
    mock_collection.find_one.return_value = mock_user
    
    with patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        response = await get_transcriptions_by_user(user_id=MOCK_USER_ID, collection=mock_collection)
    
    assert len(response) == 2
    assert isinstance(response[0], TranscriptionSummary)
    assert response[0].transcription_id == MOCK_TRANSCRIPTION["_id"]
    assert response[0].transcription_date == MOCK_TRANSCRIPTION["date"]
    assert response[1].transcription_date == "2025-05-03"  # Ordenado por fecha descendente

@pytest.mark.asyncio
async def test_get_transcriptions_by_user_user_not_found():
    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = None
    
    with patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        with pytest.raises(HTTPException) as exc:
            await get_transcriptions_by_user(user_id=MOCK_USER_ID, collection=mock_collection)
        assert exc.value.status_code == 404
        assert exc.value.detail == "Usuario no encontrado"

# 4. Pruebas para /transcriptions/user/latest
@pytest.mark.asyncio
async def test_get_latest_transcription_by_user_success():
    mock_collection = AsyncMock()
    mock_user = {
        "_id": MOCK_USER_ID,
        "transcriptions": [
            MOCK_TRANSCRIPTION,
            {**MOCK_TRANSCRIPTION, "_id": "older_id", "date": "2025-05-03", "time": "10:00:00"}
        ]
    }
    mock_collection.find_one.return_value = mock_user
    
    with patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        response = await get_latest_transcription_by_user(user_id=MOCK_USER_ID, collection=mock_collection)
    
    assert isinstance(response, TranscriptionSummary2)
    assert response.transcription_id == MOCK_TRANSCRIPTION["_id"]
    assert response.transcription_date == MOCK_TRANSCRIPTION["date"]
    assert response.emotion == MOCK_TRANSCRIPTION["emotion"]

@pytest.mark.asyncio
async def test_get_latest_transcription_by_user_user_not_found():
    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = None
    
    with patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        with pytest.raises(HTTPException) as exc:
            await get_latest_transcription_by_user(user_id=MOCK_USER_ID, collection=mock_collection)
        assert exc.value.status_code == 404
        assert exc.value.detail == "Usuario no encontrado"

@pytest.mark.asyncio
async def test_get_latest_transcription_by_user_no_transcriptions():
    mock_collection = AsyncMock()
    mock_user = {"_id": MOCK_USER_ID, "transcriptions": []}
    mock_collection.find_one.return_value = mock_user
    
    with patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        with pytest.raises(HTTPException) as exc:
            await get_latest_transcription_by_user(user_id=MOCK_USER_ID, collection=mock_collection)
        assert exc.value.status_code == 404
        assert exc.value.detail == "No se encontró ninguna transcripción para este usuario"

# 5. Pruebas para /transcriptions/user/last-week/top-emotions-sentiments
@pytest.mark.asyncio
async def test_get_top_emotions_and_sentiments_success():
    mock_collection = AsyncMock()
    today = datetime.now(timezone.utc).date()
    mock_user = {
        "_id": MOCK_USER_ID,
        "transcriptions": [
            {**MOCK_TRANSCRIPTION, "date": today.strftime("%Y-%m-%d")},
            {**MOCK_TRANSCRIPTION, "date": today.strftime("%Y-%m-%d"),
             "emotionProbabilities": {k: v * 2 for k, v in MOCK_TRANSCRIPTION["emotionProbabilities"].items()},
             "sentimentProbabilities": {k: v * 2 for k, v in MOCK_TRANSCRIPTION["sentimentProbabilities"].items()}}
        ]
    }
    mock_collection.find_one.return_value = mock_user
    
    with patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        response = await get_top_emotions_and_sentiments(user_id=MOCK_USER_ID, collection=mock_collection)
    
    assert isinstance(response, TrancriptionTop3)
    assert response.emotion_probs_top1 in MOCK_TRANSCRIPTION["emotionProbabilities"]
    assert response.sentiment_probs_top1 == "positive"  # Basado en los datos mockeados

@pytest.mark.asyncio
async def test_get_top_emotions_and_sentiments_user_not_found():
    mock_collection = AsyncMock()
    mock_collection.find_one.return_value = None
    
    with patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        with pytest.raises(HTTPException) as exc:
            await get_top_emotions_and_sentiments(user_id=MOCK_USER_ID, collection=mock_collection)
        assert exc.value.status_code == 404
        assert exc.value.detail == "Usuario no encontrado"

@pytest.mark.asyncio
async def test_get_top_emotions_and_sentiments_no_transcriptions():
    mock_collection = AsyncMock()
    mock_user = {"_id": MOCK_USER_ID, "transcriptions": []}
    mock_collection.find_one.return_value = mock_user
    
    with patch("app.routes.transcription.get_current_user", return_value=MOCK_USER_ID):
        with pytest.raises(HTTPException) as exc:
            await get_top_emotions_and_sentiments(user_id=MOCK_USER_ID, collection=mock_collection)
        assert exc.value.status_code == 404
        assert exc.value.detail == "No hay transcripciones en los últimos 7 días"