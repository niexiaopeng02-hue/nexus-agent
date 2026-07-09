import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.classifier import classify_message
from app.ai.providers.base import LLMProvider
from app.core.config import get_settings
from app.repositories import BusinessRepository, ConversationRepository, DocumentRepository, citations_from_retrieved
from app.schemas.chat import ChatResponse, Intent, ToolExecution
from app.tools.registry import ToolExecutionError, execute_tool


async def route_message(message: str, conversation_id: str | None, provider: LLMProvider, session: AsyncSession) -> ChatResponse:
    started = time.perf_counter()
    conversations = ConversationRepository(session)
    documents = DocumentRepository(session)
    business = BusinessRepository(session)
    conversation_id, _ = await conversations.add_message(conversation_id, "user", message)
    classification_started = time.perf_counter()
    intent = await classify_message(message, provider)
    classification_ms = int((time.perf_counter() - classification_started) * 1000)
    retrieval_ms = 0
    llm_ms = 0
    tool_ms = 0
    tool_executions: list[ToolExecution] = []
    citations = []
    insufficient_context = False
    success = True

    async def run_tool(tool_name: str, raw_input: dict) -> dict | None:
        nonlocal tool_ms, success
        tool_started = time.perf_counter()
        try:
            output = await execute_tool(business, tool_name, raw_input)
            tool_executions.append(ToolExecution(tool_name=tool_name, status="success", input=raw_input, output=output))
            return output
        except ToolExecutionError as exc:
            success = False
            tool_executions.append(
                ToolExecution(
                    tool_name=tool_name,
                    status="failed",
                    input=raw_input,
                    error_code=exc.code,
                    error_message=exc.message,
                    error=exc.message,
                )
            )
            return None
        finally:
            tool_ms += int((time.perf_counter() - tool_started) * 1000)

    if intent.intent == Intent.order_query:
        raw = {"order_id": intent.entities["order_id"]}
        output = await run_tool("get_order_status", raw)
        answer = (
            f"Order: {output.get('order_id')}\n"
            f"Status: {output.get('status')}\n"
            f"Carrier: {output.get('carrier')}\n"
            f"Tracking Number: {output.get('tracking_number')}\n"
            f"Estimated Delivery: {output.get('estimated_delivery')}"
            if output and output.get("found")
            else (output["message"] if output else "I could not look up that order right now.")
        )
    elif intent.intent == Intent.inventory_query:
        product_id = intent.entities.get("product_id", "PRD-001")
        raw = {"product_id": product_id}
        output = await run_tool("check_inventory", raw)
        answer = (
            f"{output.get('product_name', product_id)} inventory: {output.get('quantity')} units, status {output.get('status')}."
            if output and output.get("found")
            else (output["message"] if output else "I could not check inventory right now.")
        )
    elif intent.intent == Intent.product_query:
        raw = {"query": intent.entities.get("query", message)}
        output = await run_tool("search_products", raw)
        answer = (
            "Matching products: " + ", ".join(item["name"] for item in output["results"])
            if output and output["results"]
            else ("No matching NovaTech products were found." if output else "I could not search products right now.")
        )
    elif intent.intent == Intent.create_ticket:
        raw = {"summary": intent.entities.get("summary", message), "category": "technical_support", "priority": "normal"}
        output = await run_tool("create_support_ticket", raw)
        answer = (
            f"Support ticket {output['id']} has been created. A human support agent will review: {output['summary']}"
            if output
            else "I could not create a support ticket right now."
        )
    elif intent.intent == Intent.human_handoff:
        raw = {"reason": intent.entities.get("reason", message), "conversation_id": conversation_id}
        output = await run_tool("create_handoff_request", raw)
        answer = f"Human handoff request {output['id']} has been queued." if output else "I could not queue a human handoff right now."
    else:
        retrieval_started = time.perf_counter()
        query_embedding = await provider.embed(message)
        chunks = await documents.vector_search(query_embedding, threshold=get_settings().rag_similarity_threshold)
        retrieval_ms = int((time.perf_counter() - retrieval_started) * 1000)
        citations = citations_from_retrieved(chunks)
        context = "\n\n".join(chunk.content for chunk in chunks)
        insufficient_context = not bool(citations)
        llm_started = time.perf_counter()
        answer = await provider.generate(message, context=context, citations=citations)
        llm_ms = int((time.perf_counter() - llm_started) * 1000)

    _, message_id = await conversations.add_message(conversation_id, "assistant", answer, intent.intent.value, citations)
    await business.log_request_metric(
        conversation_id=conversation_id,
        intent=intent.intent.value,
        total_ms=int((time.perf_counter() - started) * 1000),
        classification_ms=classification_ms,
        retrieval_ms=retrieval_ms,
        llm_ms=llm_ms,
        tool_ms=tool_ms,
        citation_count=len(citations),
        tool_count=len(tool_executions),
        success=success,
    )
    return ChatResponse(
        conversation_id=conversation_id,
        message_id=message_id,
        answer=answer,
        intent=intent,
        citations=citations,
        tool_executions=tool_executions,
        insufficient_context=insufficient_context,
    )
