import os
from pathlib import Path

import pytest
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError

from alembic import command
from alembic.config import Config
from app.agent.router import route_message
from app.ai.providers.mock_provider import MockProvider
from app.db.init_db import create_schema, drop_schema
from app.db.seed import seed_demo_data
from app.db.session import configure_database
from app.models import tables
from app.rag.ingestion import ingest_text_document
from app.repositories import BusinessRepository, DocumentRepository

pytestmark = pytest.mark.integration


def pgvector_url() -> str:
    url = os.getenv("PGVECTOR_TEST_DATABASE_URL")
    if not url:
        pytest.skip("PGVECTOR_TEST_DATABASE_URL is not configured")
    return url


async def reset_pg_database(engine) -> None:
    await drop_schema(engine)
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS alembic_version"))


@pytest.fixture()
async def pg_session():
    url = pgvector_url()
    configure_database(url)
    from app.db import session as db_session

    await reset_pg_database(db_session.engine)
    await create_schema(db_session.engine)
    async with db_session.AsyncSessionLocal() as session:
        await seed_demo_data(session, MockProvider())
        yield session


@pytest.mark.asyncio
async def test_pgvector_migrations_apply():
    url = pgvector_url()
    configure_database(url)
    from app.db import session as db_session

    await reset_pg_database(db_session.engine)
    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "head")
    async with db_session.AsyncSessionLocal() as session:
        revision = await session.scalar(text("SELECT version_num FROM alembic_version"))
        assert revision == "0002"
        result = await session.execute(select(tables.DocumentChunk.id).limit(1))
        assert result.scalar_one_or_none() is None
    await reset_pg_database(db_session.engine)


@pytest.mark.asyncio
async def test_pgvector_upgrade_from_0001_drops_legacy_64_dim_embeddings():
    url = pgvector_url()
    configure_database(url)
    from app.db import session as db_session

    await reset_pg_database(db_session.engine)
    alembic_ini = Path(__file__).resolve().parents[1] / "alembic.ini"
    config = Config(str(alembic_ini))
    config.set_main_option("sqlalchemy.url", url)
    command.upgrade(config, "0001")
    legacy_vector = "[" + ",".join(["0.1"] * 64) + "]"
    async with db_session.engine.begin() as conn:
        await conn.execute(text("INSERT INTO documents (id, name, status) VALUES ('legacy-doc', 'legacy.md', 'processed')"))
        await conn.execute(
            text(
                "INSERT INTO document_chunks (id, document_id, chunk_index, content, embedding) "
                "VALUES ('legacy-chunk', 'legacy-doc', 0, 'legacy content', :embedding)"
            ),
            {"embedding": legacy_vector},
        )
    command.upgrade(config, "head")
    async with db_session.AsyncSessionLocal() as session:
        revision = await session.scalar(text("SELECT version_num FROM alembic_version"))
        assert revision == "0002"
        assert await session.scalar(select(tables.Document.id).where(tables.Document.id == "legacy-doc")) is None
        assert await session.scalar(select(tables.DocumentChunk.id).where(tables.DocumentChunk.id == "legacy-chunk")) is None
    await drop_schema(db_session.engine)


@pytest.mark.asyncio
async def test_pgvector_document_chunk_search_and_citation(pg_session):
    extension = await pg_session.scalar(text("SELECT extname FROM pg_extension WHERE extname = 'vector'"))
    assert extension == "vector"
    repo = DocumentRepository(pg_session)
    provider = MockProvider()
    unique_phrase = "integrationvectoralpha refund diagnostic marker"
    doc = await ingest_text_document("integration_return.md", f"{unique_phrase} Returns are accepted within 30 days.", provider, repo)
    query_embedding = await provider.embed(unique_phrase)
    assert len(query_embedding) == 256
    chunks = await repo.vector_search(query_embedding, k=5, threshold=0.01)
    assert chunks
    assert any(chunk.document_id == doc.id for chunk in chunks)
    matched = next(chunk for chunk in chunks if chunk.document_id == doc.id)
    assert matched.document_name == "integration_return.md"
    assert unique_phrase in matched.content
    filtered = await repo.vector_search(query_embedding, k=3, threshold=1.01)
    assert filtered == []


@pytest.mark.asyncio
async def test_pgvector_rejects_wrong_embedding_dimension(pg_session):
    await pg_session.execute(text("INSERT INTO documents (id, name, status) VALUES ('bad-dim-doc', 'bad.md', 'processed')"))
    with pytest.raises(SQLAlchemyError):
        await pg_session.execute(
            text(
                "INSERT INTO document_chunks (id, document_id, chunk_index, content, embedding) "
                "VALUES ('bad-dim-chunk', 'bad-dim-doc', 0, 'bad', '[0.1,0.2]')"
            )
        )
        await pg_session.commit()
    await pg_session.rollback()


@pytest.mark.asyncio
async def test_pgvector_chat_persists_conversation_tool_log_ticket_and_cascade(pg_session):
    provider = MockProvider()
    response = await route_message("Where is order ORD-10001?", None, provider, pg_session)
    assert response.tool_executions[0].tool_name == "get_order_status"

    ticket = await BusinessRepository(pg_session).create_ticket("Integration support issue")
    ticket_with_email = await BusinessRepository(pg_session).create_ticket(
        "Integration email issue", customer_email="integration@example.com"
    )
    handoff = await BusinessRepository(pg_session).create_handoff("Integration handoff", response.conversation_id)
    assert ticket["id"].startswith("TCK-")
    assert len(ticket["id"]) == 16
    assert ticket_with_email["customer_email"] == "integration@example.com"
    assert handoff["id"].startswith("HND-")
    assert handoff["conversation_id"] == response.conversation_id

    await BusinessRepository(pg_session).log_tool(
        "integration_failure",
        "failed",
        {"value": "safe"},
        error_code="TOOL_HANDLER_FAILED",
        error_message="Internal tool execution failed.",
    )

    logs = await pg_session.scalar(select(tables.ToolExecutionLog.id).limit(1))
    conversation = await pg_session.scalar(select(tables.Conversation.id).limit(1))
    message_count = await pg_session.scalar(select(text("count(*)")).select_from(tables.Message))
    metrics = await pg_session.scalar(select(tables.RequestMetric.id).limit(1))
    failed_log = await pg_session.scalar(select(tables.ToolExecutionLog).where(tables.ToolExecutionLog.tool_name == "integration_failure"))
    assert logs is not None
    assert conversation is not None
    assert message_count and message_count >= 2
    assert metrics is not None
    assert failed_log is not None
    assert failed_log.error_message == "Internal tool execution failed."

    repo = DocumentRepository(pg_session)
    document, _ = (await repo.list_documents())[0]
    assert await repo.delete_document(document.id) is True
    remaining = await pg_session.scalar(select(tables.DocumentChunk.id).where(tables.DocumentChunk.document_id == document.id).limit(1))
    assert remaining is None
