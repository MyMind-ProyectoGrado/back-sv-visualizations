from pydantic import BaseModel
from datetime import datetime, time
from typing import Optional

class TranscriptionOut(BaseModel):
    transcription_id: str
    transcription_date: datetime
    transcription_time: Optional[time] = None
    text: Optional[str] = None
    emotion: Optional[str] = None
    sentiment: Optional[str] = None
    topic: Optional[str] = None

    # Nuevos campos agregados
    emotion_probs_joy: Optional[float] = None
    emotion_probs_anger: Optional[float] = None
    emotion_probs_sadness: Optional[float] = None
    emotion_probs_disgust: Optional[float] = None
    emotion_probs_fear: Optional[float] = None
    emotion_probs_neutral: Optional[float] = None
    emotion_probs_surprise: Optional[float] = None
    emotion_probs_trust: Optional[float] = None
    emotion_probs_anticipation: Optional[float] = None

    sentiment_probs_positive: Optional[float] = None
    sentiment_probs_negative: Optional[float] = None
    sentiment_probs_neutral: Optional[float] = None

    user_id: str

    class Config:
        from_attributes = True
