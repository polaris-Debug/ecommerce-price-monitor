from fastapi.testclient import TestClient

from src.api.main import app


def test_health(monkeypatch):
    monkeypatch.setattr("src.api.main.check_database", lambda engine: {"database": True})
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "dependencies": {"database": True}}
