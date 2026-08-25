"""Durable audit trail for every dynamic-query request and workflow stage."""

import json
import logging
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.connection import create_database_engine

logger = logging.getLogger("erp_ai_analyst.audit")


def _record_event(
    request_id: str,
    *,
    status: str,
    stage: str,
    response: Mapping[str, Any] | None = None,
    error_type: str | None = None,
    error_detail: str | None = None,
) -> None:
    payload = dict(response or {})
    proposal = payload.get("query") or {}
    validation = payload.get("validation") or {}
    result = payload.get("result") or {}
    event = {
        "stage": stage,
        "status": status,
        "at": datetime.now(UTC).isoformat(),
        "error_type": error_type,
    }
    query = text(
        """UPDATE analysis_interaction
        SET status = :status,
            current_stage = :stage,
            stage_history = stage_history || CAST(:event AS JSONB),
            analysis_goal = COALESCE(:analysis_goal, analysis_goal),
            sql_candidate = COALESCE(:sql_candidate, sql_candidate),
            sql_hash = COALESCE(:sql_hash, sql_hash),
            validation = CASE WHEN :has_validation THEN CAST(:validation AS JSONB) ELSE validation END,
            result = CASE WHEN :has_result THEN CAST(:result AS JSONB) ELSE result END,
            response = response || CAST(:response AS JSONB),
            warnings = CASE WHEN :has_warnings THEN CAST(:warnings AS JSONB) ELSE warnings END,
            error_type = :error_type,
            error_detail = :error_detail,
            updated_at = CURRENT_TIMESTAMP
        WHERE request_id = :request_id"""
    )
    try:
        with create_database_engine().begin() as connection:
            connection.execute(
                query,
                {
                    "request_id": request_id,
                    "status": status,
                    "stage": stage,
                    "event": json.dumps([event]),
                    "analysis_goal": proposal.get("analysis_goal"),
                    "sql_candidate": proposal.get("sql"),
                    "sql_hash": result.get("sql_hash"),
                    "validation": json.dumps(validation),
                    "result": json.dumps(result),
                    "response": json.dumps(payload),
                    "warnings": json.dumps(payload.get("warnings", [])),
                    "has_validation": bool(validation),
                    "has_result": bool(result),
                    "has_warnings": "warnings" in payload,
                    "error_type": error_type,
                    "error_detail": error_detail,
                },
            )
    except SQLAlchemyError:
        logger.exception("audit_update_failed", extra={"request_id": request_id, "stage": stage})


def start_interaction(*, request_id: str, question: str, conversation_id: str | None = None) -> None:
    query = text(
        """INSERT INTO analysis_interaction
        (request_id, conversation_id, question, status, current_stage, stage_history, response)
        VALUES (:request_id, :conversation_id, :question, 'received', 'received',
                CAST(:history AS JSONB), CAST(:response AS JSONB))"""
    )
    try:
        with create_database_engine().begin() as connection:
            connection.execute(
                query,
                {
                    "request_id": request_id,
                    "conversation_id": conversation_id,
                    "question": question,
                    "history": json.dumps([{"stage": "received", "status": "received", "at": datetime.now(UTC).isoformat()}]),
                    "response": json.dumps({"request_id": request_id, "status": "received"}),
                },
            )
    except SQLAlchemyError:
        logger.exception("audit_start_failed", extra={"request_id": request_id})


def update_interaction(
    *, request_id: str, stage: str, status: str, response: Mapping[str, Any] | None = None
) -> None:
    _record_event(request_id, status=status, stage=stage, response=response)


def fail_interaction(*, request_id: str, stage: str, error: BaseException) -> None:
    _record_event(
        request_id,
        status="failed",
        stage=stage,
        response={"status": "failed", "warnings": [str(error)]},
        error_type=type(error).__name__,
        error_detail=str(error),
    )


def record_interaction(
    *, request_id: str, question: str, response: Mapping[str, Any], conversation_id: str | None = None
) -> None:
    """Keep a final audit update for callers that finish outside the graph."""
    _record_event(
        request_id,
        status=str(response.get("status", "failed")),
        stage="completed",
        response=response,
    )
