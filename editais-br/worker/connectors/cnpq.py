"""CnpqConnector — conector para o portal CNPq (https://www.gov.br/cnpq)."""

import logging

import httpx
from bs4 import BeautifulSoup

from worker.connectors.base import BaseConnector, EditalRaw

logger = logging.getLogger(__name__)
BASE_URL = "https://www.gov.br/cnpq/pt-br/assuntos/noticias/cnpq-lanca-chamadas"


class CnpqConnector(BaseConnector):
    mode = "http"
    base_url = BASE_URL
    crawl_interval_hours = 12

    def fetch_editais(self) -> list[EditalRaw]:
        with httpx.Client(timeout=30) as client:
            response = client.get(self.base_url)
            response.raise_for_status()
            return self.parse(response.text)

    def parse(self, content: str) -> list[EditalRaw]:
        soup = BeautifulSoup(content, "html.parser")
        editais = []
        for link in soup.find_all("a", href=True):
            titulo = link.get_text(strip=True)
            url = link["href"]
            if titulo and url and not url.startswith("#"):
                if not url.startswith("http"):
                    url = f"https://www.gov.br{url}" if url.startswith("/") else f"https://www.gov.br/{url}"
                editais.append(EditalRaw(titulo=titulo, url=url))
        return editais
