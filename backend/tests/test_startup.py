from fastapi.testclient import TestClient

from app.main import app


def test_application_imports() -> None:
    assert app.title == "ERP AI Analyst"


def test_frontend_and_assets_are_served() -> None:
    client = TestClient(app)

    home = client.get("/")
    script = client.get("/assets/app.js")
    chat_state = client.get("/assets/chat-state.js")
    stylesheet = client.get("/assets/styles.css")

    assert home.status_code == 200
    assert "ERP AI Analyst" in home.text
    assert script.status_code == 200
    assert "fetch('/api/v1/dynamic-analysis'" in script.text
    assert chat_state.status_code == 200
    assert "createChatState" in chat_state.text
    assert stylesheet.status_code == 200
    assert ".hero" in stylesheet.text
