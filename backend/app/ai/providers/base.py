from abc import ABC, abstractmethod

from app.schemas.chat import Citation


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, prompt: str, context: str = "", citations: list[Citation] | None = None) -> str:
        raise NotImplementedError

    @abstractmethod
    async def embed(self, text: str) -> list[float]:
        raise NotImplementedError
