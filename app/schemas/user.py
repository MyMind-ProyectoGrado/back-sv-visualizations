from pydantic import BaseModel, EmailStr
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
    user_id: str

    class Config:
        from_attributes = True
