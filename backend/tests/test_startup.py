from app.main import app


def test_application_imports() -> None:
    assert app.title == "ERP AI Analyst"
