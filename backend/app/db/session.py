from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings


def _make_engine(url: str):
    return create_async_engine(url, pool_pre_ping=True)


engine = _make_engine(get_settings().database_url)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    async with AsyncSessionLocal() as session:
        yield session


def configure_database(url: str) -> None:
    global engine, AsyncSessionLocal
    engine = _make_engine(url)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

