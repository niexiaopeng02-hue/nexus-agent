from enum import Enum

from pydantic import BaseModel, Field


class Intent(str, Enum):
    knowledge_query = "knowledge_query"
    order_query = "order_query"
    product_query = "product_query"
    inventory_query = "inventory_query"
    refund_request = "refund_request"
    technical_support = "technical_support"
    create_ticket = "create_ticket"
    human_handoff = "human_handoff"
    general_conversation = "general_conversation"
    unknown = "unknown"


class IntentResult(BaseModel):
    intent: Intent
    confidence: float = Field(ge=0, le=1)
    entities: dict[str, str] = Field(default_factory=dict)
    requires_tool: bool = False
    requires_human: bool = False


class Citation(BaseModel):
    document_id: str
    document_name: str
    chunk_index: int
    page_number: int | None = None
    snippet: str


class ToolExecution(BaseModel):
    tool_name: str
    status: str
    input: dict
    output: dict | None = None
    error: str | None = None
    error_code: str | None = None
    error_message: str | None = None


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None


class ChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    answer: str
    intent: IntentResult
    citations: list[Citation] = Field(default_factory=list)
    tool_executions: list[ToolExecution] = Field(default_factory=list)
    insufficient_context: bool = False


class MessageView(BaseModel):
    id: str
    role: str
    content: str
    intent: str | None = None
    citations: list[Citation] = Field(default_factory=list)
    created_at: str


class ConversationView(BaseModel):
    id: str
    title: str
    message_count: int
    last_intent: str | None = None
    created_at: str
    messages: list[MessageView] = Field(default_factory=list)
