import pytest
from fastapi.testclient import TestClient

from app.agent.gateway import RuleBasedGateway
from app.api.analysis import get_model_gateway
from app.main import app

app.dependency_overrides[get_model_gateway] = lambda: RuleBasedGateway()


def test_analysis_api_returns_structured_evidence() -> None:
    response = TestClient(app).post(
        "/api/v1/analysis",
        json={"question": "¿Por qué disminuyeron las ventas entre marzo y abril de 2025?"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["conversation_id"]
    assert body["request_id"]
    assert response.headers["X-Request-ID"] == body["request_id"]
    assert body["status"] == "completed"
    assert body["evidence"]
    assert body["analysis_performed"]
    assert body["structured_data"]


def test_analysis_api_preserves_conversation_id() -> None:
    conversation_id = "demo-session-001"
    response = TestClient(app).post(
        "/api/v1/analysis",
        json={"question": "¿Cuál fue el costo total de nómina este mes?", "conversation_id": conversation_id},
    )

    assert response.status_code == 200
    assert response.json()["conversation_id"] == conversation_id


def test_analysis_api_rejects_empty_question() -> None:
    response = TestClient(app).post("/api/v1/analysis", json={"question": ""})

    assert response.status_code == 422


def test_dynamic_analysis_api_exposes_query_and_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.api import analysis as analysis_api

    monkeypatch.setattr(
        analysis_api,
        "run_dynamic_analysis",
        lambda question, request_id, conversation_id=None: {
            "request_id": request_id,
            "answer": "Hay 2 proveedores.",
            "key_findings": [],
            "evidence": [],
            "analysis_performed": [],
            "structured_data": [],
            "warnings": [],
            "status": "completed",
            "query": {"sql": "SELECT 1"},
            "validation": {"status": "approved"},
            "result": {"row_count": 2},
        },
    )

    response = TestClient(app).post(
        "/api/v1/dynamic-analysis",
        json={"question": "¿Cuántos proveedores tienen órdenes?"},
    )

    assert response.status_code == 200
    assert response.json()["validation"]["status"] == "approved"
