import pytest

from app.agent.classifier import classify_intent, classify_message
from app.agent.router import route_message
from app.ai.providers.mock_provider import MockProvider
from app.repositories import BusinessRepository
from app.schemas.chat import Intent
from app.tools.registry import execute_tool


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


@pytest.mark.asyncio
async def test_handoff_tool(db_session):
    output = await execute_tool(BusinessRepository(db_session), "create_handoff_request", {"reason": "Need human help"})
    assert output["id"].startswith("HND-")


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
