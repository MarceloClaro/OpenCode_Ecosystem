"""HTMLExtractor refatorado com DI.

Implementa IHTMLParser, IExtractor.
Usa BeautifulSoup4 para parsing e oferece fallback configravel.
"""

from __future__ import annotations
import logging
from typing import Protocol

from _reversa_sdd.reconstruction.editais_br_interfaces import IExtractor, IHTMLParser

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup

    HAS_BS4 = True
except ImportError:
    HAS_BS4 = False
    BeautifulSoup = None  # type: ignore


class HTMLCleanerProtocol(Protocol):
    """Protocolo para funcao de limpeza HTML customizada."""

    def __call__(self, html: str) -> str: ...


class HTMLExtractor(IHTMLParser, IExtractor):
    """Extrator de texto HTML com DI.

    Args:
        cleaner: Funcao opcional de limpeza HTML (default: BeautifulSoup).
        remove_tags: Tags a remover durante extracao.
    """

    def __init__(
        self,
        cleaner: HTMLCleanerProtocol | None = None,
        remove_tags: list[str] | None = None,
    ):
        self._cleaner = cleaner
        self._remove_tags = remove_tags or ["script", "style", "nav", "footer", "header"]

    # -- IExtractor ----------------------------------------------------------

    def extract(self, raw: bytes | str) -> str:
        """Extrai texto limpo de HTML.

        Args:
            raw: Conteudo HTML (bytes ou string).

        Returns:
            Texto limpo extraido.
        """
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")

        if self._cleaner:
            return self._cleaner(raw)

        return self.clean_html(raw)

    # -- IHTMLParser ---------------------------------------------------------

    def clean_html(self, html: str) -> str:
        """Remove scripts, estilos e tags, retornando texto limpo."""
        if not HAS_BS4:
            logger.error("BeautifulSoup4 nao instalado")
            return ""

        soup = BeautifulSoup(html, "html.parser")

        for tag in soup(self._remove_tags):
            tag.decompose()

        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)

    def find_pdf_links(self, html: str, base_url: str) -> list[str]:
        """Encontra links de PDF em uma pagina HTML."""
        if not HAS_BS4:
            return []

        from urllib.parse import urljoin

        soup = BeautifulSoup(html, "html.parser")
        pdf_urls: list[str] = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(".pdf") or ".pdf?" in href.lower():
                url = urljoin(base_url, href)
                if url not in pdf_urls:
                    pdf_urls.append(url)

        return pdf_urls

    # -- Factory -------------------------------------------------------------

    @classmethod
    def create_default(cls) -> "HTMLExtractor":
        """Cria instancia com configuracao padrao."""
        return cls()
