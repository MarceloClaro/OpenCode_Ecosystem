"""Testes do BrowserConnector com Playwright — Issue #50."""

from unittest.mock import MagicMock, patch
from worker.connectors.base import BaseConnector, EditalRaw


def test_browser_connector_existe():
    """BrowserConnector deve ser importável."""
    from worker.connectors.browser_base import BrowserConnector


def test_browser_connector_herda_base():
    """BrowserConnector deve herdar de BaseConnector."""
    from worker.connectors.browser_base import BrowserConnector

    assert issubclass(BrowserConnector, BaseConnector)


def test_browser_connector_mode_browser():
    """BrowserConnector deve ter mode='browser'."""
    from worker.connectors.browser_base import BrowserConnector

    class TestConnector(BrowserConnector):
        base_url = "https://teste.com"

        def parse(self, content):
            return []

    c = TestConnector()
    assert c.mode == "browser"


def test_finep_connector_mode_browser():
    """FINEP deve ser browser mode (tem Cloudflare)."""
    from worker.connectors.finep import FinepConnector

    c = FinepConnector()
    assert c.mode == "browser"


@patch("worker.connectors.browser_base.sync_playwright")
def test_browser_connector_fetch_usa_playwright(mock_pw):
    """fetch_editais() deve usar Playwright para buscar a página."""
    from worker.connectors.browser_base import BrowserConnector
    from unittest.mock import MagicMock

    mock_browser = MagicMock()
    mock_page = MagicMock()
    mock_page.content.return_value = "<html><body></body></html>"
    mock_browser.new_page.return_value = mock_page
    mock_browser.__enter__.return_value = mock_browser
    mock_browser.__exit__.return_value = False

    mock_playwright = MagicMock()
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_pw.return_value.__enter__.return_value = mock_playwright
    mock_pw.return_value.__exit__.return_value = False

    class TestConnector(BrowserConnector):
        base_url = "https://exemplo.com"

        def parse(self, content):
            return [EditalRaw(titulo="Teste", url="https://exemplo.com/1")]

    c = TestConnector()
    result = c.fetch_editais()

    assert len(result) == 1
    assert result[0].titulo == "Teste"
