import json
import os
import sys
from urllib import request
from urllib.error import HTTPError, URLError


BASE_URL = os.getenv("NEXUS_API_BASE_URL", "http://localhost:8000").rstrip("/")


def fail(name: str, message: str) -> None:
    print(f"FAIL {name}: {message}")
    raise SystemExit(1)


def http_json(method: str, path: str, payload: dict | None = None, headers: dict | None = None) -> dict:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    req = request.Request(
        f"{BASE_URL}{path}",
        data=body,
        method=method,
        headers={"Content-Type": "application/json", **(headers or {})},
    )
    try:
        with request.urlopen(req, timeout=15) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}: {exc.read().decode('utf-8', errors='ignore')}") from exc
    except URLError as exc:
        raise RuntimeError(str(exc)) from exc


def upload_markdown() -> dict:
    boundary = "----NexusAgentSmokeBoundary"
    content = b"# Smoke Test\n\nSmoke test uploads should preserve return policy text."
    body = (
        f"--{boundary}\r\n"
        'Content-Disposition: form-data; name="file"; filename="smoke.md"\r\n'
        "Content-Type: text/markdown\r\n\r\n"
    ).encode("utf-8") + content + f"\r\n--{boundary}--\r\n".encode("utf-8")
    req = request.Request(
        f"{BASE_URL}/api/documents/upload",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def check(name: str, fn) -> None:
    try:
        if fn() is False:
            fail(name, "check returned false")
    except Exception as exc:
        fail(name, str(exc))
    print(f"PASS {name}")


def main() -> int:
    check("health", lambda: http_json("GET", "/api/health")["status"] == "ok" or fail("health", "status was not ok"))
    check(
        "order query",
        lambda: "ORD-10001" in http_json("POST", "/api/chat", {"message": "Where is order ORD-10001?"})["answer"],
    )
    check(
        "inventory query",
        lambda: http_json("POST", "/api/chat", {"message": "Is Product X available?"})["tool_executions"][0]["tool_name"]
        == "check_inventory"
        or fail("inventory query", "inventory tool was not executed"),
    )
    check(
        "knowledge query",
        lambda: http_json("POST", "/api/chat", {"message": "What is NovaTech's return policy?"})["citations"]
        or fail("knowledge query", "missing citations"),
    )
    check(
        "no-context query",
        lambda: http_json("POST", "/api/chat", {"message": "Do you offer drone insurance?"})["insufficient_context"]
        or fail("no-context query", "expected insufficient_context"),
    )
    check(
        "ticket creation",
        lambda: http_json("POST", "/api/tickets", {"summary": "Smoke test ticket", "category": "smoke", "priority": "normal"})[
            "id"
        ].startswith("TCK-")
        or fail("ticket creation", "ticket id missing"),
    )
    check("document upload", lambda: upload_markdown()["chunk_count"] >= 1 or fail("document upload", "no chunks created"))
    check(
        "analytics",
        lambda: http_json("GET", "/api/analytics/overview")["total_conversations"] >= 1
        or fail("analytics", "expected conversations"),
    )
    print(f"Smoke tests passed against {BASE_URL}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
