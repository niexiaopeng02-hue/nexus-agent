from app.ai.providers.base import LLMProvider
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
        response = await client.embeddings.create(model="text-embedding-3-small", input=text)
        return response.data[0].embedding
