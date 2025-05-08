from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str
    profile_pic: Optional[str]
    birthdate: Optional[datetime]
    city: Optional[str]
    personality: Optional[str]
    university: Optional[str]
    degree: Optional[str]
    gender: Optional[str]


class UserCreate(UserBase):
    pass


class UserOut(UserBase):
    user_id: str = Field(alias="_id")  # Alias para MongoDB

    class Config:
        populate_by_name = True  # para que use el alias
