import logging
import sys
from typing import Any


class JsonLikeFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        fields: dict[str, Any] = {
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
        }
        for key in ("request_id", "conversation_id", "intent", "tool_name", "tool_status"):
            if hasattr(record, key):
                fields[key] = getattr(record, key)
        return str(fields)


def configure_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonLikeFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)
