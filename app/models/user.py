from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(String(255), primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True)
    profile_pic = Column(String(200))
    birthdate = Column(DateTime)
    city = Column(String(100))
    personality = Column(String(100))
    university = Column(String(255))
    degree = Column(String(255))
    gender = Column(String(50))
    notifications = Column(Boolean, default=True)
    accept_policies = Column(Boolean, default=False)
    acceptance_date = Column(DateTime, default=datetime.utcnow)
    acceptance_ip = Column(String(45))
    allow_anonimized_usage = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transcriptions = relationship("Transcription", back_populates="owner")
