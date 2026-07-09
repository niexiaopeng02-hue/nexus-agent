import pytest
from sqlalchemy import func, select

from app.agent.classifier import classify_intent, classify_message
from app.agent.router import route_message
from app.ai.providers.mock_provider import MockProvider
from app.db.seed import seed_demo_data
from app.models import tables
from app.repositories import BusinessRepository
from app.schemas.chat import Intent
from app.tools.registry import ToolHandlerError, ToolInputError, ToolNotFoundError, execute_tool


def test_order_intent_extracts_id():
    result = classify_intent("Where is order ORD-10001?")
    assert result.intent == Intent.order_query
    assert result.entities["order_id"] == "ORD-10001"
    assert result.requires_tool is True


def test_inventory_intent_extracts_product():
    result = classify_intent("Is the Wireless Headphones product in stock?")
    assert result.intent == Intent.inventory_query
    assert result.entities["product_id"] == "PRD-001"


def test_ticket_intent_requests_human():
    result = classify_intent("My keyboard stopped working. Please create a support ticket.")
    assert result.intent == Intent.create_ticket
    assert result.requires_human is True


@pytest.mark.asyncio
async def test_malformed_model_output_falls_back_unknown():
    result = await classify_message("malformed classifier payload please", MockProvider())
    assert result.intent == Intent.unknown


@pytest.mark.asyncio
async def test_low_confidence_falls_back_unknown():
    result = await classify_message("ambiguous request without enough signal", MockProvider())
    assert result.intent == Intent.unknown


@pytest.mark.asyncio
async def test_unknown_intent_from_structured_classifier():
    result = await classify_message("quantum toaster calibration", MockProvider())
    assert result.intent == Intent.unknown


@pytest.mark.asyncio
async def test_order_tool_success(db_session):
    output = await execute_tool(BusinessRepository(db_session), "get_order_status", {"order_id": "ORD-10001"})
    assert output["status"] == "Shipped"


@pytest.mark.asyncio
async def test_inventory_tool_success(db_session):
    output = await execute_tool(BusinessRepository(db_session), "check_inventory", {"product_id": "PRD-001"})
    assert output["quantity"] == 25


@pytest.mark.asyncio
async def test_product_search_tool(db_session):
    output = await execute_tool(BusinessRepository(db_session), "search_products", {"query": "keyboard"})
    assert output["results"][0]["product_id"] == "PRD-002"


@pytest.mark.asyncio
async def test_ticket_creation_tool(db_session):
    output = await execute_tool(BusinessRepository(db_session), "create_support_ticket", {"summary": "Device stopped working"})
    assert output["id"].startswith("TCK-")
    assert len(output["id"]) == len("TCK-") + 12


@pytest.mark.asyncio
async def test_handoff_tool(db_session):
    output = await execute_tool(BusinessRepository(db_session), "create_handoff_request", {"reason": "Need human help"})
    assert output["id"].startswith("HND-")
    assert len(output["id"]) == len("HND-") + 12


@pytest.mark.asyncio
async def test_ticket_public_ids_are_unique_under_fast_creation(db_session):
    repo = BusinessRepository(db_session)
    ids = [(await repo.create_ticket(f"Bulk ticket {index}"))["id"] for index in range(100)]
    assert len(ids) == len(set(ids))
    assert all(item.startswith("TCK-") and len(item) == 16 for item in ids)


@pytest.mark.asyncio
async def test_handoff_public_ids_are_unique_under_fast_creation(db_session):
    repo = BusinessRepository(db_session)
    ids = [(await repo.create_handoff(f"Bulk handoff {index}"))["id"] for index in range(100)]
    assert len(ids) == len(set(ids))
    assert all(item.startswith("HND-") and len(item) == 16 for item in ids)


@pytest.mark.asyncio
async def test_mock_embedding_uses_configured_dimension():
    embedding = await MockProvider().embed("return policy")
    assert len(embedding) == 256


