from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from security.auth import create_access_token
from core.init_db import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from schemas.token_schema import Token
from typing import Annotated
from services.user_service import user_service


auth_router = APIRouter()


@auth_router.post("/login/")
async def login_for_access_token(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
) -> Token:
    user = await user_service.authenticate_user(
        username=user_data.username, password=user_data.password, session=session
    )
    access_token = create_access_token(data={"sub": str(user.id), "role": user.role})
    return Token(access_token=access_token)
