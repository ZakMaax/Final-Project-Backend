from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from schemas.user_schemas import (
    UserRead,
    UserCreate,
    UserUpdate,
    UserProfileUpdate,
    Role,
)
from core.init_db import get_session
from services.user_service import user_service
from pydantic import EmailStr
from pydantic_extra_types.phone_numbers import PhoneNumber
from typing import Optional, List

user_router = APIRouter()


@user_router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    user = await user_service.get_user(user_id, session)
    return UserRead.model_validate(user.model_dump())


@user_router.post("/", response_model=UserRead, status_code=201)
async def create_user(
    name: str = Form(...),
    username: str = Form(...),
    email: EmailStr = Form(...),
    phone_number: PhoneNumber = Form(...),
    password: str = Form(...),
    role: Role = Form(...),
    avatar: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session),
) -> UserRead:
    user_data = UserCreate(
        name=name,
        username=username,
        email=email,
        phone_number=phone_number,
        hashed_password=password,
        role=role,
    )
    newUser = await user_service.create_user(user_data, avatar, session)
    return newUser


@user_router.get("/agents/", response_model=List[UserRead])
async def get_agents(session: AsyncSession = Depends(get_session)):
    agents = await user_service.get_agents(session)
    return agents


@user_router.get("/", response_model=List[UserRead])
async def get_users(session: AsyncSession = Depends(get_session)):
    users = await user_service.get_users(session)
    return users


@user_router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    name: str = Form(...),
    username: str = Form(...),
    email: EmailStr = Form(...),
    phone_number: PhoneNumber = Form(...),
    role: Role = Form(...),
    avatar: Optional[UploadFile] = File(None),
    session: AsyncSession = Depends(get_session),
):
    user_update_data = UserUpdate(
        name=name,
        username=username,
        email=email,
        phone_number=phone_number,
        role=role,
    )
    return await user_service.update_user(user_id, user_update_data, avatar, session)


@user_router.patch("/profile/{user_id}")
async def update_profile(
    user_id: str,
    data: UserProfileUpdate,
    session: AsyncSession = Depends(get_session),
):
    return await user_service.update_profile(
        user_id, data.username, data.old_password, data.new_password, session
    )


@user_router.delete("/{user_id}", status_code=204)
async def delete_user(
    user_id: str,
    session: AsyncSession = Depends(get_session),
):
    try:
        result = await user_service.delete_user(user_id, session)
        return JSONResponse(content=result, status_code=200)
    except HTTPException as exc:
        return JSONResponse(content={"detail": exc.detail}, status_code=exc.status_code)
    except Exception as exc:
        print(exc)
        return JSONResponse(
            content={"detail": "Internal server error"}, status_code=500
        )
