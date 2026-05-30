"""Testes do crawler inteligente com busca web — Issue #49."""

from unittest.mock import MagicMock, patch


def test_search_engine_existe():
    """SearchEngine deve ser importável."""
    from worker.discovery import SearchEngine


def test_search_engine_tem_metodo_search():
    """SearchEngine deve ter método search()."""
    from worker.discovery import SearchEngine

    engine = SearchEngine()
    assert hasattr(engine, "search")
    assert callable(engine.search)


@patch("worker.discovery.httpx")
def test_search_engine_duckduckgo_retorna_urls(mock_httpx):
    """DuckDuckGo search deve retornar lista de URLs."""
    from worker.discovery import SearchEngine

    mock_response = MagicMock()
    mock_response.text = """
    <html><body>
    <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Ffapeg.go.gov.br%2Feditais%2F">Editais FAPEG</a>
    <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fprosas.com.br%2Feditais%2F123">Edital Prosas 2026</a>
    <a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.gov.br%2Fcnpq%2Fchamada">Chamada CNPq</a>
    </body></html>
    """
    mock_response.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = False
    mock_httpx.Client.return_value = mock_client

    engine = SearchEngine(backend="duckduckgo")
    results = engine.search("editais fomento 2026")

    assert len(results) > 0
    assert any("fapeg" in r["url"] for r in results)
    assert all("url" in r for r in results)
    assert all("title" in r for r in results)


def test_edital_classifier_existe():
    """EditalClassifier deve ser importável."""
    from worker.discovery import EditalClassifier


def test_edital_classifier_classifica_como_edital():
    """Deve classificar HTML de edital como tipo 'edital'."""
    from worker.discovery import EditalClassifier

    classifier = EditalClassifier(api_key="sk-test")

    with patch.object(classifier, "_call_ai") as mock_ai:
        mock_ai.return_value = {"tipo": "edital", "confidence": 0.95}
        result = classifier.classify("<html>Edital de Fomento 2026...</html>")

    assert result["tipo"] == "edital"
    assert result["confidence"] > 0.9


def test_edital_classifier_classifica_como_portal():
    """Deve classificar listagem como 'portal_list'."""
    from worker.discovery import EditalClassifier

    classifier = EditalClassifier(api_key="sk-test")

    with patch.object(classifier, "_call_ai") as mock_ai:
        mock_ai.return_value = {"tipo": "portal_list", "confidence": 0.88}
        result = classifier.classify("<html>Lista de Editais...</html>")

    assert result["tipo"] == "portal_list"


def test_discover_task_existe():
    """Celery task discover_editais deve existir."""
    from worker.tasks.discover import discover_editais

    assert callable(discover_editais)


@patch("worker.tasks.discover.SearchEngine")
@patch("worker.tasks.discover.EditalClassifier")
@patch("worker.tasks.discover.httpx")
def test_discover_task_fluxo_completo(mock_httpx, mock_classifier, mock_engine):
    """discover_editais deve: buscar → classificar → pipeline."""
    from worker.tasks.discover import discover_editais

    mock_engine.return_value.search.return_value = [
        {"url": "https://exemplo.com/edital/1", "title": "Edital Teste"},
        {"url": "https://exemplo.com/editais", "title": "Lista de Editais"},
    ]

    # Mock httpx para o fetch das páginas
    mock_response = MagicMock()
    mock_response.text = "<html>conteudo</html>"
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__.return_value = mock_client
    mock_client.__exit__.return_value = False
    mock_httpx.Client.return_value = mock_client

    mock_classifier.return_value.classify.side_effect = [
        {"tipo": "edital", "confidence": 0.9},
        {"tipo": "portal_list", "confidence": 0.85},
    ]

    result = discover_editais(query="editais tecnologia 2026")

    assert "total_encontrados" in result
    assert result["editais"] == 1
    assert result["portais"] == 1
