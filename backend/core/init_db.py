from typing import AsyncGenerator
from sqlmodel import SQLModel
from .config import config
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from models.users import User
from models.properties import Property, PropertyImage
from models.appointments import PropertyAppointment


DATABASE_URL = config.DATABASE_URL

engine = None
AsyncSessionLocal = None


async def init_db():
    global engine, AsyncSessionLocal

    engine = create_async_engine(DATABASE_URL, echo=True, future=True)

    AsyncSessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        autocommit=False,
        expire_on_commit=False,
    )

    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
            print("Database tables created successfully")
        print("Database Connected Successfully")
    except Exception as e:
        print(f"Failed to connect to the database: {e}")


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if AsyncSessionLocal is None:
        raise RuntimeError(
            "Database engine and sessionmaker not initialized. Call init_db() on startup."
        )
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
