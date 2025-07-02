import os
import shutil
from models.users import User
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError
from schemas.user_schemas import UserRead, UserCreate, UserUpdate
from sqlmodel import select
from fastapi import status, HTTPException
from security.security import hash_password, verify_password


class UserService:
    async def create_user(
        self, user_data: UserCreate, avatar, session: AsyncSession
    ) -> UserRead:
        web_avatar_url_for_db: str | None = None
        if avatar:
            user_folder = f"uploads/avatars/{user_data.username}"
            try:
                os.makedirs(user_folder, exist_ok=True)
                avatar_path = os.path.join(
                    user_folder, "avatar" + os.path.splitext(avatar.filename)[1]
                )

                with open(avatar_path, "wb") as buffer:
                    shutil.copyfileobj(avatar.file, buffer)
                web_avatar_url_for_db = f"/{avatar_path.replace('\\', '/')}"

            except Exception as e:
                print(f"Error saving avatar: {e}")
                raise HTTPException(
                    status_code=500, detail="Failed to save avatar image"
                )

        new_user_data = user_data.model_dump()
        new_user_data["hashed_password"] = hash_password(
            new_user_data.pop("hashed_password")
        )
        if web_avatar_url_for_db:
            new_user_data["avatar_url"] = web_avatar_url_for_db
        saved_user = User(**new_user_data)

        session.add(saved_user)

        try:
            await session.commit()
        except IntegrityError as e:
            await session.rollback()

            if "email" in str(e.orig):
                raise HTTPException(
                    status_code=409,
                    detail="A user with this email already exists",
                )
            if "phone_number" in str(e.orig):
                raise HTTPException(
                    status_code=409,
                    detail="A user with this phone number already exists",
                )
            if "username" in str(e.orig):
                raise HTTPException(
                    status_code=409,
                    detail="A user with this username already exists",
                )
            raise HTTPException(status_code=500, detail="Failed to create user")

        await session.refresh(saved_user)

        return UserRead.model_validate(saved_user.model_dump())

    async def authenticate_user(
        self, username: str, password: str, session: AsyncSession
    ) -> UserRead:
        result = await session.execute(select(User).where(User.username == username))

        user = result.scalars().first()

        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return UserRead.model_validate(user.model_dump())

    async def get_agents(self, session: AsyncSession):
        statement = select(User).where(User.role == "agent")
        result = await session.execute(statement)
        agents = result.scalars().all()

        return agents

    async def get_users(self, session: AsyncSession):
        query = select(User)
        result = await session.execute(query)
        users = result.scalars().all()

        return users

    async def get_user(self, id, session: AsyncSession):
        user = await session.get(User, id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User does not exist"
            )
        return user

    async def update_user(
        self, user_id, user_update_data: UserUpdate, avatar, session: AsyncSession
    ):
        user = await self.get_user(user_id, session)
        web_avatar_url_for_db: str | None = None

        # Handle avatar update
        if avatar:
            # Remove old avatar if exists
            if user.avatar_url:
                old_avatar_path = user.avatar_url.lstrip("/")
                if os.path.exists(old_avatar_path):
                    os.remove(old_avatar_path)
            user_folder = f"uploads/avatars/{user_update_data.username}"
            os.makedirs(user_folder, exist_ok=True)
            avatar_path = os.path.join(
                user_folder, "avatar" + os.path.splitext(avatar.filename)[1]
            )
            with open(avatar_path, "wb") as buffer:
                shutil.copyfileobj(avatar.file, buffer)
            web_avatar_url_for_db = f"/{avatar_path.replace('\\', '/')}"

        # Update user fields
        for k, v in user_update_data.model_dump().items():
            if k == "hashed_password":
                v = hash_password(v)
            setattr(user, k, v)
        if web_avatar_url_for_db:
            user.avatar_url = web_avatar_url_for_db

        await session.commit()
        await session.refresh(user)
        return UserRead.model_validate(user.model_dump())

    async def update_profile(
        self,
        user_id: str,
        username: str,
        old_password: str,
        new_password: str,
        session: AsyncSession,
    ):
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        # Check old password
        if not verify_password(old_password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Old password is incorrect")
        # Update username and password
        user.username = username
        user.hashed_password = hash_password(new_password)
        await session.commit()
        await session.refresh(user)
        return {"message": "Profile updated successfully"}

    async def delete_user(self, user_id, session: AsyncSession):
        user = await self.get_user(user_id, session)
        if user.avatar_url:
            old_avatar_path = user.avatar_url.lstrip("/")
            old_avatar_folder = os.path.dirname(old_avatar_path)
            if os.path.exists(old_avatar_folder):
                shutil.rmtree(old_avatar_folder)
        await session.delete(user)
        await session.commit()
        return {"detail": f'User "{user.username}" deleted successfully'}


user_service = UserService()
