from fastapi.testclient import TestClient

from app.agent.gateway import RuleBasedGateway
from app.api.analysis import get_model_gateway
from app.main import app

app.dependency_overrides[get_model_gateway] = lambda: RuleBasedGateway()


def test_analysis_api_returns_structured_evidence() -> None:
    response = TestClient(app).post(
        "/api/v1/analysis",
        json={"question": "¿Por qué disminuyeron las ventas este mes?"},
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
