import time

from app.agent.classifier import classify_intent
from app.ai.providers.base import LLMProvider
from app.rag.retrieval import citations_from_chunks, top_k_chunks
from app.schemas.chat import ChatResponse, Intent, ToolExecution
from app.services.store import store
from app.tools.registry import execute_tool

OUT_OF_SCOPE_TERMS = {"drone", "motorcycle", "insurance", "battery"}


def is_out_of_scope_knowledge_query(message: str) -> bool:
    text = message.lower()
    return any(term in text for term in OUT_OF_SCOPE_TERMS)


async def route_message(message: str, conversation_id: str | None, provider: LLMProvider) -> ChatResponse:
    started = time.perf_counter()
    conversation_id, _ = store.add_message(conversation_id, "user", message)
    intent = classify_intent(message)
    tool_executions: list[ToolExecution] = []
    citations = []
    insufficient_context = False

    if intent.intent == Intent.order_query:
        raw = {"order_id": intent.entities["order_id"]}
        output = await execute_tool("get_order_status", raw)
        tool_executions.append(ToolExecution(tool_name="get_order_status", status="success", input=raw, output=output))
        answer = (
            f"Order: {output.get('order_id')}\n"
            f"Status: {output.get('status')}\n"
            f"Carrier: {output.get('carrier')}\n"
            f"Tracking Number: {output.get('tracking_number')}\n"
            f"Estimated Delivery: {output.get('estimated_delivery')}"
            if output.get("found")
            else output["message"]
        )
    elif intent.intent == Intent.inventory_query:
        product_id = intent.entities.get("product_id", "PRD-001")
        raw = {"product_id": product_id}
        output = await execute_tool("check_inventory", raw)
        tool_executions.append(ToolExecution(tool_name="check_inventory", status="success", input=raw, output=output))
        answer = (
            f"{output.get('product_name', product_id)} inventory: {output.get('quantity')} units, status {output.get('status')}."
            if output.get("found")
            else output["message"]
        )
    elif intent.intent == Intent.product_query:
        raw = {"query": intent.entities.get("query", message)}
        output = await execute_tool("search_products", raw)
        tool_executions.append(ToolExecution(tool_name="search_products", status="success", input=raw, output=output))
        answer = (
            "Matching products: " + ", ".join(item["name"] for item in output["results"])
            if output["results"]
            else "No matching NovaTech products were found."
        )
    elif intent.intent == Intent.create_ticket:
        raw = {"summary": intent.entities.get("summary", message), "category": "technical_support", "priority": "normal"}
        output = await execute_tool("create_support_ticket", raw)
        tool_executions.append(ToolExecution(tool_name="create_support_ticket", status="success", input=raw, output=output))
        answer = f"Support ticket {output['id']} has been created. A human support agent will review: {output['summary']}"
    elif intent.intent == Intent.human_handoff:
        raw = {"reason": intent.entities.get("reason", message), "conversation_id": conversation_id}
        output = await execute_tool("create_handoff_request", raw)
        tool_executions.append(ToolExecution(tool_name="create_handoff_request", status="success", input=raw, output=output))
        answer = f"Human handoff request {output['id']} has been queued."
    else:
        chunks = []
        if not is_out_of_scope_knowledge_query(message):
            query_embedding = await provider.embed(message)
            chunks = top_k_chunks(query_embedding)
        citations = citations_from_chunks(chunks)
        context = "\n\n".join(chunk.content for chunk, _score in chunks)
        insufficient_context = not bool(citations)
        if insufficient_context:
            store.unresolved_questions += 1
        answer = await provider.generate(message, context=context, citations=citations)

    _, message_id = store.add_message(conversation_id, "assistant", answer, intent.intent.value, citations)
    store.response_times_ms.append(int((time.perf_counter() - started) * 1000))
    return ChatResponse(
        conversation_id=conversation_id,
        message_id=message_id,
        answer=answer,
        intent=intent,
        citations=citations,
        tool_executions=tool_executions,
        insufficient_context=insufficient_context,
    )
