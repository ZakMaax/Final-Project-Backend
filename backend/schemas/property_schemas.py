from pydantic import BaseModel, PositiveInt, PositiveFloat, EmailStr, Field
from pydantic_extra_types.phone_numbers import PhoneNumber
from enum import Enum
from uuid import UUID
from typing import Optional, List
from datetime import datetime
from models.properties import PropertyStatus


class PropertyType(str, Enum):
    residential = "residential"
    apartment = "apartment"
    commercial = "commercial"
    land = "land"


class SaleRent(str, Enum):
    sale = "sale"
    rent = "rent"


class PropertyCreate(BaseModel):
    title: str
    city: str
    description: str
    address: str
    bedrooms: PositiveInt
    bathrooms: PositiveInt
    size: PositiveInt
    price: PositiveFloat
    latitude: float
    longitude: float
    floor: PositiveInt | None = None
    type: PropertyType
    sale_or_rent: SaleRent
    agent_id: UUID


class AgentInfo(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone_number: PhoneNumber
    avatar_path: str | None = Field(None, alias="avatar_url")


class PropertyResponse(BaseModel):
    id: UUID
    title: str
    city: str
    description: str
    address: str
    bedrooms: PositiveInt
    bathrooms: PositiveInt
    size: PositiveInt
    price: PositiveFloat
    latitude: float
    longitude: float
    floor: Optional[PositiveInt]
    type: PropertyType
    sale_or_rent: SaleRent
    agent_id: UUID
    published_date: datetime
    featured: bool
    status: PropertyStatus
    images: List[str] = []
    agent: Optional[AgentInfo] = None

    class Config:
        from_attributes = True


class FeaturedUpdate(BaseModel):
    featured: bool


class StatusUpdate(BaseModel):
    status: PropertyStatus
