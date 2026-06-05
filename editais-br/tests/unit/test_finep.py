"""Testes do conector FINEP — Issue #6."""

from unittest.mock import MagicMock, patch

from worker.connectors.base import BaseConnector, EditalRaw


def test_finep_connector_herda_base():
    """FinepConnector deve herdar de BaseConnector."""
    from worker.connectors.finep import FinepConnector

    assert issubclass(FinepConnector, BaseConnector)


def test_finep_connector_mode_http():
    """FINEP é HTTP (não precisa de browser)."""
    from worker.connectors.finep import FinepConnector

    connector = FinepConnector()
    assert connector.mode == "http"


def test_finep_connector_base_url():
    """URL base deve ser a da FINEP."""
    from worker.connectors.finep import FinepConnector

    connector = FinepConnector()
    assert "finep.gov.br" in connector.base_url


def test_parse_extrai_editais_do_html():
    """parse() deve extrair editais do HTML da FINEP."""
    from worker.connectors.finep import FinepConnector

    html = """
    <html><body>
    <table class="editais-table">
        <tr>
            <td><a href="/chamadas/chamada/123">Chamada Finep 01/2026</a></td>
            <td>2026-05-01</td>
        </tr>
        <tr>
            <td><a href="/chamadas/chamada/456">Subvenção Inovação 2026</a></td>
            <td>2026-04-20</td>
        </tr>
    </table>
    </body></html>
    """

    connector = FinepConnector()
    editais = connector.parse(html)

    assert len(editais) == 2
    assert isinstance(editais[0], EditalRaw)
    assert editais[0].titulo == "Chamada Finep 01/2026"
    assert "123" in editais[0].url


@patch("worker.connectors.finep.httpx")
def test_fetch_editais_faz_requisicao_http(mock_httpx):
    """fetch_editais() deve fazer GET na URL base."""
    from worker.connectors.finep import FinepConnector

    mock_response = MagicMock()
    mock_response.text = "<html></html>"
    mock_response.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_response
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_httpx.Client.return_value = mock_client

    connector = FinepConnector()
    connector.fetch_editais()

    mock_client.get.assert_called_once()
