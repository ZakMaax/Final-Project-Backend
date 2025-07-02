from pydantic import BaseModel, field_validator
from pydantic_extra_types.phone_numbers import PhoneNumber
from uuid import UUID
from datetime import datetime, timezone
from models.appointments import AppointmentStatus


class AppointmentCreate(BaseModel):
    customer_name: str
    customer_phone: str
    appointment_datetime: datetime
    property_id: UUID

    @field_validator("appointment_datetime", mode="before")
    @classmethod
    def make_naive(cls, v):
        # If input is a string, parse it to datetime first
        if isinstance(v, str):
            v = datetime.fromisoformat(v)
        if v.tzinfo is not None:
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v


class AppointmentRead(BaseModel):
    id: UUID
    customer_name: str
    customer_phone: PhoneNumber
    appointment_datetime: datetime
    appointment_status: AppointmentStatus
    property_id: UUID
    property_title: str
    agent_name: str
    agent_id: UUID


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus
