from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.base import LLMProvider
from app.models import tables
from app.rag.ingestion import ingest_text_document
from app.repositories import DocumentRepository
from app.services.store import load_sample_texts


async def seed_business_data(session: AsyncSession) -> None:
    if await session.get(tables.Order, "ORD-10001"):
        return
    session.add_all(
        [
            tables.Order(
                id="ORD-10001",
                status="Shipped",
                carrier="DHL",
                tracking_number="TEST123456",
                estimated_delivery="2026-07-12",
            ),
            tables.Order(id="ORD-10002", status="Processing", carrier=None, tracking_number=None, estimated_delivery="2026-07-15"),
            tables.Product(id="PRD-001", name="Wireless Headphones", description="Noise-reducing Bluetooth headphones from NovaTech."),
            tables.Product(id="PRD-002", name="Smart Keyboard", description="Low-profile programmable keyboard for office and travel."),
            tables.Inventory(product_id="PRD-001", quantity=25, status="in_stock"),
            tables.Inventory(product_id="PRD-002", quantity=0, status="out_of_stock"),
        ]
    )
    await session.commit()


async def seed_knowledge_base(session: AsyncSession, provider: LLMProvider) -> None:
    existing = await session.scalar(select(tables.Document.id).limit(1))
    if existing:
        return
    repo = DocumentRepository(session)
    for name, text in load_sample_texts():
        await ingest_text_document(name, text, provider, repo)


async def seed_demo_data(session: AsyncSession, provider: LLMProvider) -> None:
    await seed_business_data(session)
    await seed_knowledge_base(session, provider)

