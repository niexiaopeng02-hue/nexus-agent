from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(40), default="admin")
    password_hash: Mapped[str | None] = mapped_column(String(255))


class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)


class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    page_number: Mapped[int | None] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(1536))


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))


class Message(Base, TimestampMixin):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(40))
    content: Mapped[str] = mapped_column(Text)
    intent: Mapped[str | None] = mapped_column(String(80), index=True)
    citations: Mapped[dict | None] = mapped_column(JSONB)


class Order(Base, TimestampMixin):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    status: Mapped[str] = mapped_column(String(80), index=True)
    carrier: Mapped[str | None] = mapped_column(String(80))
    tracking_number: Mapped[str | None] = mapped_column(String(80))
    estimated_delivery: Mapped[str | None] = mapped_column(String(40))


class Product(Base, TimestampMixin):
    __tablename__ = "products"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str] = mapped_column(Text)


class Inventory(Base, TimestampMixin):
    __tablename__ = "inventory"
    product_id: Mapped[str] = mapped_column(ForeignKey("products.id"), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(40), index=True)


class SupportTicket(Base, TimestampMixin):
    __tablename__ = "support_tickets"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    category: Mapped[str] = mapped_column(String(80))
    priority: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), index=True)
    summary: Mapped[str] = mapped_column(Text)


class HandoffRequest(Base, TimestampMixin):
    __tablename__ = "handoff_requests"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), index=True)


class ToolExecutionLog(Base, TimestampMixin):
    __tablename__ = "tool_execution_logs"
    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True)
    tool_name: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    input: Mapped[dict] = mapped_column(JSONB)
    output: Mapped[dict | None] = mapped_column(JSONB)
