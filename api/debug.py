from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path
import re
import sys
import traceback


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


def _redact(value: str) -> str:
    value = re.sub(r"://([^:/?]+):([^@]+)@", r"://\1:***@", value)
    value = re.sub(r"(SECRET_KEY=)[^\s,]+", r"\1***", value)
    return value


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        status = 200
        payload = {"status": "ok"}
        try:
            from app.core.config import get_settings
            from app.db import session as db_session
            from app.main import app

            settings = get_settings()
            payload.update(
                {
                    "app": app.title,
                    "provider": settings.llm_provider,
                    "database_backend": db_session.engine.url.get_backend_name(),
                    "auto_create_schema": settings.auto_create_schema,
                }
            )
        except Exception as exc:
            status = 500
            payload = {
                "status": "error",
                "error_type": type(exc).__name__,
                "error": _redact(str(exc)),
                "traceback": _redact("".join(traceback.format_exception_only(type(exc), exc))),
            }

        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("content-type", "application/json")
        self.send_header("content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