@pytest.mark.asyncio
async def test_seed_demo_data_is_idempotent(db_session):
    before_documents = await db_session.scalar(select(func.count()).select_from(tables.Document))
    before_orders = await db_session.scalar(select(func.count()).select_from(tables.Order))
    await seed_demo_data(db_session, MockProvider())
    after_documents = await db_session.scalar(select(func.count()).select_from(tables.Document))
    after_orders = await db_session.scalar(select(func.count()).select_from(tables.Order))
    assert after_documents == before_documents
    assert after_orders == before_orders


@pytest.mark.asyncio
async def test_unknown_tool_is_logged_as_failure(db_session):
    repo = BusinessRepository(db_session)
    with pytest.raises(ToolNotFoundError):
        await execute_tool(repo, "unknown_tool", {"value": "x"})
    log = await db_session.scalar(select(tables.ToolExecutionLog).where(tables.ToolExecutionLog.tool_name == "unknown_tool"))
    assert log is not None
    assert log.status == "failed"
    assert log.error_code == "TOOL_NOT_FOUND"


@pytest.mark.asyncio
async def test_invalid_tool_input_is_logged_as_failure(db_session):
    repo = BusinessRepository(db_session)
    with pytest.raises(ToolInputError):
        await execute_tool(repo, "get_order_status", {})
    log = await db_session.scalar(select(tables.ToolExecutionLog).where(tables.ToolExecutionLog.error_code == "TOOL_INPUT_INVALID"))
    assert log is not None
    assert log.error_message == "Tool input did not match its schema."


@pytest.mark.asyncio
async def test_tool_handler_exception_is_logged_as_failure(db_session, monkeypatch):
    async def broken_get_order(*_args):
        raise RuntimeError("database outage with sensitive connection detail")

    from app.tools import registry

    original = registry.TOOLS["get_order_status"]
    monkeypatch.setitem(registry.TOOLS, "get_order_status", original.model_copy(update={"handler": broken_get_order}))
    repo = BusinessRepository(db_session)
    with pytest.raises(ToolHandlerError):
        await execute_tool(repo, "get_order_status", {"order_id": "ORD-10001"})
    log = await db_session.scalar(select(tables.ToolExecutionLog).where(tables.ToolExecutionLog.error_code == "TOOL_HANDLER_FAILED"))
    assert log is not None
    assert log.error_message == "Internal tool execution failed."
    assert "secret" not in log.error_message


@pytest.mark.asyncio
async def test_chat_api_tool_failure_returns_safe_message(db_session, monkeypatch):
    async def broken_get_order(*_args):
        raise RuntimeError("driver exception with password=secret")

    from app.tools import registry

    original = registry.TOOLS["get_order_status"]
    monkeypatch.setitem(registry.TOOLS, "get_order_status", original.model_copy(update={"handler": broken_get_order}))
    response = await route_message("Where is order ORD-10001?", None, MockProvider(), db_session)
    assert response.tool_executions[0].status == "failed"
    assert response.tool_executions[0].error_message == "Internal tool execution failed."
    assert "secret" not in response.answer


@pytest.mark.asyncio
async def test_rag_knowledge_query_has_citation(db_session):
    response = await route_message("What is NovaTech's return policy?", None, MockProvider(), db_session)
    assert response.intent.intent == Intent.knowledge_query
    assert response.citations
    assert "30 days" in response.answer


@pytest.mark.asyncio
async def test_no_context_behavior_for_unrelated_question(db_session):
    response = await route_message("Explain commercial drone insurance underwriting exclusions", None, MockProvider(), db_session)
    assert response.insufficient_context is True
    assert "do not have enough information" in response.answer.lower()


@pytest.mark.asyncio
async def test_route_message_persists_request_metrics(db_session):
    response = await route_message("What is NovaTech's return policy?", None, MockProvider(), db_session)
    metric = await db_session.scalar(select(tables.RequestMetric).where(tables.RequestMetric.conversation_id == response.conversation_id))
    assert metric is not None
    assert metric.intent == "knowledge_query"
    assert metric.citation_count == len(response.citations)
    assert metric.success is True
