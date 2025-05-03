from sqlalchemy import Column, String, DateTime, ForeignKey, Time, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base
from app.models.user import User

class Transcription(Base):
    __tablename__ = "transcriptions"

    transcription_id = Column(String(255), primary_key=True, index=True)
    transcription_date = Column(DateTime, default=datetime.utcnow)
    transcription_time = Column(Time)
    text = Column(String(1000))
    emotion = Column(String(100))
    sentiment = Column(String(100))
    topic = Column(String(255))
    
    emotion_probs_joy = Column(Float)
    emotion_probs_anger = Column(Float)
    emotion_probs_sadness = Column(Float)
    emotion_probs_disgust = Column(Float)
    emotion_probs_fear = Column(Float)
    emotion_probs_neutral = Column(Float)
    emotion_probs_surprise = Column(Float)
    emotion_probs_trust = Column(Float)
    emotion_probs_anticipation = Column(Float)
    
    sentiment_probs_positive = Column(Float)
    sentiment_probs_negative = Column(Float)
    sentiment_probs_neutral = Column(Float)

    user_id = Column(String(255), ForeignKey("users.user_id"))
    owner = relationship("User", back_populates="transcriptions")
