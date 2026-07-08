# API Reference

NexusAgent exposes OpenAPI at `/docs` when the FastAPI backend is running.

## Core Endpoints

- `GET /api/health`
- `POST /api/chat`
- `GET /api/conversations`
- `GET /api/conversations/{id}`
- `POST /api/documents/upload`
- `GET /api/documents`
- `GET /api/documents/{id}`
- `DELETE /api/documents/{id}`
- `POST /api/documents/{id}/reprocess`
- `GET /api/tickets`
- `POST /api/tickets`
- `GET /api/tickets/{id}`
- `GET /api/analytics/overview`
- `GET /api/orders/{order_id}`
- `GET /api/products/search?q=keyboard`
- `GET /api/inventory/{product_id}`

Error responses follow:

```json
{
  "error": {
    "code": "DOCUMENT_NOT_FOUND",
    "message": "Document not found",
    "request_id": "..."
  }
}
```

