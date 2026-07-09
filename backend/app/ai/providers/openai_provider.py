from app.ai.providers.base import LLMProvider
from app.core.config import get_settings
from app.schemas.chat import Citation


class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: str) -> None:
        self.api_key = api_key

    async def generate(self, prompt: str, context: str = "", citations: list[Citation] | None = None) -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)
        response = await client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "Answer only from provided context. If context is insufficient, say so clearly."},
                {"role": "user", "content": f"Context:\n{context}\n\nQuestion:\n{prompt}"},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    async def embed(self, text: str) -> list[float]:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)
        response = await client.embeddings.create(
            model="text-embedding-3-small",
            input=text,
            dimensions=get_settings().embedding_dimensions,
        )
        return response.data[0].embedding

    async def classify_intent(self, message: str) -> str:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(api_key=self.api_key)
        response = await client.chat.completions.create(
            model="gpt-4.1-mini",
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Return only JSON with keys intent, confidence, entities, requires_tool, requires_human. "
                        "Supported intents: knowledge_query, order_query, product_query, inventory_query, refund_request, "
                        "technical_support, create_ticket, human_handoff, general_conversation, unknown."
                    ),
                },
                {"role": "user", "content": message},
            ],
            temperature=0,
        )
        return response.choices[0].message.content or "{}"
