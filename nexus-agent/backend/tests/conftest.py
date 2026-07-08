import pytest
from fastapi.testclient import TestClient

from app.ai.providers.mock_provider import MockProvider
from app.main import app
from app.rag.ingestion import ingest_sample_documents
from app.services.store import store


@pytest.fixture(autouse=True)
async def reset_store():
    store.reset()
    await ingest_sample_documents(MockProvider())
    yield


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
