from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime

class User(BaseModel):
    user_id: str = Field(..., alias="_id")  # MongoDB usa _id como clave primaria
    name: Optional[str]
    email: Optional[EmailStr]
    profile_pic: Optional[str]
    birthdate: Optional[datetime]
    city: Optional[str]
    personality: Optional[str]
    university: Optional[str]
    degree: Optional[str]
    gender: Optional[str]
    notifications: bool = True
    accept_policies: bool = False
    acceptance_date: datetime = Field(default_factory=datetime.utcnow)
    acceptance_ip: Optional[str]
    allow_anonimized_usage: bool = False

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda dt: dt.isoformat(),
        }
