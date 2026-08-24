"""Safe JSON event logging with request-ID context."""

import json
import logging
from contextvars import ContextVar
from typing import Any

request_id_context: ContextVar[str] = ContextVar("request_id", default="-")


def configure_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(message)s",
        force=True,
    )


def log_event(event: str, request_id: str | None = None, **fields: Any) -> None:
    payload = {
        "event": event,
        "request_id": request_id or request_id_context.get(),
        **fields,
    }
    logging.getLogger("erp_ai_analyst").info(
        json.dumps(payload, default=str, sort_keys=True)
    )
