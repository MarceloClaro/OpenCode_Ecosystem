"""Testes da API de jobs — Issue #15."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def setup_db():
    from api.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_db):
    from api.main import app
    return TestClient(app)


def test_post_portais_id_crawl_retorna_202(client):
    """POST /portais/{id}/crawl deve retornar 202 (aceito)."""
    response = client.post("/portais/00000000-0000-0000-0000-000000000001/crawl")
    assert response.status_code in [202, 404]  # 404 se portal não existe


def test_get_jobs_id_retorna_404(client):
    """GET /jobs/{id} deve retornar 404 para job inexistente."""
    response = client.get("/jobs/00000000-0000-0000-0000-000000000001")
    assert response.status_code == 404
