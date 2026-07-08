import pytest
from fastapi.testclient import TestClient

from app.ai.providers.mock_provider import MockProvider
from app.db import session as database
from app.db.init_db import create_schema, drop_schema
from app.db.seed import seed_demo_data
from app.db.session import configure_database
from app.main import app

configure_database("sqlite+aiosqlite:///./test_nexusagent.db")


@pytest.fixture(autouse=True)
async def reset_store():
    await drop_schema(database.engine)
    await create_schema(database.engine)

    async with database.AsyncSessionLocal() as session:
        await seed_demo_data(session, MockProvider())
    yield


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
async def db_session():
    async with database.AsyncSessionLocal() as session:
        yield session
