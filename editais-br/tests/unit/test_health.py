"""Testes do health check — Issue #18."""

from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)


def test_health_retorna_200():
    """GET /health deve retornar 200."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_retorna_json_com_status_ok():
    """GET /health deve retornar {"status": "ok"}."""
    response = client.get("/health")
    data = response.json()
    assert "status" in data
    assert data["status"] == "ok"


def test_health_nao_exige_autenticacao():
    """Health check deve funcionar sem headers especiais."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_tem_content_type_json():
    """Health check deve retornar Content-Type application/json."""
    response = client.get("/health")
    assert "application/json" in response.headers["content-type"]
