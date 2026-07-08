from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import Depends, FastAPI, File, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.agent.router import route_message
from app.ai.providers.factory import get_provider
from app.core.config import Settings, get_settings
from app.core.errors import AppError, app_error_handler
from app.core.logging import configure_logging
from app.rag.ingestion import ingest_sample_documents, ingest_text_document
from app.schemas.chat import ChatRequest, ChatResponse, ConversationView
from app.schemas.domain import AnalyticsOverview, DocumentView, TicketCreate, TicketView
from app.services.store import store


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    await ingest_sample_documents(get_provider())
    yield


app = FastAPI(title="NexusAgent API", version="0.1.0", lifespan=lifespan)
app.add_exception_handler(AppError, app_error_handler)

settings = get_settings()
UPLOAD_FILE = File(...)
SETTINGS_DEP = Depends(get_settings)
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
async def chat(payload: ChatRequest) -> ChatResponse:
    return await route_message(payload.message, payload.conversation_id, get_provider())


@app.get("/api/conversations", response_model=list[ConversationView])
async def conversations() -> list[ConversationView]:
    return [
        ConversationView(
            id=item.id,
            title=item.title,
            message_count=len(item.messages),
            last_intent=next((message.intent for message in reversed(item.messages) if message.intent), None),
            created_at=item.created_at,
        )
        for item in store.conversations.values()
    ]


@app.get("/api/conversations/{conversation_id}", response_model=ConversationView)
async def conversation(conversation_id: str) -> ConversationView:
    item = store.conversations.get(conversation_id)
    if not item:
        raise AppError("CONVERSATION_NOT_FOUND", "Conversation not found", 404)
    return ConversationView(
        id=item.id,
        title=item.title,
        message_count=len(item.messages),
        last_intent=next((message.intent for message in reversed(item.messages) if message.intent), None),
        created_at=item.created_at,
        messages=item.messages,
    )


@app.post("/api/documents/upload", response_model=DocumentView)
async def upload_document(file: UploadFile = UPLOAD_FILE, settings: Settings = SETTINGS_DEP) -> DocumentView:
    suffix = "." + file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if suffix not in settings.allowed_extensions_set:
        raise AppError("INVALID_FILE_TYPE", "Only PDF, DOCX, TXT, and Markdown files are allowed.", 400)
    raw = await file.read()
    if len(raw) > settings.upload_max_bytes:
        raise AppError("FILE_TOO_LARGE", "Uploaded document exceeds the configured size limit.", 400)
    safe_name = "".join(ch for ch in file.filename if ch.isalnum() or ch in "._- ")[:120]
    text = raw.decode("utf-8", errors="ignore")
    document = await ingest_text_document(safe_name, text, get_provider())
    return DocumentView(
        id=document.id, name=document.name, status=document.status, chunk_count=document.chunk_count, uploaded_at=document.uploaded_at
    )


@app.get("/api/documents", response_model=list[DocumentView])
async def list_documents() -> list[DocumentView]:
    return [
        DocumentView(id=d.id, name=d.name, status=d.status, chunk_count=d.chunk_count, uploaded_at=d.uploaded_at)
        for d in store.documents.values()
    ]


@app.get("/api/documents/{document_id}", response_model=DocumentView)
async def get_document(document_id: str) -> DocumentView:
    document = store.documents.get(document_id)
    if not document:
        raise AppError("DOCUMENT_NOT_FOUND", "Document not found", 404)
    return DocumentView(
        id=document.id, name=document.name, status=document.status, chunk_count=document.chunk_count, uploaded_at=document.uploaded_at
    )


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str) -> dict:
    if not store.delete_document(document_id):
        raise AppError("DOCUMENT_NOT_FOUND", "Document not found", 404)
    return {"deleted": True}


@app.post("/api/documents/{document_id}/reprocess", response_model=DocumentView)
async def reprocess_document(document_id: str) -> DocumentView:
    document = store.documents.get(document_id)
    if not document:
        raise AppError("DOCUMENT_NOT_FOUND", "Document not found", 404)
    document.status = "processed"
    return DocumentView(
        id=document.id, name=document.name, status=document.status, chunk_count=document.chunk_count, uploaded_at=document.uploaded_at
    )


@app.get("/api/tickets", response_model=list[TicketView])
async def list_tickets() -> list[TicketView]:
    return [TicketView(**ticket) for ticket in store.tickets.values()]


@app.post("/api/tickets", response_model=TicketView)
async def create_ticket(payload: TicketCreate) -> TicketView:
    return TicketView(**store.create_ticket(**payload.model_dump()))


@app.get("/api/tickets/{ticket_id}", response_model=TicketView)
async def get_ticket(ticket_id: str) -> TicketView:
    ticket = store.tickets.get(ticket_id)
    if not ticket:
        raise AppError("TICKET_NOT_FOUND", "Ticket not found", 404)
    return TicketView(**ticket)


@app.get("/api/analytics/overview", response_model=AnalyticsOverview)
async def analytics() -> AnalyticsOverview:
    total = len(store.response_times_ms)
    avg = int(sum(store.response_times_ms) / total) if total else 0
    knowledge_queries = sum(
        1 for convo in store.conversations.values() for message in convo.messages if message.intent == "knowledge_query"
    )
    return AnalyticsOverview(
        total_conversations=len(store.conversations),
        knowledge_queries=knowledge_queries,
        tool_calls=len(store.tool_logs),
        tickets_created=len(store.tickets),
        unresolved_questions=store.unresolved_questions,
        average_response_time_ms=avg,
    )


@app.get("/api/orders/{order_id}")
async def get_order(order_id: str) -> dict:
    order = store.orders.get(order_id.upper())
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@app.get("/api/products/search")
async def products_search(q: str = "") -> dict:
    needle = q.lower()
    return {
        "results": [
            product for product in store.products.values() if needle in product["name"].lower() or needle in product["description"].lower()
        ]
    }


@app.get("/api/inventory/{product_id}")
async def get_inventory(product_id: str) -> dict:
    inventory = store.inventory.get(product_id.upper())
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found")
    return inventory
