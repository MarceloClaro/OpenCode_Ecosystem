"""Testes das Celery tasks — Issue #13."""

from unittest.mock import MagicMock, patch


def test_celery_app_existe():
    """Celery app deve ser importável."""
    from worker.celery_app import app
    assert app is not None
    assert hasattr(app, "task")


def test_crawl_portal_task_existe():
    """Task crawl_portal deve existir e ter assinatura correta."""
    from worker.tasks.crawl import crawl_portal

    assert callable(crawl_portal)


def test_extract_edital_task_existe():
    """Task extract_edital deve existir."""
    from worker.tasks.extract import extract_edital

    assert callable(extract_edital)


def test_analyze_edital_task_existe():
    """Task analyze_edital deve existir."""
    from worker.tasks.analyze import analyze_edital

    assert callable(analyze_edital)


@patch.dict("worker.tasks.crawl.CONNECTORS", {"prosas": MagicMock()})
@patch("worker.tasks.crawl.SessionLocal")
def test_crawl_portal_busca_e_salva_editais(mock_session):
    """crawl_portal deve: buscar editais → salvar no banco."""
    from worker.tasks.crawl import CONNECTORS, crawl_portal

    mock_connector = CONNECTORS["prosas"].return_value
    mock_connector.fetch_editais.return_value = []

    mock_portal = MagicMock()
    mock_portal.nome = "prosas"
    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_portal
    mock_session.return_value = mock_db

    crawl_portal(portal_id="00000000-0000-0000-0000-000000000001")
    mock_connector.fetch_editais.assert_called_once()


@patch("worker.tasks.extract.httpx.get")
@patch("worker.tasks.extract.SessionLocal")
@patch("worker.tasks.extract.PDFExtractor")
def test_extract_edital_extrai_texto(mock_extractor_class, mock_session, mock_httpx_get):
    """extract_edital deve: buscar edital → extrair texto → salvar."""
    from worker.tasks.extract import extract_edital

    mock_extractor = MagicMock()
    mock_extractor.extract.return_value = "Texto extraído."
    mock_extractor_class.return_value = mock_extractor

    mock_response = MagicMock()
    mock_response.content = b"%PDF-1.4 fake"
    mock_response.raise_for_status = MagicMock()
    mock_httpx_get.return_value = mock_response

    mock_db = MagicMock()
    mock_edital = MagicMock()
    mock_edital.pdf_url = "https://exemplo.com/edital.pdf"
    mock_db.query.return_value.filter.return_value.first.return_value = mock_edital
    mock_session.return_value = mock_db

    extract_edital(edital_id="00000000-0000-0000-0000-000000000002")
    mock_extractor.extract.assert_called_once()


@patch.dict("os.environ", {"DEEPSEEK_API_KEY": "sk-test"})
@patch("worker.tasks.analyze.SessionLocal")
@patch("worker.tasks.analyze.ExtractorAgent")
def test_analyze_edital_chama_agente(mock_agent_class, mock_session):
    """analyze_edital deve: buscar edital → chamar agente → salvar resultado."""
    from worker.tasks.analyze import analyze_edital

    mock_agent = MagicMock()
    mock_agent.execute.return_value = {"titulo": "X", "resumo": "Y"}
    mock_agent_class.return_value = mock_agent

    mock_db = MagicMock()
    mock_edital = MagicMock()
    mock_edital.raw_text = "Texto do edital..."
    mock_db.query.return_value.filter.return_value.first.return_value = mock_edital
    mock_session.return_value = mock_db

    analyze_edital(edital_id="00000000-0000-0000-0000-000000000003")
    mock_agent.execute.assert_called_once()
