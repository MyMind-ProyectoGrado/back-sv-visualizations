from sqlalchemy import Column, String, DateTime, ForeignKey, Time
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Transcription(Base):
    __tablename__ = "transcriptions"

    transcription_id = Column(String(255), primary_key=True, index=True)
    transcription_date = Column(DateTime, default=datetime.utcnow)
    transcription_time = Column(Time)
    text = Column(String(1000))
    emotion = Column(String(100))
    sentiment = Column(String(100))
    topic = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = Column(String(255), ForeignKey("users.user_id"))
    owner = relationship("User", back_populates="transcriptions")
