"""Testes da API de editais — Issue #14 e #22."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def setup_db():
    """Cria tabelas uma vez para todos os testes."""
    from api.database import Base, engine
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(setup_db):
    from api.main import app
    return TestClient(app)


def test_get_editais_retorna_200(client):
    """GET /editais deve retornar 200."""
    response = client.get("/editais")
    assert response.status_code == 200


def test_get_editais_retorna_lista(client):
    """GET /editais deve retornar uma lista."""
    response = client.get("/editais")
    data = response.json()
    assert isinstance(data, list)


def test_get_editais_com_paginacao(client):
    """GET /editais deve aceitar skip e limit."""
    response = client.get("/editais?skip=0&limit=10")
    assert response.status_code == 200


def test_get_editais_filtro_por_status(client):
    """GET /editais deve aceitar filtro por status."""
    response = client.get("/editais?status=inscricoes_abertas")
    assert response.status_code == 200


def test_get_editais_filtro_por_valor(client):
    """GET /editais deve aceitar filtro por faixa de valor."""
    response = client.get("/editais?valor_min=50000&valor_max=200000")
    assert response.status_code == 200


def test_get_editais_por_id_retorna_404(client):
    """GET /editais/{id} deve retornar 404 para ID inexistente."""
    response = client.get("/editais/00000000-0000-0000-0000-000000000001")
    assert response.status_code == 404


def test_get_editais_por_id_invalido_retorna_422(client):
    """GET /editais/{id} com ID inválido retorna 422."""
    response = client.get("/editais/id-invalido")
    assert response.status_code == 422
