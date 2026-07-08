import re

from app.schemas.chat import Intent, IntentResult

ORDER_RE = re.compile(r"\bORD-\d{5}\b", re.I)


def classify_intent(message: str) -> IntentResult:
    text = message.lower()
    entities: dict[str, str] = {}
    order_match = ORDER_RE.search(message)
    if order_match:
        entities["order_id"] = order_match.group(0).upper()
        return IntentResult(intent=Intent.order_query, confidence=0.97, entities=entities, requires_tool=True)
    if any(word in text for word in ("inventory", "in stock", "available", "stock")):
        if "keyboard" in text:
            entities["product_id"] = "PRD-002"
        elif "headphone" in text or "product x" in text or "wireless" in text:
            entities["product_id"] = "PRD-001"
        return IntentResult(intent=Intent.inventory_query, confidence=0.9, entities=entities, requires_tool=True)
    if any(word in text for word in ("ticket", "stopped working", "support", "broken", "not working")):
        return IntentResult(
            intent=Intent.create_ticket, confidence=0.88, entities={"summary": message}, requires_tool=True, requires_human=True
        )
    if "human" in text or "agent" in text or "handoff" in text:
        return IntentResult(
            intent=Intent.human_handoff, confidence=0.86, entities={"reason": message}, requires_tool=True, requires_human=True
        )
    if any(word in text for word in ("return", "refund", "policy", "warranty", "shipping", "faq", "insurance", "drone")):
        return IntentResult(intent=Intent.knowledge_query, confidence=0.86, entities={"query": message})
    if any(word in text for word in ("product", "headphones", "keyboard")):
        return IntentResult(intent=Intent.product_query, confidence=0.82, entities={"query": message}, requires_tool=True)
    if len(text.split()) <= 2:
        return IntentResult(intent=Intent.general_conversation, confidence=0.72)
    return IntentResult(intent=Intent.knowledge_query, confidence=0.62, entities={"query": message})
