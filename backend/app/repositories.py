from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import tables
from app.schemas.chat import Citation, MessageView


@dataclass
class RetrievedChunk:
    id: str
    document_id: str
    document_name: str
    chunk_index: int
    content: str
    score: float
    page_number: int | None = None


class DocumentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_document(self, name: str, chunks: list[tuple[str, list[float], int | None]]) -> tables.Document:
        document = tables.Document(id=str(uuid4()), name=name, status="processed")
        self.session.add(document)
        await self.session.flush()
        for index, (content, embedding, page_number) in enumerate(chunks):
            self.session.add(
                tables.DocumentChunk(
                    id=str(uuid4()),
                    document_id=document.id,
                    chunk_index=index,
                    page_number=page_number,
                    content=content,
                    embedding=embedding,
                )
            )
        await self.session.commit()
        document.chunk_count = len(chunks)  # type: ignore[attr-defined]
        return document

    async def list_documents(self) -> list[tuple[tables.Document, int]]:
        stmt = (
            select(tables.Document, func.count(tables.DocumentChunk.id))
            .outerjoin(tables.DocumentChunk, tables.DocumentChunk.document_id == tables.Document.id)
            .group_by(tables.Document.id)
            .order_by(tables.Document.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return [(row[0], int(row[1])) for row in result.all()]

    async def get_document(self, document_id: str) -> tuple[tables.Document, int] | None:
        stmt = (
            select(tables.Document, func.count(tables.DocumentChunk.id))
            .outerjoin(tables.DocumentChunk, tables.DocumentChunk.document_id == tables.Document.id)
            .where(tables.Document.id == document_id)
            .group_by(tables.Document.id)
        )
        result = await self.session.execute(stmt)
        row = result.one_or_none()
        return (row[0], int(row[1])) if row else None

    async def delete_document(self, document_id: str) -> bool:
        result = await self.session.execute(delete(tables.Document).where(tables.Document.id == document_id))
        await self.session.commit()
        return bool(result.rowcount)

    async def reprocess_document(self, document_id: str) -> tuple[tables.Document, int] | None:
        found = await self.get_document(document_id)
        if not found:
            return None
        document, count = found
        document.status = "processed"
        await self.session.commit()
        return document, count

    async def vector_search(self, embedding: list[float], k: int = 4, threshold: float = 0.18) -> list[RetrievedChunk]:
        if self.session.bind and self.session.bind.dialect.name == "postgresql":
            distance = tables.DocumentChunk.embedding.cosine_distance(embedding)
            stmt = (
                select(
                    tables.DocumentChunk,
                    tables.Document.name,
                    (1 - distance).label("score"),
                )
                .join(tables.Document, tables.Document.id == tables.DocumentChunk.document_id)
                .where(distance <= 1 - threshold)
                .order_by(distance)
                .limit(k)
            )
            result = await self.session.execute(stmt)
            rows = result.all()
            return [
                RetrievedChunk(
                    id=chunk.id,
                    document_id=chunk.document_id,
                    document_name=name,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    content=chunk.content,
                    score=float(score),
                )
                for chunk, name, score in rows
            ]

        from app.rag.retrieval import cosine

        stmt = select(tables.DocumentChunk, tables.Document.name).join(
            tables.Document, tables.Document.id == tables.DocumentChunk.document_id
        )
        result = await self.session.execute(stmt)
        ranked = []
        for chunk, name in result.all():
            score = cosine(embedding, chunk.embedding)
            if score >= threshold:
                ranked.append((chunk, name, score))
        ranked.sort(key=lambda item: item[2], reverse=True)
        return [
            RetrievedChunk(
                id=chunk.id,
                document_id=chunk.document_id,
                document_name=name,
                chunk_index=chunk.chunk_index,
                page_number=chunk.page_number,
                content=chunk.content,
                score=score,
            )
            for chunk, name, score in ranked[:k]
        ]


class ConversationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add_message(
        self, conversation_id: str | None, role: str, content: str, intent: str | None = None, citations: list[Citation] | None = None
    ) -> tuple[str, str]:
        if conversation_id:
            conversation = await self.session.get(tables.Conversation, conversation_id)
        else:
            conversation = None
        if conversation is None:
            conversation_id = str(uuid4())
            conversation = tables.Conversation(id=conversation_id, title=content[:60] or "Conversation")
            self.session.add(conversation)
            await self.session.flush()
        message_id = str(uuid4())
        self.session.add(
            tables.Message(
                id=message_id,
                conversation_id=conversation_id,
                role=role,
                content=content,
                intent=intent,
                citations=[item.model_dump() for item in citations] if citations else [],
            )
        )
        await self.session.commit()
        return conversation_id, message_id

    async def list_conversations(self) -> list[tuple[tables.Conversation, int, str | None]]:
        stmt = (
            select(tables.Conversation, func.count(tables.Message.id), func.max(tables.Message.intent))
            .outerjoin(tables.Message, tables.Message.conversation_id == tables.Conversation.id)
            .group_by(tables.Conversation.id)
            .order_by(tables.Conversation.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return [(row[0], int(row[1]), row[2]) for row in result.all()]

    async def get_conversation(self, conversation_id: str) -> tuple[tables.Conversation, list[MessageView]] | None:
        conversation = await self.session.get(tables.Conversation, conversation_id)
        if not conversation:
            return None
        result = await self.session.execute(
            select(tables.Message).where(tables.Message.conversation_id == conversation_id).order_by(tables.Message.created_at)
        )
        messages = [
            MessageView(
                id=m.id,
                role=m.role,
                content=m.content,
                intent=m.intent,
                citations=[Citation(**item) for item in (m.citations or [])],
                created_at=m.created_at.isoformat(),
            )
            for m in result.scalars().all()
        ]
        return conversation, messages


class BusinessRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_order(self, order_id: str) -> dict | None:
        order = await self.session.get(tables.Order, order_id.upper())
        if not order:
            return None
        return {
            "order_id": order.id,
            "status": order.status,
            "carrier": order.carrier,
            "tracking_number": order.tracking_number,
            "estimated_delivery": order.estimated_delivery,
        }

    async def search_products(self, query: str) -> list[dict]:
        needle = f"%{query.lower()}%"
        result = await self.session.execute(
            select(tables.Product).where(func.lower(tables.Product.name).like(needle) | func.lower(tables.Product.description).like(needle))
        )
        return [{"product_id": p.id, "name": p.name, "description": p.description} for p in result.scalars().all()]

    async def get_inventory(self, product_id: str) -> dict | None:
        result = await self.session.execute(
            select(tables.Inventory, tables.Product.name)
            .join(tables.Product, tables.Product.id == tables.Inventory.product_id)
            .where(tables.Inventory.product_id == product_id.upper())
        )
        row = result.one_or_none()
        if not row:
            return None
        inventory, name = row
        return {"product_id": inventory.product_id, "product_name": name, "quantity": inventory.quantity, "status": inventory.status}

    async def create_ticket(
        self, summary: str, category: str = "technical_support", priority: str = "normal", customer_email: str | None = None
    ) -> dict:
        public_id = f"TCK-{uuid4().hex[:12].upper()}"
        ticket = tables.SupportTicket(
            id=str(uuid4()),
            public_id=public_id,
            category=category,
            priority=priority,
            status="open",
            summary=summary,
            customer_email=customer_email,
        )
        self.session.add(ticket)
        await self.session.commit()
        return {
            "id": ticket.public_id,
            "public_id": ticket.public_id,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "summary": ticket.summary,
            "customer_email": ticket.customer_email,
            "created_at": ticket.created_at.isoformat(),
        }

    async def get_ticket(self, ticket_id: str) -> dict | None:
        result = await self.session.execute(
            select(tables.SupportTicket).where(
                (tables.SupportTicket.id == ticket_id) | (tables.SupportTicket.public_id == ticket_id)
            )
        )
        ticket = result.scalar_one_or_none()
        if not ticket:
            return None
        return {
            "id": ticket.public_id,
            "public_id": ticket.public_id,
            "category": ticket.category,
            "priority": ticket.priority,
            "status": ticket.status,
            "summary": ticket.summary,
            "customer_email": ticket.customer_email,
            "created_at": ticket.created_at.isoformat(),
        }

    async def list_tickets(self) -> list[dict]:
        result = await self.session.execute(select(tables.SupportTicket).order_by(tables.SupportTicket.created_at.desc()))
        return [
            {
                "id": ticket.public_id,
                "public_id": ticket.public_id,
                "category": ticket.category,
                "priority": ticket.priority,
                "status": ticket.status,
                "summary": ticket.summary,
                "customer_email": ticket.customer_email,
                "created_at": ticket.created_at.isoformat(),
            }
            for ticket in result.scalars().all()
        ]

    async def create_handoff(self, reason: str, conversation_id: str | None = None) -> dict:
        public_id = f"HND-{uuid4().hex[:12].upper()}"
        handoff = tables.HandoffRequest(
            id=str(uuid4()),
            public_id=public_id,
            reason=reason,
            conversation_id=conversation_id,
            status="queued",
        )
        self.session.add(handoff)
        await self.session.commit()
        return {
            "id": handoff.public_id,
            "public_id": handoff.public_id,
            "reason": handoff.reason,
            "conversation_id": conversation_id,
            "status": handoff.status,
        }

    async def log_tool(
        self,
        tool_name: str,
        status: str,
        input_data: dict,
        output: dict | None = None,
        error_code: str | None = None,
        error_message: str | None = None,
    ) -> None:
        self.session.add(
            tables.ToolExecutionLog(
                id=str(uuid4()),
                tool_name=tool_name,
                status=status,
                input=input_data,
                output=output,
                error_code=error_code,
                error_message=error_message,
            )
        )
        await self.session.commit()

    async def log_request_metric(
        self,
        conversation_id: str,
        intent: str,
        total_ms: int,
        classification_ms: int = 0,
        retrieval_ms: int = 0,
        llm_ms: int = 0,
        tool_ms: int = 0,
        citation_count: int = 0,
        tool_count: int = 0,
        success: bool = True,
    ) -> None:
        self.session.add(
            tables.RequestMetric(
                id=str(uuid4()),
                conversation_id=conversation_id,
                intent=intent,
                total_ms=total_ms,
                classification_ms=classification_ms,
                retrieval_ms=retrieval_ms,
                llm_ms=llm_ms,
                tool_ms=tool_ms,
                citation_count=citation_count,
                tool_count=tool_count,
                success=success,
            )
        )
        await self.session.commit()

    async def analytics(self) -> dict:
        conversations = int(await self.session.scalar(select(func.count()).select_from(tables.Conversation)) or 0)
        knowledge_query_count = select(func.count()).select_from(tables.Message).where(tables.Message.intent == "knowledge_query")
        knowledge = int(await self.session.scalar(knowledge_query_count) or 0)
        tool_calls = int(await self.session.scalar(select(func.count()).select_from(tables.ToolExecutionLog)) or 0)
        tickets = int(await self.session.scalar(select(func.count()).select_from(tables.SupportTicket)) or 0)
        unresolved = int(
            await self.session.scalar(select(func.count()).select_from(tables.Message).where(tables.Message.intent == "unknown")) or 0
        )
        return {
            "total_conversations": conversations,
            "knowledge_queries": knowledge,
            "tool_calls": tool_calls,
            "tickets_created": tickets,
            "unresolved_questions": unresolved,
            "average_response_time_ms": int(
                await self.session.scalar(select(func.coalesce(func.avg(tables.RequestMetric.total_ms), 0))) or 0
            ),
            "average_retrieval_time_ms": int(
                await self.session.scalar(select(func.coalesce(func.avg(tables.RequestMetric.retrieval_ms), 0))) or 0
            ),
            "average_llm_time_ms": int(await self.session.scalar(select(func.coalesce(func.avg(tables.RequestMetric.llm_ms), 0))) or 0),
        }


def citations_from_retrieved(chunks: list[RetrievedChunk]) -> list[Citation]:
    return [
        Citation(
            document_id=chunk.document_id,
            document_name=chunk.document_name,
            chunk_index=chunk.chunk_index,
            page_number=chunk.page_number,
            snippet=chunk.content[:240],
        )
        for chunk in chunks
    ]
