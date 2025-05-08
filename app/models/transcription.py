from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, time

class Transcription(BaseModel):
    transcription_id: str = Field(..., alias="_id")  # Mongo usa "_id" como clave primaria
    transcription_date: datetime = Field(default_factory=datetime.utcnow)
    transcription_time: Optional[time]
    text: Optional[str]
    emotion: Optional[str]
    sentiment: Optional[str]
    topic: Optional[str]

    emotion_probs_joy: Optional[float]
    emotion_probs_anger: Optional[float]
    emotion_probs_sadness: Optional[float]
    emotion_probs_disgust: Optional[float]
    emotion_probs_fear: Optional[float]
    emotion_probs_neutral: Optional[float]
    emotion_probs_surprise: Optional[float]
    emotion_probs_trust: Optional[float]
    emotion_probs_anticipation: Optional[float]

    sentiment_probs_positive: Optional[float]
    sentiment_probs_negative: Optional[float]
    sentiment_probs_neutral: Optional[float]

    user_id: str  # Aquí solo guardas el ID del usuario, no hay relaciones

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }
