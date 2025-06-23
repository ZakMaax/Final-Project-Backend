from pydantic import BaseModel
from enum import Enum
from uuid import UUID


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class Roles(str, Enum):
    admin = "admin"
    agent = "agent"


class TokenData(BaseModel):
    id: UUID | None = None
    role: Roles | None = None
    name: str | None = None
    avatar: str | None = None
