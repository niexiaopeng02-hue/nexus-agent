import { Link } from 'react-router-dom';

export function LandingPage() {
  return (
    <section>
      <div className="hero">
        <p className="eyebrow">Production-oriented AI support platform</p>
        <h1>NexusAgent</h1>
        <p>
          AI customer support, knowledge base retrieval, and business workflow automation for a fictional NovaTech support desk.
        </p>
        <Link className="button" to="/chat">Open Demo Chat</Link>
      </div>
      <div className="grid three">
        <div><h3>RAG with citations</h3><p>Documents are chunked, embedded, retrieved, and returned with source snippets.</p></div>
        <div><h3>Explicit routing</h3><p>Intent classification selects RAG, order lookup, inventory checks, tickets, or handoff.</p></div>
        <div><h3>Business tools</h3><p>Tool calls use validated schemas and log execution status for auditability.</p></div>
      </div>
      <div className="architecture">
        User to React to FastAPI to Agent Router to RAG or Tools to PostgreSQL/pgvector to LLM to Response
      </div>
    </section>
  );
}
