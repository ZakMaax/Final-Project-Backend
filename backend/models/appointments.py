from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .properties import Property


class AppointmentStatus(str, Enum):
    scheduled = "scheduled"
    pending = "pending"
    completed = "completed"
    cancelled = "cancelled"
    no_show_agent = "no_show_agent"
    no_show_customer = "no_show_customer"


class PropertyAppointment(SQLModel, table=True):
    __tablename__ = "property_appointments"  # type: ignore

    id: Optional[UUID] = Field(default_factory=uuid4, primary_key=True, index=True)
    customer_name: str = Field(nullable=False)
    customer_phone: str = Field(nullable=False)
    appointment_datetime: datetime = Field(nullable=False, index=True)
    appointment_status: AppointmentStatus = Field(default=AppointmentStatus.scheduled)
    property_id: UUID = Field(foreign_key="properties.id", nullable=False)
    property: "Property" = Relationship(back_populates="appointments")
