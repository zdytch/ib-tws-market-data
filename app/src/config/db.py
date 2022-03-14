from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel
from .settings import DB_URL

engine = create_async_engine(DB_URL)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

DB = AsyncSession


async def get_db():
    async with Session() as session:
        yield session


async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
