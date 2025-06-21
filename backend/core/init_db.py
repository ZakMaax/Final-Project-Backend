from .config import config
from sqlmodel import SQLModel, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.orm import sessionmaker
from models.properties import Property
from models.users import User

DATABASE_URL = config.DATABASE_URL

engine = AsyncEngine(create_engine(url=DATABASE_URL, echo=True, future=True))
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session():
    async with async_session() as session:
        yield session
