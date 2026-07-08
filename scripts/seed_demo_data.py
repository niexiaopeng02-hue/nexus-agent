import asyncio

from app.ai.providers.factory import get_provider
from app.db.init_db import create_schema
from app.db.seed import seed_demo_data
from app.db.session import AsyncSessionLocal, engine


async def main() -> None:
    await create_schema(engine)
    async with AsyncSessionLocal() as session:
        await seed_demo_data(session, get_provider())
    print("Seeded NovaTech documents, orders, products, inventory, and support demo data.")


if __name__ == "__main__":
    asyncio.run(main())
