import asyncio

from app.ai.providers.factory import get_provider
from app.rag.ingestion import ingest_sample_documents
from app.services.store import store


async def main() -> None:
    await ingest_sample_documents(get_provider())
    print(f"Seeded {len(store.documents)} documents and {len(store.chunks)} chunks")
    print(f"Demo orders: {', '.join(store.orders)}")
    print(f"Demo products: {', '.join(store.products)}")


if __name__ == "__main__":
    asyncio.run(main())

