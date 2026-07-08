import { useState } from 'react';
import { api } from '../api/client';
import type { ChatResponse } from '../types/api';

const demos = [
  "What is NovaTech's return policy?",
  'Where is order ORD-10001?',
  'Is the Wireless Headphones product in stock?',
  'My keyboard stopped working. Please create a support ticket.',
  'Do you offer drone insurance?'
];

export function ChatPage() {
  const [message, setMessage] = useState(demos[0]);
  const [conversationId, setConversationId] = useState<string>();
  const [responses, setResponses] = useState<ChatResponse[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>();

  async function send() {
    setLoading(true);
    setError(undefined);
    try {
      const response = await api.chat(message, conversationId);
      setConversationId(response.conversation_id);
      setResponses((items) => [...items, response]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat request failed');
    } finally {
      setLoading(false);
    }
  }

  return (
    <section>
      <h1>Chat</h1>
      <div className="demo-row">
        {demos.map((item) => <button key={item} onClick={() => setMessage(item)}>{item}</button>)}
      </div>
      <div className="chat-input">
        <textarea value={message} onChange={(event) => setMessage(event.target.value)} />
        <button className="button" disabled={loading} onClick={send}>{loading ? 'Sending...' : 'Send'}</button>
      </div>
      {error && <div className="state error">{error}</div>}
      <div className="thread">
        {responses.map((response) => (
          <article className="message" key={response.message_id}>
            <div className="badge">Intent: {response.intent.intent}</div>
            <pre>{response.answer}</pre>
            {response.tool_executions.length > 0 && <p className="muted">Tool used: {response.tool_executions.map((tool) => tool.tool_name).join(', ')}</p>}
            {response.citations.length > 0 && (
              <div>
                <h4>Sources</h4>
                {response.citations.map((citation) => (
                  <p className="source" key={`${citation.document_id}-${citation.chunk_index}`}>
                    {citation.document_name} chunk {citation.chunk_index + 1}: {citation.snippet}
                  </p>
                ))}
              </div>
            )}
          </article>
        ))}
      </div>
    </section>
  );
}

