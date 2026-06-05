"""Testes do conector Prosas — Issue #5."""

from unittest.mock import MagicMock, patch

from worker.connectors.base import BaseConnector, EditalRaw


def test_prosas_connector_herda_base():
    """ProsasConnector deve herdar de BaseConnector."""
    from worker.connectors.prosas import ProsasConnector

    assert issubclass(ProsasConnector, BaseConnector)


def test_prosas_connector_mode_http():
    """Prosas é HTTP (não precisa de browser)."""
    from worker.connectors.prosas import ProsasConnector

    connector = ProsasConnector()
    assert connector.mode == "http"


def test_prosas_connector_base_url():
    """URL base deve ser a do Prosas."""
    from worker.connectors.prosas import ProsasConnector

    connector = ProsasConnector()
    assert "prosas.com.br" in connector.base_url


def test_parse_extrai_editais_do_html():
    """parse() deve extrair editais do HTML do Prosas."""
    from worker.connectors.prosas import ProsasConnector

    html = """
    <html><body>
    <div class="edital-card">
        <h2>Edital de Fomento 2026</h2>
        <a href="/editais/123">Ver edital</a>
        <span class="date">2026-05-08</span>
    </div>
    <div class="edital-card">
        <h2>Chamada Inovação</h2>
        <a href="/editais/456">Ver edital</a>
        <span class="date">2026-04-15</span>
    </div>
    </body></html>
    """

    connector = ProsasConnector()
    editais = connector.parse(html)

    assert len(editais) == 2
    assert isinstance(editais[0], EditalRaw)
    assert editais[0].titulo == "Edital de Fomento 2026"
    assert "123" in editais[0].url


@patch("worker.connectors.prosas.httpx")
def test_fetch_editais_faz_requisicao_http(mock_httpx):
    """fetch_editais() deve fazer GET na URL base."""
    from worker.connectors.prosas import ProsasConnector

    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_response.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_httpx.Client.return_value = mock_client

    connector = ProsasConnector()
    connector.fetch_editais()

    mock_client.get.assert_called_once()
