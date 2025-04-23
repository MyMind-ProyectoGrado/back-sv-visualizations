from pydantic import BaseModel
from datetime import datetime, time

class TranscriptionOut(BaseModel):
    transcription_id: str
    transcription_date: datetime
    transcription_time: time | None = None
    text: str | None = None
    emotion: str | None = None
    sentiment: str | None = None
    topic: str | None = None
    created_at: datetime
    updated_at: datetime
    user_id: str

    class Config:
        from_attributes = True
