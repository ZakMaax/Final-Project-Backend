from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
import uuid
from enum import Enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional, List
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber

if TYPE_CHECKING:
    from .properties import Property


class Roles(str, Enum):
    admin = "admin"
    agent = "agent"


class User(SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        sa_column=Column(pg.UUID, primary_key=True, index=True, nullable=False),
    )
    name: str = Field(nullable=False)
    date_created: datetime = Field(
        default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP, nullable=False)
    )
    username: str = Field(unique=True, index=True, nullable=False)
    email: EmailStr = Field(unique=True, nullable=False)
    phone_number: PhoneNumber = Field(unique=True, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    hashed_password: str = Field(nullable=False)
    role: Roles = Field(nullable=False)
    avatar_url: Optional[str] = Field(default=None, nullable=True)
    properties: List["Property"] = Relationship(back_populates="agent")

    def __repr__(self):
        return f"<User(username={self.username}, role={self.role}, email={self.email})>"
