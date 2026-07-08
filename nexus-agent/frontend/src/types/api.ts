export type IntentResult = {
  intent: string;
  confidence: number;
  entities: Record<string, string>;
  requires_tool: boolean;
  requires_human: boolean;
};

export type Citation = {
  document_id: string;
  document_name: string;
  chunk_index: number;
  page_number?: number | null;
  snippet: string;
};

export type ToolExecution = {
  tool_name: string;
  status: string;
  input: Record<string, unknown>;
  output?: Record<string, unknown> | null;
  error?: string | null;
};

export type ChatResponse = {
  conversation_id: string;
  message_id: string;
  answer: string;
  intent: IntentResult;
  citations: Citation[];
  tool_executions: ToolExecution[];
  insufficient_context: boolean;
};

export type DocumentView = {
  id: string;
  name: string;
  status: string;
  chunk_count: number;
  uploaded_at: string;
};

export type ConversationView = {
  id: string;
  title: string;
  message_count: number;
  last_intent?: string | null;
  created_at: string;
  messages?: Array<{ id: string; role: string; content: string; intent?: string | null; created_at: string; citations: Citation[] }>;
};

export type TicketView = {
  id: string;
  category: string;
  priority: string;
  status: string;
  summary: string;
  created_at: string;
};

export type AnalyticsOverview = {
  total_conversations: number;
  knowledge_queries: number;
  tool_calls: number;
  tickets_created: number;
  unresolved_questions: number;
  average_response_time_ms: number;
};

