"""SigepeConnector — portal de oportunidades do governo federal.

Fonte: https://oportunidades.sigepe.gov.br/oportunidades-portal/api/html/
HTML puro, sem JavaScript — httpx direto funciona.
"""

import logging
import re
import httpx
from bs4 import BeautifulSoup
from worker.connectors.base import BaseConnector, EditalRaw

logger = logging.getLogger(__name__)

BASE_URL = "https://oportunidades.sigepe.gov.br/oportunidades-portal/api/html/"


class SigepeConnector(BaseConnector):
    """Conector para o portal SIGEPE de oportunidades do governo federal.

    Lista editais/oportunidades de todos os ministérios.
    HTML estático — não requer navegador.
    """

    mode = "http"
    base_url = BASE_URL
    crawl_interval_hours = 6

    def fetch_editais(self) -> list[EditalRaw]:
        """Busca a lista de oportunidades do governo federal.

        Returns:
            Lista de editais brutos encontrados.
        """
        with httpx.Client(timeout=30, headers={"User-Agent": "Mozilla/5.0"}) as client:
            response = client.get(self.base_url)
            response.raise_for_status()
            return self.parse(response.text)

    def parse(self, content: str) -> list[EditalRaw]:
        """Converte o HTML do SIGEPE em objetos EditalRaw.

        Args:
            content: HTML da página de oportunidades.

        Returns:
            Lista de editais parseados.
        """
        soup = BeautifulSoup(content, "html.parser")
        editais = []

        # Cada edital tem um <p class="text-up-01"> com link dentro
        items = soup.select("p.text-up-01")

        for p_elem in items:
            try:
                link_elem = p_elem.find("a", class_="text-blue-warm-vivid-80")
                if not link_elem:
                    continue

                titulo = link_elem.get_text(strip=True)
                href = link_elem.get("href", "")

                # Extrai ID do edital (onclick="window.open(this.href+6428,...)")
                onclick = link_elem.get("onclick", "")
                id_match = re.search(r"this\.href\+(\d+)", onclick)
                edital_id = id_match.group(1) if id_match else ""
                url = f"https://oportunidades.sigepe.gov.br/oportunidades-portal/api/html/{edital_id}" if edital_id else ""

                # Data de inscrição — está em span.br-tag próximo
                parent_row = p_elem.find_parent("div", class_="row")
                data_publicacao = None
                if parent_row:
                    data_elem = parent_row.select_one(".br-tag")
                    if data_elem:
                        data_text = data_elem.get_text(strip=True)
                        date_match = re.search(r"(\d{2}/\d{2}/\d{4})", data_text)
                        if date_match:
                            data_publicacao = date_match.group(1)

                if titulo and url:
                    editais.append(
                        EditalRaw(
                            titulo=titulo,
                            url=url,
                            pdf_url=None,
                            data_publicacao=data_publicacao,
                        )
                    )
            except Exception as e:
                logger.warning(f"Erro ao parsear linha do SIGEPE: {e}")
                continue

        return editais
