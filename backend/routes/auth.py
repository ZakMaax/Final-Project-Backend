from fastapi import APIRouter, Depends, HTTPException, Body
import jwt
from jwt.exceptions import InvalidTokenError
from fastapi.security import OAuth2PasswordRequestForm
from security.auth import create_access_token, create_refresh_token
from core.init_db import get_session
from sqlmodel.ext.asyncio.session import AsyncSession
from schemas.token_schema import Token
from typing import Annotated
from services.user_service import user_service
from core.config import config
import datetime

SECRET_KEY = config.SECRET_KEY
ALGORITHM = config.JWT_ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = config.ACCESS_TOKEN_EXPIRE_MINUTES


auth_router = APIRouter()


@auth_router.post("/login/")
async def login_for_access_token(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
) -> Token:
    user = await user_service.authenticate_user(
        username=user_data.username, password=user_data.password, session=session
    )
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "role": user.role,
        }
    )

    refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "role": user.role,
            "name": user.name,
            "avatar": user.avatar_url,
        }
    )
    return Token(access_token=access_token, refresh_token=refresh_token)


@auth_router.post("/refresh")
async def refresh_access_token(refresh_token: str = Body(..., embed=True)):
    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        user_id = payload.get("sub")
        role = payload.get("role")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(
        data={"sub": user_id, "role": role},
        expires_delta=datetime.timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": new_access_token, "token_type": "bearer"}
