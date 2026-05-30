"""HTMLExtractor — extrai texto de páginas HTML.

Usa BeautifulSoup4 para remover tags e extrair texto limpo.
"""

import logging

from extractors.base import BaseExtractor

logger = logging.getLogger(__name__)

try:
    from bs4 import BeautifulSoup
except ImportError:  # pragma: no cover
    BeautifulSoup = None


class HTMLExtractor(BaseExtractor):
    """Extrai texto limpo de páginas HTML."""

    def extract(self, raw: bytes | str) -> str:
        """Extrai texto de HTML, removendo scripts, estilos e tags.

        Args:
            raw: Conteúdo HTML (bytes ou string).

        Returns:
            Texto limpo extraído.
        """
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8", errors="replace")

        if BeautifulSoup is None:
            logger.error("BeautifulSoup4 não instalado")
            return ""

        soup = BeautifulSoup(raw, "html.parser")

        # Remove scripts e estilos
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        # Extrai texto
        text = soup.get_text(separator="\n", strip=True)

        # Remove linhas vazias consecutivas
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return "\n".join(lines)
