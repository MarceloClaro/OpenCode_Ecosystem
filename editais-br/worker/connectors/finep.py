"""FinepConnector — conector para o portal FINEP (https://www.finep.gov.br).

Modo Browser (Playwright) — o portal tem proteção Cloudflare que bloqueia HTTP direto.
"""

import logging

from bs4 import BeautifulSoup

from worker.connectors.browser_base import BrowserConnector
from worker.connectors.base import EditalRaw

logger = logging.getLogger(__name__)

BASE_URL = "https://www.finep.gov.br/chamadas-publicas"


class FinepConnector(BrowserConnector):
    """Conector para o portal FINEP usando Playwright (anti-bot).

    Extrai chamadas públicas via navegador real e faz parsing do HTML.
    """

    base_url = BASE_URL
    crawl_interval_hours = 24

    def parse(self, content: str) -> list[EditalRaw]:
        """Converte o HTML da FINEP em objetos EditalRaw.

        Args:
            content: HTML da página de chamadas públicas.

        Returns:
            Lista de editais parseados.
        """
        soup = BeautifulSoup(content, "html.parser")
        editais = []

        rows = soup.select("tr, .chamada-item, .edital-item, a[href]")

        for row in rows:
            try:
                link_elem = row.find("a", href=True) if row.name != "a" else row
                if not link_elem:
                    continue

                titulo = link_elem.get_text(strip=True)
                url = link_elem["href"]

                if not titulo or not url or len(titulo) < 10:
                    continue

                if url and not url.startswith("http"):
                    url = f"https://www.finep.gov.br{url}" if url.startswith("/") else f"https://www.finep.gov.br/{url}"

                if titulo and url:
                    editais.append(EditalRaw(titulo=titulo, url=url, pdf_url=None, data_publicacao=None))
            except Exception as e:
                logger.warning(f"Erro ao parsear item da FINEP: {e}")
                continue

        return editais
