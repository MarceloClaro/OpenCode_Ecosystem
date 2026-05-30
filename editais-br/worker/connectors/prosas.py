"""ProsasConnector — conector para o portal Prosas (https://prosas.com.br/editais).

Modo HTTP — o portal não requer browser anti-bot.
"""

import logging

import httpx
from bs4 import BeautifulSoup

from worker.connectors.base import BaseConnector, EditalRaw

logger = logging.getLogger(__name__)

BASE_URL = "https://prosas.com.br/editais"


class ProsasConnector(BaseConnector):
    """Conector para o portal Prosas.

    Extrai editais via HTTP e faz parsing do HTML com BeautifulSoup.
    """

    mode = "http"
    base_url = BASE_URL
    crawl_interval_hours = 6

    def fetch_editais(self) -> list[EditalRaw]:
        """Busca a lista de editais do Prosas.

        Returns:
            Lista de editais brutos encontrados.
        """
        with httpx.Client(timeout=30) as client:
            response = client.get(self.base_url)
            response.raise_for_status()
            return self.parse(response.text)

    def parse(self, content: str) -> list[EditalRaw]:
        """Converte o HTML do Prosas em objetos EditalRaw.

        Args:
            content: HTML da página de listagem de editais.

        Returns:
            Lista de editais parseados.
        """
        soup = BeautifulSoup(content, "html.parser")
        editais = []

        # Cada edital está em um card
        cards = soup.select(".edital-card, .card-edital, article")

        for card in cards:
            try:
                titulo_elem = card.find("h2") or card.find("h3")
                link_elem = card.find("a", href=True)
                data_elem = card.select_one(".date, .data, time")

                titulo = titulo_elem.get_text(strip=True) if titulo_elem else ""
                url = link_elem["href"] if link_elem else ""
                data = data_elem.get_text(strip=True) if data_elem else None

                # URL relativa → absoluta
                if url and not url.startswith("http"):
                    url = f"https://prosas.com.br{url}" if url.startswith("/") else f"https://prosas.com.br/{url}"

                if titulo and url:
                    editais.append(
                        EditalRaw(
                            titulo=titulo,
                            url=url,
                            pdf_url=None,  # Prosas pode ter PDF link separado
                            data_publicacao=data,
                        )
                    )
            except Exception as e:
                logger.warning(f"Erro ao parsear card do Prosas: {e}")
                continue

        return editais
