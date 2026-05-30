"""Testes da interface web — Issue #16."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Cria tabelas e retorna TestClient."""
    from api.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    from api.main import app
    yield TestClient(app)

    Base.metadata.drop_all(bind=engine)


def test_dashboard_retorna_html(client):
    """GET / deve retornar HTML."""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_dashboard_htmx_retorna_tabela(client):
    """GET / com header HX-Request retorna partial da tabela."""
    response = client.get("/", headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_detalhe_edital_retorna_html(client):
    """GET /edital/{id} deve retornar 404 para ID inexistente."""
    response = client.get("/edital/00000000-0000-0000-0000-000000000001")
    assert response.status_code == 404


def test_portais_retorna_html(client):
    """GET /portais deve retornar HTML."""
    response = client.get("/portais")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_jobs_id_retorna_html(client):
    """GET /jobs/{id} deve retornar 404 para job inexistente."""
    response = client.get("/jobs/00000000-0000-0000-0000-000000000001")
    assert response.status_code == 404
