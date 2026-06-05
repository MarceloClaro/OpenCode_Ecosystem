"""BrowserConnector — conector base com Playwright para sites anti-bot.

Usa Playwright (Chromium) em modo headless com Camoufox para evasão de detecção.
Para portais com Cloudflare, CAPTCHA ou que exigem JavaScript.
"""

import logging
from worker.connectors.base import BaseConnector, EditalRaw

logger = logging.getLogger(__name__)

try:
    from playwright.sync_api import sync_playwright

    HAS_PLAYWRIGHT = True
except ImportError:  # pragma: no cover
    sync_playwright = None  # type: ignore
    HAS_PLAYWRIGHT = False


class BrowserConnector(BaseConnector):
    """Conector base para sites que exigem navegador real.

    Usa Playwright com Chromium headless. Suporte opcional a Camoufox
    para evasão de detecção anti-bot.
    """

    mode = "browser"
    base_url = ""
    crawl_interval_hours = 24

    def fetch_editais(self) -> list[EditalRaw]:
        """Busca editais usando navegador real (Playwright).

        Returns:
            Lista de editais brutos encontrados.
        """
        if not HAS_PLAYWRIGHT:
            logger.error("Playwright não instalado. Use: pip install playwright && playwright install chromium")
            return []

        logger.info(f"🌐 Abrindo navegador para {self.base_url}")

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            try:
                page.goto(self.base_url, wait_until="domcontentloaded", timeout=30000)
                content = page.content()
            except Exception as e:
                logger.error(f"Erro ao acessar {self.base_url}: {e}")
                content = ""
            finally:
                browser.close()

        return self.parse(content)

    def parse(self, content: str) -> list[EditalRaw]:
        """Subclasses devem implementar o parsing específico do portal."""
        raise NotImplementedError("Subclasses devem implementar parse()")
