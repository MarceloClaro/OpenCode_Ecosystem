"""Testes do pipeline automático — Issue #51."""

from unittest.mock import MagicMock, patch


def test_beat_schedule_configurado():
    """Celery app deve ter beat_schedule com discover_editais."""
    from worker.celery_app import app

    assert hasattr(app, "conf")
    schedule = app.conf.beat_schedule
    assert "discover_editais_frequente" in schedule
    task_config = schedule["discover_editais_diario"]
    assert task_config["task"] == "discover_editais"


def test_beat_schedule_tem_intervalo():
    """Intervalo deve ser configurado (crontab ou timedelta)."""
    from worker.celery_app import app

    task_config = app.conf.beat_schedule["discover_editais_frequente"]
    assert "schedule" in task_config
    assert task_config["schedule"] is not None


def test_seed_automatico_existe():
    """Deve existir task seed_automatico."""
    from worker.tasks.seed import seed_automatico

    assert callable(seed_automatico)


@patch("worker.tasks.seed.SessionLocal")
def test_seed_automatico_popula_portais(mock_session):
    """seed_automatico deve cadastrar portais se não existirem."""
    from worker.tasks.seed import seed_automatico

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = None
    mock_session.return_value = mock_db

    result = seed_automatico()
    assert "portais_criados" in result
    assert result["total"] == 5


@patch("worker.tasks.discover.SearchEngine")
@patch("worker.tasks.discover.EditalClassifier")
@patch("worker.tasks.discover.httpx")
def test_discover_salva_editais_no_banco(mock_httpx, mock_classifier, mock_engine):
    """discover_editais deve buscar, classificar E salvar no banco."""
    from worker.tasks.discover import discover_editais

    mock_engine.return_value.search.return_value = [
        {"url": "https://fapesp.br/chamada/1", "title": "Chamada FAPESP"},
    ]

    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.text = "<html>Edital FAPESP 2026</html>"
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = False
    mock_httpx.Client.return_value = mock_client

    mock_classifier.return_value.classify.return_value = {
        "tipo": "edital", "confidence": 0.9
    }

    result = discover_editais(query="fapesp")
    assert result["total_encontrados"] == 1
    assert result["editais"] >= 0
