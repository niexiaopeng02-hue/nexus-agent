from pydantic import BaseModel, Field


class DocumentView(BaseModel):
    id: str
    name: str
    status: str
    chunk_count: int
    uploaded_at: str


class TicketCreate(BaseModel):
    customer_email: str | None = None
    category: str = "technical_support"
    priority: str = "normal"
    summary: str = Field(min_length=3, max_length=500)


class TicketView(BaseModel):
    id: str
    category: str
    priority: str
    status: str
    summary: str
    created_at: str


class AnalyticsOverview(BaseModel):
    total_conversations: int
    knowledge_queries: int
    tool_calls: int
    tickets_created: int
    unresolved_questions: int
    average_response_time_ms: int
