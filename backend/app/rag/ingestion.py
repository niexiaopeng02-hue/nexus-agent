from pathlib import Path

from app.ai.providers.base import LLMProvider
from app.rag.chunking import paragraph_aware_chunks
from app.services.store import Document, load_sample_texts, store


async def ingest_text_document(name: str, text: str, provider: LLMProvider) -> Document:
    chunks = []
    for chunk in paragraph_aware_chunks(text):
        embedding = await provider.embed(chunk)
        page_number = 1 if Path(name).suffix.lower() in {".pdf", ".docx"} else None
        chunks.append((chunk, embedding, page_number))
    return store.add_document(name=name, chunks=chunks)


async def ingest_sample_documents(provider: LLMProvider) -> None:
    if store.documents:
        return
    for name, text in load_sample_texts():
        await ingest_text_document(name, text, provider)
