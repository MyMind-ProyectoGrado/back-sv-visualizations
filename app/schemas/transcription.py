from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime

class TranscriptionOut(BaseModel):
    id: str = Field(..., alias="_id")
    user_id: str
    date: str
    time: str
    text: str
    emotion: str
    emotionProbabilities: Dict[str, float]
    sentiment: str
    sentimentProbabilities: Dict[str, float]
    topic: Optional[str] = None

    class Config:
        validate_by_name = True  # Cambiado de allow_population_by_field_name

class TranscriptionSummary(BaseModel):
    transcription_id: str
    transcription_date: str
    transcription_time: str

class TranscriptionSummary2(BaseModel):
    transcription_id: str
    transcription_date: str
    transcription_time: str
    emotion: str
    sentiment: str
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

class TrancriptionTop3(BaseModel):
    emotion_probs_top1: str
    emotion_probs_top2: str
    emotion_probs_top3: str
    sentiment_probs_top1: str