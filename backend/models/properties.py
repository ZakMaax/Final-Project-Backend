from sqlmodel import SQLModel, Field, Column, Relationship
import sqlalchemy.dialects.postgresql as pg
from pydantic import PositiveFloat, PositiveInt
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from .users import User
    from .appointments import PropertyAppointment


class PropertyType(str, Enum):
    residential = "residential"
    apartment = "apartment"
    commercial = "commercial"
    land = "land"


class SaleRent(str, Enum):
    sale = "sale"
    rent = "rent"


class PropertyStatus(str, Enum):
    available = "available"
    sold = "sold"
    rented = "rented"


class Property(SQLModel, table=True):
    __tablename__ = "properties"  # type: ignore

    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID, primary_key=True, index=True, nullable=False),
    )
    title: str = Field(nullable=False)
    description: str = Field(sa_column=Column(pg.TEXT, nullable=False))
    city: str = Field(index=True, nullable=False)
    address: str = Field(nullable=False)
    bedrooms: PositiveInt = Field(nullable=False)
    bathrooms: PositiveInt = Field(nullable=False)
    size: PositiveInt = Field(nullable=False)
    price: PositiveFloat = Field(index=True, nullable=False)
    published_date: datetime = Field(
        default_factory=datetime.now, sa_column=Column(pg.TIMESTAMP, nullable=False)
    )
    featured: bool = Field(sa_column=Column(pg.BOOLEAN, default=False, nullable=False))
    latitude: float = Field(ge=-90, le=90, nullable=False)
    longitude: float = Field(ge=-180, le=180, nullable=False)
    floor: Optional[PositiveInt] = Field(default=None, nullable=True)
    type: PropertyType = Field(index=True, nullable=False)
    status: PropertyStatus = Field(default=PropertyStatus.available)
    sale_or_rent: SaleRent = Field(nullable=False)
    agent_id: UUID = Field(foreign_key="users.id", nullable=False)
    agent: Optional["User"] = Relationship(back_populates="properties")
    images: List["PropertyImage"] = Relationship(
        back_populates="property",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    appointments: list["PropertyAppointment"] = Relationship(back_populates="property")

    def __repr__(self):
        return f"<Property(title={self.title}, city={self.city}, price={self.price})>"


class PropertyImage(SQLModel, table=True):
    __tablename__ = "property_images"  # type: ignore
    id: Optional[UUID] = Field(
        default_factory=uuid4,
        sa_column=Column(pg.UUID, primary_key=True, index=True, nullable=False),
    )
    file_name: str = Field(nullable=False)
    property_id: UUID = Field(foreign_key="properties.id", nullable=False)
    property: "Property" = Relationship(back_populates="images")

    def __repr__(self):
        return f"<PropertyImage(file_name={self.file_name}, property_id={self.property_id})>"
