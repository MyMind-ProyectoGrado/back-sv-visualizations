from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta, timezone
from app.models.transcription import Transcription


def get_all_transcriptions(db: Session):
    return db.query(Transcription).all()


def get_transcription_by_id(db: Session, transcription_id: str):
    return db.query(Transcription).filter(Transcription.transcription_id == transcription_id).first()


def get_transcriptions_last_7_days(db: Session):
    today = datetime.now(timezone.utc).date()
    seven_days_ago = today - timedelta(days=7)
    yesterday = today - timedelta(days=1)

    return (
        db.query(Transcription)
        .filter(Transcription.transcription_date >= seven_days_ago)
        .filter(Transcription.transcription_date <= yesterday)
        .order_by(Transcription.transcription_date.asc())
        .all()
    )


def get_transcriptions_by_user(db: Session, user_id: str):
    return (
        db.query(Transcription)
        .filter(Transcription.user_id == user_id)
        .order_by(Transcription.transcription_date.desc())
        .all()
    )


def get_latest_transcription_by_user(db: Session, user_id: str):
    return (
        db.query(Transcription)
        .filter(Transcription.user_id == user_id)
        .order_by(Transcription.transcription_date.desc())
        .first()
    )
