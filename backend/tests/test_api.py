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
    assert body["request_id"]
    assert body["status"] == "completed"
    assert body["evidence"]
    assert body["analysis_performed"]
    assert body["structured_data"]


def test_analysis_api_rejects_empty_question() -> None:
    response = TestClient(app).post("/api/v1/analysis", json={"question": ""})

    assert response.status_code == 422
