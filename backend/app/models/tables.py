from __future__ import annotations

from datetime import datetime
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import JSON, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class User(Base, TimestampMixin):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    role: Mapped[str] = mapped_column(String(40), default="admin")
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))


class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)


class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(64), ForeignKey("documents.id", ondelete="CASCADE"), index=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    page_number: Mapped[Optional[int]] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float]] = mapped_column(Vector(256))


class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(255))


class Message(Base, TimestampMixin):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String(64), ForeignKey("conversations.id", ondelete="CASCADE"), index=True)
    role: Mapped[str] = mapped_column(String(40))
    content: Mapped[str] = mapped_column(Text)
    intent: Mapped[Optional[str]] = mapped_column(String(80), index=True)
    citations: Mapped[Optional[dict]] = mapped_column(JSON)


class Order(Base, TimestampMixin):
    __tablename__ = "orders"
    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    status: Mapped[str] = mapped_column(String(80), index=True)
    carrier: Mapped[Optional[str]] = mapped_column(String(80))
    tracking_number: Mapped[Optional[str]] = mapped_column(String(80))
    estimated_delivery: Mapped[Optional[str]] = mapped_column(String(40))


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
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    public_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    customer_email: Mapped[Optional[str]] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(80))
    priority: Mapped[str] = mapped_column(String(40))
    status: Mapped[str] = mapped_column(String(40), index=True)
    summary: Mapped[str] = mapped_column(Text)


class HandoffRequest(Base, TimestampMixin):
    __tablename__ = "handoff_requests"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    public_id: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    conversation_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("conversations.id", ondelete="SET NULL"), index=True)
    reason: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), index=True)


class ToolExecutionLog(Base, TimestampMixin):
    __tablename__ = "tool_execution_logs"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    tool_name: Mapped[str] = mapped_column(String(120), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    input: Mapped[dict] = mapped_column(JSON)
    output: Mapped[Optional[dict]] = mapped_column(JSON)
    error_code: Mapped[Optional[str]] = mapped_column(String(80), index=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text)


class RequestMetric(Base, TimestampMixin):
    __tablename__ = "request_metrics"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    conversation_id: Mapped[Optional[str]] = mapped_column(String(64), ForeignKey("conversations.id", ondelete="SET NULL"), index=True)
    intent: Mapped[str] = mapped_column(String(80), index=True)
    total_ms: Mapped[int] = mapped_column(Integer)
    classification_ms: Mapped[int] = mapped_column(Integer, default=0)
    retrieval_ms: Mapped[int] = mapped_column(Integer, default=0)
    llm_ms: Mapped[int] = mapped_column(Integer, default=0)
    tool_ms: Mapped[int] = mapped_column(Integer, default=0)
    citation_count: Mapped[int] = mapped_column(Integer, default=0)
    tool_count: Mapped[int] = mapped_column(Integer, default=0)
    success: Mapped[float] = mapped_column(Float, default=1.0)
