from sqlalchemy.ext.asyncio import AsyncEngine

from app.models.base import Base


async def create_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        if engine.url.get_backend_name().startswith("postgresql"):
            await conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector")
        await conn.run_sync(Base.metadata.create_all)


async def drop_schema(engine: AsyncEngine) -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

