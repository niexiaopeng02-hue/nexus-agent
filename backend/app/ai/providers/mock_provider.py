import hashlib
import json
import math
import re

from app.ai.providers.base import LLMProvider
from app.core.config import get_settings
from app.schemas.chat import Citation


class MockProvider(LLMProvider):
    async def generate(self, prompt: str, context: str = "", citations: list[Citation] | None = None) -> str:
        text = (context or prompt).lower()
        if not context.strip():
            return (
                "I do not have enough information in the current knowledge base to answer that. "
                "I can create a handoff request for a human support agent."
            )
        if "return" in text:
            return (
                "According to NovaTech's return policy, eligible products may be returned within 30 days of delivery "
                "when they are in good condition and include the required proof of purchase."
            )
        if "warranty" in text:
            return (
                "NovaTech products include a limited warranty for manufacturing defects. "
                "Coverage depends on the product line and proof of purchase."
            )
        if "shipping" in text:
            return (
                "NovaTech shipping timelines depend on destination and stock status. "
                "Most standard shipments include tracking after the order leaves the warehouse."
            )
        return "Based on the retrieved NovaTech knowledge base passages, here is the most relevant answer: " + context[:350]

    async def embed(self, text: str) -> list[float]:
        tokens = re.findall(r"[a-z0-9]+", text.lower())
        dimensions = get_settings().embedding_dimensions
        vector = [0.0] * dimensions
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = digest[0] % len(vector)
            vector[index] += 1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    async def classify_intent(self, message: str) -> str:
        text = message.lower()
        if "malformed" in text:
            return "{not-json"
        if "ambiguous" in text:
            return json.dumps(
                {"intent": "knowledge_query", "confidence": 0.21, "entities": {}, "requires_tool": False, "requires_human": False}
            )
        if "quantum toaster" in text:
            return json.dumps({"intent": "unknown", "confidence": 0.82, "entities": {}, "requires_tool": False, "requires_human": False})
        return json.dumps(
            {"intent": "general_conversation", "confidence": 0.72, "entities": {}, "requires_tool": False, "requires_human": False}
        )
