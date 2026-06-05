"""PDFMarkdownExtractor — baixa PDF e converte para Markdown."""

import logging
import httpx
from io import BytesIO
from extractors.base import BaseExtractor

logger = logging.getLogger(__name__)

try:
    import pymupdf  # type: ignore

    HAS_PYMUPDF = True
except ImportError:  # pragma: no cover
    HAS_PYMUPDF = False


class PDFMarkdownExtractor(BaseExtractor):
    """Baixa um PDF de uma URL e converte para texto Markdown."""

    def extract(self, raw: bytes | str) -> str:
        """Converte PDF (bytes ou URL) para Markdown.

        Se for URL (string começando com http), faz o download primeiro.
        Se for bytes, processa direto.
        """
        if isinstance(raw, str) and raw.startswith("http"):
            raw = self._download(raw)

        if not raw:
            return ""

        return self._pdf_to_markdown(raw)

    def _download(self, url: str) -> bytes:
        """Baixa o PDF da URL."""
        try:
            with httpx.Client(timeout=60, follow_redirects=True) as client:
                response = client.get(url)
                response.raise_for_status()
                content_type = response.headers.get("content-type", "")
                if "pdf" not in content_type and not url.endswith(".pdf"):
                    logger.warning(f"URL não parece ser PDF: {content_type} — {url[:80]}")
                return response.content
        except Exception as e:
            logger.error(f"Erro ao baixar PDF {url[:80]}: {e}")
            return b""

    def _pdf_to_markdown(self, pdf_bytes: bytes) -> str:
        """Converte PDF bytes para Markdown usando pymupdf."""
        if not HAS_PYMUPDF:
            logger.error("pymupdf não instalado")
            return ""

        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            markdown_parts = []

            for page_num, page in enumerate(doc, 1):
                # Extrai texto como markdown (pymupdf >= 1.23)
                try:
                    md = page.get_text("markdown")
                    if md.strip():
                        markdown_parts.append(md)
                except Exception:
                    # Fallback: texto simples
                    text = page.get_text("text")
                    if text.strip():
                        markdown_parts.append(text)

                logger.debug(f"Página {page_num}/{len(doc)} processada")

            doc.close()
            return "\n\n".join(markdown_parts)

        except Exception as e:
            logger.error(f"Erro ao converter PDF para Markdown: {e}")
            return ""

    def find_pdf_links(self, html: str, base_url: str) -> list[str]:
        """Encontra links de PDF em uma página HTML."""
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin

        soup = BeautifulSoup(html, "html.parser")
        pdf_urls = []

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.lower().endswith(".pdf") or ".pdf?" in href.lower():
                url = urljoin(base_url, href)
                if url not in pdf_urls:
                    pdf_urls.append(url)

        return pdf_urls
