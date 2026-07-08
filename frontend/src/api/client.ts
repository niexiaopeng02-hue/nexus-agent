import type { AnalyticsOverview, ChatResponse, ConversationView, DocumentView, TicketView } from '../types/api';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? '';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: options?.body instanceof FormData ? undefined : { 'Content-Type': 'application/json' },
    ...options
  });
  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.error?.message ?? `Request failed with ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export const api = {
  chat: (message: string, conversationId?: string) =>
    request<ChatResponse>('/api/chat', { method: 'POST', body: JSON.stringify({ message, conversation_id: conversationId }) }),
  documents: () => request<DocumentView[]>('/api/documents'),
  uploadDocument: (file: File) => {
    const body = new FormData();
    body.append('file', file);
    return request<DocumentView>('/api/documents/upload', { method: 'POST', body });
  },
  deleteDocument: (id: string) => request<{ deleted: boolean }>(`/api/documents/${id}`, { method: 'DELETE' }),
  conversations: () => request<ConversationView[]>('/api/conversations'),
  conversation: (id: string) => request<ConversationView>(`/api/conversations/${id}`),
  tickets: () => request<TicketView[]>('/api/tickets'),
  analytics: () => request<AnalyticsOverview>('/api/analytics/overview')
};

