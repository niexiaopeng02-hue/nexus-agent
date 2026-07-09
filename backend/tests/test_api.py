def test_health(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_chat_order_api(client):
    response = client.post("/api/chat", json={"message": "Where is order ORD-10001?"})
    assert response.status_code == 200
    body = response.json()
    assert body["intent"]["intent"] == "order_query"
    assert "DHL" in body["answer"]


def test_chat_inventory_api(client):
    response = client.post("/api/chat", json={"message": "Is Product X available?"})
    assert response.status_code == 200
    assert response.json()["tool_executions"][0]["tool_name"] == "check_inventory"


def test_chat_ticket_api(client):
    response = client.post("/api/chat", json={"message": "My product stopped working after two days. I need support."})
    assert response.status_code == 200
    assert "Support ticket" in response.json()["answer"]


def test_conversations_api(client):
    client.post("/api/chat", json={"message": "Where is order ORD-10001?"})
    response = client.get("/api/conversations")
    assert response.status_code == 200
    assert response.json()[0]["message_count"] == 2


def test_documents_list_seeded(client):
    response = client.get("/api/documents")
    assert response.status_code == 200
    assert len(response.json()) >= 5


def test_document_upload_validation(client):
    response = client.post("/api/documents/upload", files={"file": ("bad.exe", b"nope", "application/octet-stream")})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_FILE_TYPE"


def test_document_upload_markdown(client):
    response = client.post("/api/documents/upload", files={"file": ("policy.md", b"# Policy\n\nReturns are allowed.", "text/markdown")})
    assert response.status_code == 200
    assert response.json()["chunk_count"] == 1


def test_tickets_api(client):
    created = client.post(
        "/api/tickets",
        json={"summary": "Need warranty review", "category": "warranty", "priority": "normal", "customer_email": "customer@example.com"},
    )
    assert created.status_code == 200
    body = created.json()
    assert body["id"].startswith("TCK-")
    assert body["customer_email"] == "customer@example.com"
    ticket_id = body["id"]
    fetched = client.get(f"/api/tickets/{ticket_id}")
    assert fetched.status_code == 200


def test_analytics_api(client):
    client.post("/api/chat", json={"message": "Where is order ORD-10001?"})
    response = client.get("/api/analytics/overview")
    assert response.status_code == 200
    assert response.json()["tool_calls"] >= 1
    assert response.json()["average_response_time_ms"] >= 0


def test_order_demo_api(client):
    response = client.get("/api/orders/ORD-10001")
    assert response.status_code == 200
    assert response.json()["carrier"] == "DHL"


def test_inventory_demo_api(client):
    response = client.get("/api/inventory/PRD-001")
    assert response.status_code == 200
    assert response.json()["quantity"] == 25
