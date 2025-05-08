from pydantic import BaseModel, Field
from datetime import datetime, time
from typing import Optional


class TranscriptionOut(BaseModel):
    transcription_id: str = Field(alias="_id")  # <-- importante si usas _id en Mongo
    transcription_date: datetime
    transcription_time: Optional[time] = None
    text: Optional[str] = None
    emotion: Optional[str] = None
    sentiment: Optional[str] = None
    topic: Optional[str] = None

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
        populate_by_name = True  # permite usar .dict(by_alias=True)

class TranscriptionSummary(BaseModel):
    transcription_id: str = Field(alias="_id")  # Alias para MongoDB
    transcription_date: datetime
    transcription_time: Optional[time] = None

    class Config:
        populate_by_name = True  # para que use el alias


class TranscriptionSummary2(BaseModel):
    transcription_id: str = Field(alias="_id")  # Alias para MongoDB
    transcription_date: datetime
    transcription_time: Optional[time] = None
    emotion: Optional[str] = None
    sentiment: Optional[str] = None

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

    class Config:
        populate_by_name = True  # para que use el alias


class TranscriptionAverages(BaseModel):
    emotion_probs_joy: float
    emotion_probs_anger: float
    emotion_probs_sadness: float
    emotion_probs_disgust: float
    emotion_probs_fear: float
    emotion_probs_neutral: float
    emotion_probs_surprise: float
    emotion_probs_trust: float
    emotion_probs_anticipation: float
    sentiment_probs_positive: float
    sentiment_probs_negative: float
    sentiment_probs_neutral: float

    class Config:
        populate_by_name = True  # para que use el alias


class TrancriptionTop3(BaseModel):
    emotion_probs_top1: str
    emotion_probs_top2: str
    emotion_probs_top3: str
    sentiment_probs_top1: str

    class Config:
        populate_by_name = True  # para que use el alias