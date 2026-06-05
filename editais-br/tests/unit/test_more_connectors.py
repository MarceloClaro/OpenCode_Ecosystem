"""Testes conectores SEBRAE, CNPq, FAPEG — Issues #7, #8, #9."""

from unittest.mock import MagicMock, patch

from worker.connectors.base import BaseConnector


def test_sebrae_connector():
    from worker.connectors.sebrae import SebraeConnector
    assert issubclass(SebraeConnector, BaseConnector)
    c = SebraeConnector()
    assert c.mode == "http"
    assert "sebrae" in c.base_url
    e = c.parse("<html><a href='/editais/1'>Edital SEBRAE</a></html>")
    assert len(e) >= 1
    assert e[0].titulo == "Edital SEBRAE"


@patch("worker.connectors.sebrae.httpx")
def test_sebrae_fetch(mock_httpx):
    from worker.connectors.sebrae import SebraeConnector
    mock_resp = MagicMock()
    mock_resp.text = "<html></html>"
    mock_resp.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_resp
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_httpx.Client.return_value = mock_client
    SebraeConnector().fetch_editais()
    mock_client.get.assert_called_once()


def test_cnpq_connector():
    from worker.connectors.cnpq import CnpqConnector
    assert issubclass(CnpqConnector, BaseConnector)
    c = CnpqConnector()
    assert c.mode == "http"
    assert "cnpq" in c.base_url
    e = c.parse("<html><a href='/chamada/1'>Chamada CNPq</a></html>")
    assert len(e) >= 1
    assert e[0].titulo == "Chamada CNPq"


@patch("worker.connectors.cnpq.httpx")
def test_cnpq_fetch(mock_httpx):
    from worker.connectors.cnpq import CnpqConnector
    mock_resp = MagicMock()
    mock_resp.text = "<html></html>"
    mock_resp.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_resp
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_httpx.Client.return_value = mock_client
    CnpqConnector().fetch_editais()
    mock_client.get.assert_called_once()


def test_fapeg_connector():
    from worker.connectors.fapeg import FapegConnector
    assert issubclass(FapegConnector, BaseConnector)
    c = FapegConnector()
    assert c.mode == "http"
    assert "fapeg" in c.base_url
    e = c.parse("<html><a href='/chamada/1'>Chamada FAPEG</a></html>")
    assert len(e) >= 1
    assert e[0].titulo == "Chamada FAPEG"


@patch("worker.connectors.fapeg.httpx")
def test_fapeg_fetch(mock_httpx):
    from worker.connectors.fapeg import FapegConnector
    mock_resp = MagicMock()
    mock_resp.text = "<html></html>"
    mock_resp.raise_for_status = MagicMock()
    mock_client = MagicMock()
    mock_client.get.return_value = mock_resp
    mock_client.__enter__ = MagicMock(return_value=mock_client)
    mock_client.__exit__ = MagicMock(return_value=False)
    mock_httpx.Client.return_value = mock_client
    FapegConnector().fetch_editais()
    mock_client.get.assert_called_once()
