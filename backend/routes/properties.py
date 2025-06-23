from fastapi import APIRouter, HTTPException, Query, Depends, status, Form, UploadFile
from sqlmodel.ext.asyncio.session import AsyncSession
from schemas.property_schemas import (
    PropertyCreate,
    PropertyResponse,
    PropertyType,
    SaleRent,
    FeaturedUpdate,
    StatusUpdate,
)
from core.init_db import get_session
from typing import List, Optional
from pydantic import PositiveInt, PositiveFloat
from services.property_service import property_service
from security.auth import require_admin
from uuid import UUID
from schemas.user_schemas import UserRead

property_router = APIRouter()


@property_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_property(
    title: str = Form(...),
    city: str = Form(...),
    description: str = Form(...),
    address: str = Form(...),
    bedrooms: PositiveInt = Form(...),
    bathrooms: PositiveInt = Form(...),
    size: PositiveInt = Form(...),
    price: PositiveFloat = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    floor: Optional[PositiveInt] = Form(None),
    type: PropertyType = Form(...),
    sale_or_rent: SaleRent = Form(...),
    agent_id: UUID = Form(...),
    files: List[UploadFile] = Form(...),
    current_user: UserRead = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    property_data = PropertyCreate(
        title=title,
        city=city,
        description=description,
        address=address,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        size=size,
        price=price,
        latitude=latitude,
        longitude=longitude,
        floor=floor,
        type=type,
        sale_or_rent=sale_or_rent,
        agent_id=agent_id,
    )
    return await property_service.create_property(property_data, files, session)


@property_router.get("/", response_model=List[PropertyResponse])
async def get_all_properties(
    sale_or_rent: Optional[SaleRent] = Query(None),
    city: Optional[str] = Query(None),
    min_price: Optional[float] = Query(None),
    max_price: Optional[float] = Query(None),
    type: Optional[PropertyType] = Query(None),
    agent_id: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
):
    properties = await property_service.get_properties(
        sale_or_rent=sale_or_rent,
        city=city,
        min_price=min_price,
        max_price=max_price,
        type=type,
        agent_id=agent_id,
        session=session,
    )
    return properties


@property_router.get("/property/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: str, session: AsyncSession = Depends(get_session)
) -> PropertyResponse:
    property = await property_service.get_property(property_id, session)
    return property


@property_router.get("/featured", response_model=List[PropertyResponse])
async def get_featured_properties(
    session: AsyncSession = Depends(get_session),
):
    properties = await property_service.get_featured_properties(session)
    return properties


@property_router.delete(
    "/property/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_property(
    property_id: str,
    current_user: UserRead = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> None:
    await property_service.delete_property(property_id, session)
    return None


@property_router.put("/property/{id}")
async def update_property(
    id: str,
    title: str = Form(...),
    city: str = Form(...),
    description: str = Form(...),
    address: str = Form(...),
    bedrooms: int = Form(...),
    bathrooms: int = Form(...),
    size: int = Form(...),
    price: float = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    floor: Optional[int] = Form(None),
    type: PropertyType = Form(...),
    sale_or_rent: SaleRent = Form(...),
    agent_id: UUID = Form(...),
    files: List[UploadFile] = Form(...),
    current_user: UserRead = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    property_data = PropertyCreate(
        title=title,
        city=city,
        description=description,
        address=address,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        size=size,
        price=price,
        latitude=latitude,
        longitude=longitude,
        floor=floor,
        type=type,
        sale_or_rent=sale_or_rent,
        agent_id=agent_id,
    )
    await property_service.update_property(id, property_data, files, session)
    return {"message": "Property updated successfully"}


@property_router.patch(
    "/property/{property_id}/featured", response_model=PropertyResponse
)
async def update_featured(
    property_id: str,
    featured_update: FeaturedUpdate,
    current_user: UserRead = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
) -> PropertyResponse:
    updated_property = await property_service.update_featured(
        property_id, featured_update.featured, session
    )
    return updated_property


@property_router.patch("/property/{property_id}/status")
async def update_status(
    property_id: str,
    status_update: StatusUpdate,
    current_user: UserRead = Depends(require_admin),
    session: AsyncSession = Depends(get_session),
):
    await property_service.update_status(property_id, status_update.status, session)
    return {"message": "Property status updated successfully"}
