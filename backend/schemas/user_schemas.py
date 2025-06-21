# schemas.py
from pydantic import BaseModel, ConfigDict, EmailStr, Field, computed_field
from pydantic_extra_types.phone_numbers import PhoneNumber
from enum import Enum
from uuid import UUID
from datetime import datetime


class Role(str, Enum):
    admin = "admin"
    agent = "agent"


class UserCreate(BaseModel):
    name: str
    username: str
    email: EmailStr
    phone_number: PhoneNumber
    hashed_password: str
    role: Role


class UserUpdate(BaseModel):
    name: str
    username: str
    email: EmailStr
    phone_number: PhoneNumber
    role: Role


class UserInDB(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone_number: PhoneNumber
    username: str
    role: Role
    date_created: datetime
    is_active: bool
    avatar_path: str | None = Field(None, alias="avatar_url")

    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def avatar_url(self) -> str:
        base_url = "http://localhost:8000"
        if self.avatar_path:
            return f"{base_url}{self.avatar_path}"
        return f"{base_url}/uploads/default_avatar.png"
