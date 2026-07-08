from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.schemas.chat import Citation, MessageView


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Chunk:
    id: str
    document_id: str
    document_name: str
    chunk_index: int
    content: str
    embedding: list[float]
    page_number: int | None = None


@dataclass
class Document:
    id: str
    name: str
    status: str = "processed"
    chunk_count: int = 0
    uploaded_at: str = field(default_factory=now_iso)


@dataclass
class Conversation:
    id: str
    title: str
    created_at: str = field(default_factory=now_iso)
    messages: list[MessageView] = field(default_factory=list)


class DemoStore:
    def __init__(self) -> None:
        self.documents: dict[str, Document] = {}
        self.chunks: list[Chunk] = []
        self.conversations: dict[str, Conversation] = {}
        self.orders = {
            "ORD-10001": {
                "order_id": "ORD-10001",
                "status": "Shipped",
                "carrier": "DHL",
                "tracking_number": "TEST123456",
                "estimated_delivery": "2026-07-12",
            },
            "ORD-10002": {
                "order_id": "ORD-10002",
                "status": "Processing",
                "carrier": None,
                "tracking_number": None,
                "estimated_delivery": "2026-07-15",
            },
        }
        self.products = {
            "PRD-001": {
                "product_id": "PRD-001",
                "name": "Wireless Headphones",
                "description": "Noise-reducing Bluetooth headphones from NovaTech.",
            },
            "PRD-002": {
                "product_id": "PRD-002",
                "name": "Smart Keyboard",
                "description": "Low-profile programmable keyboard for office and travel.",
            },
        }
        self.inventory = {
            "PRD-001": {"product_id": "PRD-001", "quantity": 25, "status": "in_stock"},
            "PRD-002": {"product_id": "PRD-002", "quantity": 0, "status": "out_of_stock"},
        }
        self.tickets: dict[str, dict] = {}
        self.handoffs: dict[str, dict] = {}
        self.tool_logs: list[dict] = []
        self.response_times_ms: list[int] = []
        self.unresolved_questions = 0

    def reset(self) -> None:
        self.__init__()

    def add_document(self, name: str, chunks: list[tuple[str, list[float], int | None]]) -> Document:
        document_id = str(uuid4())
        document = Document(id=document_id, name=name, chunk_count=len(chunks))
        self.documents[document_id] = document
        for index, (content, embedding, page_number) in enumerate(chunks):
            self.chunks.append(Chunk(str(uuid4()), document_id, name, index, content, embedding, page_number))
        return document

    def delete_document(self, document_id: str) -> bool:
        if document_id not in self.documents:
            return False
        del self.documents[document_id]
        self.chunks = [chunk for chunk in self.chunks if chunk.document_id != document_id]
        return True

    def add_message(
        self, conversation_id: str | None, role: str, content: str, intent: str | None = None, citations: list[Citation] | None = None
    ) -> tuple[str, str]:
        if not conversation_id or conversation_id not in self.conversations:
            conversation_id = str(uuid4())
            self.conversations[conversation_id] = Conversation(conversation_id, content[:60] or "Conversation")
        message_id = str(uuid4())
        message = MessageView(id=message_id, role=role, content=content, intent=intent, citations=citations or [], created_at=now_iso())
        self.conversations[conversation_id].messages.append(message)
        return conversation_id, message_id

    def create_ticket(
        self, summary: str, category: str = "technical_support", priority: str = "normal", customer_email: str | None = None
    ) -> dict:
        ticket_id = f"TCK-{10000 + len(self.tickets) + 1}"
        ticket = {
            "id": ticket_id,
            "category": category,
            "priority": priority,
            "status": "open",
            "summary": summary,
            "customer_email": customer_email,
            "created_at": now_iso(),
        }
        self.tickets[ticket_id] = ticket
        return ticket

    def create_handoff(self, reason: str, conversation_id: str | None = None) -> dict:
        handoff_id = f"HND-{10000 + len(self.handoffs) + 1}"
        handoff = {"id": handoff_id, "reason": reason, "conversation_id": conversation_id, "status": "queued", "created_at": now_iso()}
        self.handoffs[handoff_id] = handoff
        return handoff


store = DemoStore()


def load_sample_texts() -> list[tuple[str, str]]:
    root = Path(__file__).resolve().parents[3] / "sample_data"
    return [(path.name, path.read_text(encoding="utf-8")) for path in sorted(root.glob("*.md"))]
