import os

import pytest
from sqlalchemy import select

from app.agent.router import route_message
from app.ai.providers.mock_provider import MockProvider
from app.db.init_db import create_schema, drop_schema
from app.db.seed import seed_demo_data
from app.db.session import configure_database
from app.models import tables
from app.rag.ingestion import ingest_text_document
from app.repositories import BusinessRepository, DocumentRepository

pytestmark = pytest.mark.integration


@pytest.fixture()
async def pg_session():
    url = os.getenv("PGVECTOR_TEST_DATABASE_URL")
    if not url:
        pytest.skip("PGVECTOR_TEST_DATABASE_URL is not configured")
    configure_database(url)
    from app.db import session as db_session

    await drop_schema(db_session.engine)
    await create_schema(db_session.engine)
    async with db_session.AsyncSessionLocal() as session:
        await seed_demo_data(session, MockProvider())
        yield session


@pytest.mark.asyncio
async def test_pgvector_document_chunk_search_and_citation(pg_session):
    repo = DocumentRepository(pg_session)
    provider = MockProvider()
    doc = await ingest_text_document("integration_return.md", "Returns are accepted within 30 days of delivery.", provider, repo)
    query_embedding = await provider.embed("return policy")
    chunks = await repo.vector_search(query_embedding, k=3, threshold=0.01)
    assert chunks
    assert any(chunk.document_id == doc.id for chunk in chunks)


@pytest.mark.asyncio
async def test_pgvector_chat_persists_conversation_tool_log_ticket_and_cascade(pg_session):
    provider = MockProvider()
    response = await route_message("Where is order ORD-10001?", None, provider, pg_session)
    assert response.tool_executions[0].tool_name == "get_order_status"

    ticket = await BusinessRepository(pg_session).create_ticket("Integration support issue")
    assert ticket["id"].startswith("TCK-")

    logs = await pg_session.scalar(select(tables.ToolExecutionLog.id).limit(1))
    conversation = await pg_session.scalar(select(tables.Conversation.id).limit(1))
    assert logs is not None
    assert conversation is not None

    repo = DocumentRepository(pg_session)
    document, _ = (await repo.list_documents())[0]
    assert await repo.delete_document(document.id) is True
    remaining = await pg_session.scalar(select(tables.DocumentChunk.id).where(tables.DocumentChunk.document_id == document.id).limit(1))
    assert remaining is None

