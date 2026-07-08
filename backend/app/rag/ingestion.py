from pathlib import Path

from app.ai.providers.base import LLMProvider
from app.rag.chunking import paragraph_aware_chunks
from app.rag.parsers import get_parser
from app.repositories import DocumentRepository
from app.services.store import load_sample_texts


async def ingest_text_document(name: str, text: str, provider: LLMProvider, repo: DocumentRepository):
    chunks = []
    for chunk in paragraph_aware_chunks(text):
        embedding = await provider.embed(chunk)
        page_number = 1 if Path(name).suffix.lower() in {".pdf", ".docx"} else None
        chunks.append((chunk, embedding, page_number))
    return await repo.create_document(name=name, chunks=chunks)


async def ingest_binary_document(name: str, content: bytes, provider: LLMProvider, repo: DocumentRepository):
    parsed = get_parser(name).parse(name, content)
    chunks = []
    for section in parsed:
        for chunk in paragraph_aware_chunks(section.text):
            embedding = await provider.embed(chunk)
            chunks.append((chunk, embedding, section.page_number))
    return await repo.create_document(name=name, chunks=chunks)


async def ingest_sample_documents(provider: LLMProvider, repo: DocumentRepository) -> None:
    for name, text in load_sample_texts():
        await ingest_text_document(name, text, provider, repo)
