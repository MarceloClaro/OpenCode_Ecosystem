"""Testes dos modelos SQLAlchemy e migrations — Issue #3."""

from pathlib import Path


def test_database_module_existe():
    """api/database.py deve existir."""
    from api import database
    assert hasattr(database, "Base"), "database.Base não encontrado"
    assert hasattr(database, "engine"), "database.engine não encontrado"
    assert hasattr(database, "SessionLocal"), "database.SessionLocal não encontrado"


def test_models_existem_e_sao_instanciaveis():
    """Portal, Edital, Job devem ser classes SQLAlchemy."""
    from sqlalchemy.orm import declarative_base

    from api.models.edital import Edital
    from api.models.job import Job
    from api.models.portal import Portal

    declarative_base()

    for model in [Portal, Edital, Job]:
        assert hasattr(model, "__tablename__"), f"{model.__name__} precisa de __tablename__"
        assert hasattr(model, "__table__"), f"{model.__name__} não é modelo SQLAlchemy"


def test_portal_tem_colunas_obrigatorias():
    """Portal deve ter: id, nome, base_url, mode, crawl_interval_hours, ativo."""
    from api.models.portal import Portal

    colunas = {c.name for c in Portal.__table__.columns}
    obrigatorias = {"id", "nome", "base_url", "mode", "crawl_interval_hours", "ativo"}
    assert obrigatorias.issubset(colunas), f"Faltam colunas: {obrigatorias - colunas}"


def test_edital_tem_colunas_obrigatorias():
    """Edital deve ter: id, titulo, url_original, portal_id, status, raw_text."""
    from api.models.edital import Edital

    colunas = {c.name for c in Edital.__table__.columns}
    obrigatorias = {"id", "titulo", "url_original", "portal_id", "status"}
    assert obrigatorias.issubset(colunas), f"Faltam colunas: {obrigatorias - colunas}"


def test_job_tem_colunas_obrigatorias():
    """Job deve ter: id, portal_id, status, tipo, created_at."""
    from api.models.job import Job

    colunas = {c.name for c in Job.__table__.columns}
    obrigatorias = {"id", "portal_id", "status", "tipo", "created_at"}
    assert obrigatorias.issubset(colunas), f"Faltam colunas: {obrigatorias - colunas}"


def test_alembic_config_existe():
    """Alembic deve estar configurado com env.py e alembic.ini."""
    root = Path(__file__).parents[2]

    alembic_ini = root / "alembic.ini"
    assert alembic_ini.exists(), "alembic.ini não encontrado"

    env_py = root / "api" / "migrations" / "env.py"
    assert env_py.exists(), "api/migrations/env.py não encontrado"


def test_alembic_script_location():
    """alembic.ini deve apontar para api/migrations."""
    root = Path(__file__).parents[2]
    content = (root / "alembic.ini").read_text()
    assert "script_location = api/migrations" in content
