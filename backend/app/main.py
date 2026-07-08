from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.agent.router import route_message
from app.ai.providers.factory import get_provider
from app.core.config import Settings, get_settings
from app.core.errors import AppError, app_error_handler
from app.core.logging import configure_logging
from app.db import session as db_session
from app.db.init_db import create_schema
from app.db.seed import seed_demo_data
from app.db.session import get_session
from app.rag.ingestion import ingest_binary_document
from app.repositories import BusinessRepository, ConversationRepository, DocumentRepository
from app.schemas.chat import ChatRequest, ChatResponse, ConversationView
from app.schemas.domain import AnalyticsOverview, DocumentView, TicketCreate, TicketView


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    await create_schema(db_session.engine)
    async with get_session_context() as session:
        await seed_demo_data(session, get_provider())
    yield


@asynccontextmanager
async def get_session_context():
    async for session in get_session():
        yield session


app = FastAPI(title="NexusAgent API", version="0.1.0", lifespan=lifespan)
app.add_exception_handler(AppError, app_error_handler)

settings = get_settings()
UPLOAD_FILE = File(...)
SETTINGS_DEP = Depends(get_settings)
SESSION_DEP = Depends(get_session)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    request.state.request_id = request.headers.get("x-request-id", str(uuid4()))
    response = await call_next(request)
    response.headers["x-request-id"] = request.state.request_id
    return response


@app.get("/api/health")
async def health() -> dict:
    return {"status": "ok", "service": "NexusAgent", "provider": get_settings().llm_provider}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, session: AsyncSession = SESSION_DEP) -> ChatResponse:
    return await route_message(payload.message, payload.conversation_id, get_provider(), session)


@app.get("/api/conversations", response_model=list[ConversationView])
async def conversations(session: AsyncSession = SESSION_DEP) -> list[ConversationView]:
    rows = await ConversationRepository(session).list_conversations()
    return [
        ConversationView(
            id=item.id,
            title=item.title,
            message_count=count,
            last_intent=last_intent,
            created_at=item.created_at.isoformat(),
        )
        for item, count, last_intent in rows
    ]


@app.get("/api/conversations/{conversation_id}", response_model=ConversationView)
async def conversation(conversation_id: str, session: AsyncSession = SESSION_DEP) -> ConversationView:
    found = await ConversationRepository(session).get_conversation(conversation_id)
    if not found:
        raise AppError("CONVERSATION_NOT_FOUND", "Conversation not found", 404)
    item, messages = found
    return ConversationView(
        id=item.id,
        title=item.title,
        message_count=len(messages),
        last_intent=next((message.intent for message in reversed(messages) if message.intent), None),
        created_at=item.created_at.isoformat(),
        messages=messages,
    )


@app.post("/api/documents/upload", response_model=DocumentView)
async def upload_document(
    file: UploadFile = UPLOAD_FILE,
    settings: Settings = SETTINGS_DEP,
    session: AsyncSession = SESSION_DEP,
) -> DocumentView:
    suffix = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if suffix not in settings.allowed_extensions_set:
        raise AppError("INVALID_FILE_TYPE", "Only PDF, DOCX, TXT, and Markdown files are allowed.", 400)
    raw = await file.read()
    if len(raw) > settings.upload_max_bytes:
        raise AppError("FILE_TOO_LARGE", "Uploaded document exceeds the configured size limit.", 400)
    safe_name = "".join(ch for ch in file.filename if ch.isalnum() or ch in "._- ")[:120]
    document = await ingest_binary_document(safe_name, raw, get_provider(), DocumentRepository(session))
    return DocumentView(
        id=document.id,
        name=document.name,
        status=document.status,
        chunk_count=document.chunk_count,
        uploaded_at=document.created_at.isoformat(),
    )


@app.get("/api/documents", response_model=list[DocumentView])
async def list_documents(session: AsyncSession = SESSION_DEP) -> list[DocumentView]:
    rows = await DocumentRepository(session).list_documents()
    return [
        DocumentView(id=d.id, name=d.name, status=d.status, chunk_count=count, uploaded_at=d.created_at.isoformat())
        for d, count in rows
    ]


@app.get("/api/documents/{document_id}", response_model=DocumentView)
async def get_document(document_id: str, session: AsyncSession = SESSION_DEP) -> DocumentView:
    found = await DocumentRepository(session).get_document(document_id)
    if not found:
        raise AppError("DOCUMENT_NOT_FOUND", "Document not found", 404)
    document, count = found
    return DocumentView(
        id=document.id,
        name=document.name,
        status=document.status,
        chunk_count=count,
        uploaded_at=document.created_at.isoformat(),
    )


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str, session: AsyncSession = SESSION_DEP) -> dict:
    if not await DocumentRepository(session).delete_document(document_id):
        raise AppError("DOCUMENT_NOT_FOUND", "Document not found", 404)
    return {"deleted": True}


@app.post("/api/documents/{document_id}/reprocess", response_model=DocumentView)
async def reprocess_document(document_id: str, session: AsyncSession = SESSION_DEP) -> DocumentView:
    found = await DocumentRepository(session).reprocess_document(document_id)
    if not found:
        raise AppError("DOCUMENT_NOT_FOUND", "Document not found", 404)
    document, count = found
    return DocumentView(
        id=document.id,
        name=document.name,
        status=document.status,
        chunk_count=count,
        uploaded_at=document.created_at.isoformat(),
    )


@app.get("/api/tickets", response_model=list[TicketView])
async def list_tickets(session: AsyncSession = SESSION_DEP) -> list[TicketView]:
    return [TicketView(**ticket) for ticket in await BusinessRepository(session).list_tickets()]


@app.post("/api/tickets", response_model=TicketView)
async def create_ticket(payload: TicketCreate, session: AsyncSession = SESSION_DEP) -> TicketView:
    return TicketView(**await BusinessRepository(session).create_ticket(**payload.model_dump()))


@app.get("/api/tickets/{ticket_id}", response_model=TicketView)
async def get_ticket(ticket_id: str, session: AsyncSession = SESSION_DEP) -> TicketView:
    ticket = await BusinessRepository(session).get_ticket(ticket_id)
    if not ticket:
        raise AppError("TICKET_NOT_FOUND", "Ticket not found", 404)
    return TicketView(**ticket)


@app.get("/api/analytics/overview", response_model=AnalyticsOverview)
async def analytics(session: AsyncSession = SESSION_DEP) -> AnalyticsOverview:
    return AnalyticsOverview(**await BusinessRepository(session).analytics())


@app.get("/api/orders/{order_id}")
async def get_order(order_id: str, session: AsyncSession = SESSION_DEP) -> dict:
    order = await BusinessRepository(session).get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/api/products/search")
async def products_search(q: str = "", session: AsyncSession = SESSION_DEP) -> dict:
    return {"results": await BusinessRepository(session).search_products(q)}


@app.get("/api/inventory/{product_id}")
async def get_inventory(product_id: str, session: AsyncSession = SESSION_DEP) -> dict:
    inventory = await BusinessRepository(session).get_inventory(product_id)
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory
