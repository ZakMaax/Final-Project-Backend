from typing import Optional
from models.appointments import PropertyAppointment, AppointmentStatus
from sqlalchemy import select, and_
from fastapi import HTTPException, status
from models.properties import Property
from models.users import User
from schemas.appointment_schemas import AppointmentCreate
from datetime import timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID


class AppointmentService:
    async def create_appointment(
        self, appointment_data: AppointmentCreate, session: AsyncSession
    ):
        # Define UTC+03:00 timezone
        tz = timezone(timedelta(hours=3))
        start = appointment_data.appointment_datetime

        # Convert to UTC+03:00 and make naive (strip tzinfo for DB)
        if start.tzinfo is not None:
            start = start.astimezone(tz).replace(tzinfo=None)
        else:
            # Assume naive datetimes are already in UTC+03:00
            pass

        end = start + timedelta(minutes=30)

        overlap_stmt = select(PropertyAppointment).where(
            and_(
                PropertyAppointment.property_id == appointment_data.property_id,  # type: ignore
                PropertyAppointment.appointment_datetime < end,  # type: ignore
                PropertyAppointment.appointment_datetime  # type: ignore
                >= start - timedelta(minutes=30),
            )
        )
        result = await session.execute(overlap_stmt)
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Time already booked for this property, please pick another time.",
            )
        appointment_data_dict = appointment_data.model_dump()
        appointment_data_dict["appointment_datetime"] = start
        appointment = PropertyAppointment(**appointment_data_dict)
        session.add(appointment)
        await session.commit()
        await session.refresh(appointment)
        return {
            "message": "Your appointment is scheduled successfully! We will contact you soon"
        }

    async def get_appointments(
        self, session: AsyncSession, agent_id: Optional[UUID] = None
    ):
        stmt = (
            select(PropertyAppointment, Property, User)
            .join(Property, PropertyAppointment.property_id == Property.id)  # type: ignore
            .join(User, Property.agent_id == User.id)  # type: ignore
        )
        if agent_id:
            stmt = stmt.where(User.id == agent_id)  # type: ignore
        result = await session.execute(stmt)
        appointments = []
        for appointment, property, agent in result.all():
            appointments.append(
                {
                    "customer_name": appointment.customer_name,
                    "customer_phone": appointment.customer_phone,
                    "appointment_datetime": appointment.appointment_datetime,
                    "property_id": property.id,
                    "property_title": property.title,
                    "agent_id": agent.id,
                    "agent_name": getattr(
                        agent, "name", getattr(agent, "full_name", "")
                    )
                    if agent
                    else "N/A",
                    "appointment_status": appointment.appointment_status,
                    "id": appointment.id,
                }
            )
        return appointments

    async def update_appointment_status(
        self,
        appointment_id: UUID,
        status: AppointmentStatus,
        session: AsyncSession,
    ):
        result = await session.execute(
            select(PropertyAppointment).where(PropertyAppointment.id == appointment_id)  # type: ignore
        )
        appointment = result.scalars().first()
        if not appointment:
            raise HTTPException(status_code=404, detail="Appointment not found")
        appointment.appointment_status = status
        await session.commit()
        await session.refresh(appointment)
        return {"message": "Appointment status updated successfully"}


appointment_service = AppointmentService()
