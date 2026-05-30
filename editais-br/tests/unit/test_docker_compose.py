"""Testes de validação do docker-compose.yml — Issue #1."""

from pathlib import Path

import yaml


def load_compose() -> dict:
    path = Path(__file__).parents[2] / "docker-compose.yml"
    return yaml.safe_load(path.read_text())


def test_docker_compose_existe_eh_yaml_valido():
    """docker-compose.yml deve existir e ser YAML válido."""
    compose = load_compose()
    assert "services" in compose
    assert isinstance(compose["services"], dict)


def test_todos_servicos_obrigatorios_presentes():
    """Deve conter postgres, redis, api, worker, nginx."""
    compose = load_compose()
    servicos = compose["services"]

    obrigatorios = ["postgres", "redis", "api", "worker", "nginx"]
    for servico in obrigatorios:
        assert servico in servicos, f"Serviço '{servico}' não encontrado"


def test_postgres_config():
    """PostgreSQL 16 com volume e healthcheck."""
    compose = load_compose()
    pg = compose["services"]["postgres"]

    assert pg["image"].startswith("postgres:16")
    assert "volumes" in pg
    assert "healthcheck" in pg
    assert "POSTGRES_USER" in pg.get("environment", {})


def test_redis_config():
    """Redis com volume e healthcheck."""
    compose = load_compose()
    redis = compose["services"]["redis"]

    assert "redis" in redis["image"]
    assert "volumes" in redis
    assert "healthcheck" in redis


def test_api_depende_de_postgres_e_redis():
    """API deve ter depends_on com postgres e redis condition: service_healthy."""
    compose = load_compose()
    api = compose["services"]["api"]

    assert "build" in api or "image" in api
    deps = api.get("depends_on", {})
    assert "postgres" in deps
    assert "redis" in deps


def test_worker_depende_de_postgres_e_redis():
    """Worker Celery deve ter depends_on com postgres e redis."""
    compose = load_compose()
    worker = compose["services"]["worker"]

    deps = worker.get("depends_on", {})
    assert "postgres" in deps
    assert "redis" in deps


def test_nginx_depende_de_api():
    """Nginx proxy reverso depende da API."""
    compose = load_compose()
    nginx = compose["services"]["nginx"]

    deps = nginx.get("depends_on", {})
    assert "api" in deps
    assert "ports" in nginx


def test_networks_e_volumes_definidos():
    """Networks e volumes no nível raiz."""
    compose = load_compose()

    assert "networks" in compose
    assert "volumes" in compose
