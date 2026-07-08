from app.ai.providers.base import LLMProvider
from app.ai.providers.mock_provider import MockProvider
from app.ai.providers.openai_provider import OpenAIProvider
from app.core.config import get_settings


def get_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_provider.lower() == "openai" and settings.openai_api_key:
        return OpenAIProvider(settings.openai_api_key)
    return MockProvider()
