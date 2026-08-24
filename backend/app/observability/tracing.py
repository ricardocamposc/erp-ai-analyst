"""Environment-controlled LangSmith tracing boundary."""

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from langsmith import traceable

from app.observability.logging import log_event


def traced_analysis(function: Any) -> Any:
    """Decorate a workflow for LangSmith when LANGCHAIN_TRACING_V2 is enabled."""
    return traceable(
        name="erp-ai-analysis",
        process_inputs=lambda value: {"question": value.get("question", "")},
    )(function)


@contextmanager
def trace_tool(
    request_id: str, tool_name: str, arguments: dict[str, Any]
) -> Iterator[None]:
    log_event("tool.start", request_id, tool_name=tool_name, arguments=arguments)
    try:
        yield
    except Exception as error:
        log_event(
            "tool.error",
            request_id,
            tool_name=tool_name,
            error_type=type(error).__name__,
        )
        raise
    else:
        log_event("tool.complete", request_id, tool_name=tool_name)
