from fastapi import APIRouter, Depends
from schemas.appointment_schemas import (
    AppointmentCreate,
    AppointmentStatusUpdate,
    AppointmentRead,
)
from services.appointment_service import appointment_service
from sqlmodel.ext.asyncio.session import AsyncSession
from core.init_db import get_session
from uuid import UUID
from typing import List, Optional

appointment_router = APIRouter()


@appointment_router.post("/", status_code=201)
async def create_appointment(
    appointment_data: AppointmentCreate,
    session: AsyncSession = Depends(get_session),
):
    return await appointment_service.create_appointment(appointment_data, session)


@appointment_router.get("/", response_model=List[AppointmentRead])
async def get_appointments(
    agent_id: Optional[UUID] = None,
    session: AsyncSession = Depends(get_session),
):
    return await appointment_service.get_appointments(session, agent_id)


@appointment_router.patch("/appointment/{appointment_id}/status")
async def update_appointment_status(
    appointment_id: UUID,
    status_update: AppointmentStatusUpdate,
    session: AsyncSession = Depends(get_session),
):
    return await appointment_service.update_appointment_status(
        appointment_id, status_update.status, session
    )
