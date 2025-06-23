import os
import shutil
from typing import Optional
from models.properties import Property, PropertyImage
from sqlalchemy.ext.asyncio.session import AsyncSession
from schemas.property_schemas import PropertyCreate, PropertyResponse, PropertyStatus
from sqlalchemy.orm import selectinload
from sqlalchemy import and_
from sqlmodel import select
from fastapi import status, HTTPException
from models.users import User


class PropertyService:
    async def get_property(
        self, property_id: str, session: AsyncSession
    ) -> PropertyResponse:
        result = await session.execute(
            select(Property)
            .options(
                selectinload(Property.images),  # type: ignore
                selectinload(Property.agent),  # type: ignore
            )
            .where(Property.id == property_id)
        )
        property = result.scalars().first()
        if not property:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Property with id: {property_id} not found",
            )
        prop_dict = property.model_dump()
        prop_dict["images"] = [img.file_name for img in property.images]
        if property.agent:
            prop_dict["agent"] = {
                "id": property.agent.id,
                "name": property.agent.name,
                "email": property.agent.email,
                "phone_number": property.agent.phone_number,
                "avatar_url": getattr(property.agent, "avatar_url", None),
            }
        else:
            prop_dict["agent"] = None
        return PropertyResponse.model_validate(prop_dict)

    async def get_properties(
        self,
        sale_or_rent: Optional[str],
        city: Optional[str],
        min_price: Optional[float],
        max_price: Optional[float],
        type: Optional[str],
        agent_id: Optional[str],
        session: AsyncSession,
    ):
        query = (
            select(Property)
            .options(selectinload(Property.images))  # type: ignore
            .where(Property.status == PropertyStatus.available)
        )
        filters = []
        if sale_or_rent:
            filters.append(Property.sale_or_rent == sale_or_rent)
        if city:
            filters.append(Property.city == city)
        if min_price is not None:
            filters.append(Property.price >= min_price)
        if max_price is not None:
            filters.append(Property.price <= max_price)
        if type:
            filters.append(Property.type == type)
        if agent_id:
            filters.append(Property.agent_id == agent_id)
        if filters:
            query = query.where(and_(*filters))
        result = await session.execute(query)
        properties = result.scalars().all()
        response = []
        for prop in properties:
            prop_dict = prop.model_dump()
            home_images = [
                img.file_name for img in prop.images if img.file_name.startswith("home")
            ]
            prop_dict["images"] = home_images
            response.append(prop_dict)
        return response

    async def get_featured_properties(self, session: AsyncSession):
        query = (
            select(Property)
            .options(selectinload(Property.images))  # type: ignore
            .where(
                Property.featured,
                Property.status == PropertyStatus.available,
            )
        )
        result = await session.execute(query)
        properties = result.scalars().all()
        response = []
        for prop in properties:
            prop_dict = prop.model_dump()
            home_images = [
                img.file_name for img in prop.images if img.file_name.startswith("home")
            ]
            prop_dict["images"] = home_images
            response.append(prop_dict)
        return response

    async def create_property(
        self, property_data: PropertyCreate, files, session: AsyncSession
    ):
        result = await session.execute(
            select(User).where(User.id == property_data.agent_id)
        )
        agent = result.scalars().first()

        if not agent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Agent with ID: {property_data.agent_id} not found.",
            )
        if agent.role != "agent":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,  # Forbidden status
                detail=f"User with ID: {property_data.agent_id} is not authorized to be an agent.",
            )
        new_property = Property(**property_data.model_dump())
        try:
            session.add(new_property)
            await session.commit()
            await session.refresh(new_property)
            property_id = new_property.id

            if files:
                property_folder = f"uploads/properties/{property_id}"
                os.makedirs(property_folder, exist_ok=True)

                for file in files:
                    file_path = os.path.join(property_folder, file.filename)
                    with open(file_path, "wb") as buffer:
                        shutil.copyfileobj(file.file, buffer)

                    image = PropertyImage(
                        file_name=file.filename,
                        property_id=property_id,  # type: ignore
                    )
                    session.add(image)
                await session.commit()

        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create property or upload images: {e}",
            )
        return {"message": "Property Created Successfully"}

    async def delete_property(self, property_id: str, session: AsyncSession) -> None:
        result = await session.execute(
            select(Property).where(Property.id == property_id)
        )
        property = result.scalars().first()

        if property is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Property with id: {property_id} is not found",
            )

        property_folder = f"uploads/properties/{property_id}"
        if os.path.exists(property_folder):
            shutil.rmtree(property_folder)

        await session.delete(property)
        await session.commit()

    async def update_property(
        self,
        id: str,
        property_update_data: PropertyCreate,
        files,
        session: AsyncSession,
    ):
        result = await session.execute(select(Property).where(Property.id == id))
        property_obj = result.scalars().first()
        if not property_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Property with id: {id} not found",
            )

        # Update property fields
        for k, v in property_update_data.model_dump().items():
            setattr(property_obj, k, v)

        # Handle image files
        if files:
            property_folder = f"uploads/properties/{id}"

            # Remove old images from disk
            if os.path.exists(property_folder):
                shutil.rmtree(property_folder)
            os.makedirs(property_folder, exist_ok=True)

            # Remove old PropertyImage records
            await session.execute(
                PropertyImage.__table__.delete().where(PropertyImage.property_id == id)  # type: ignore
            )

            # Save new images and create PropertyImage records
            for file in files:
                file_path = os.path.join(property_folder, file.filename)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                image = PropertyImage(
                    file_name=file.filename,
                    property_id=id,  # type: ignore
                )
                session.add(image)

        await session.commit()
        await session.refresh(property_obj)

    async def update_featured(
        self, property_id: str, featured: bool, session: AsyncSession
    ):
        result = await session.execute(
            select(Property).where(Property.id == property_id)
        )
        property = result.scalars().first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        property.featured = featured
        await session.commit()
        await session.refresh(property)
        return PropertyResponse.model_validate(property)

    async def update_status(
        self, property_id: str, status: PropertyStatus, session: AsyncSession
    ):
        result = await session.execute(
            select(Property).where(Property.id == property_id)
        )
        property = result.scalars().first()
        if not property:
            raise HTTPException(status_code=404, detail="Property not found")
        property.status = PropertyStatus(status)
        await session.commit()
        await session.refresh(property)


property_service = PropertyService()
