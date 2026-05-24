"""PDFExtractor refatorado com DI.

Implementa IPDFParser, IExtractor.
Estrategia: pdfplumber (principal) -> pymupdf (fallback) -> erro.
URL download integrado para PDFMarkdownExtractor.
"""

from __future__ import annotations
import logging
from io import BytesIO
from typing import Protocol

import httpx

from _reversa_sdd.reconstruction.editais_br_interfaces import IExtractor, IPDFParser

logger = logging.getLogger(__name__)

try:
    import pdfplumber

    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False
    pdfplumber = None  # type: ignore

try:
    import pymupdf

    HAS_PYMUPDF = True
except ImportError:
    HAS_PYMUPDF = False
    pymupdf = None  # type: ignore


class PDFDownloaderProtocol(Protocol):
    def __call__(self, url: str, timeout: int = 60) -> bytes: ...


def _default_downloader(url: str, timeout: int = 60) -> bytes:
    """Download padrao de PDF via httpx."""
    with httpx.Client(timeout=timeout, follow_redirects=True) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.content


class PDFExtractor(IPDFParser, IExtractor):
    """Extrator de PDF com fallchain e DI.

    Args:
        pdfplumber_first: Tentar pdfplumber antes de pymupdf.
        downloader: Funcao para download de PDF via URL.
    """

    def __init__(
        self,
        pdfplumber_first: bool = True,
        downloader: PDFDownloaderProtocol | None = None,
    ):
        self._pdfplumber_first = pdfplumber_first
        self._downloader = downloader or _default_downloader

    # -- IExtractor ----------------------------------------------------------

    def extract(self, raw: bytes | str) -> str:
        """Extrai texto de PDF (bytes) ou faz download se for URL.

        Args:
            raw: Bytes do PDF ou URL string comecando com http.

        Returns:
            Texto extraido.
        """
        if isinstance(raw, str) and raw.startswith("http"):
            raw = self._download(raw)

        if isinstance(raw, str):
            raw = raw.encode("utf-8")

        if not raw:
            return ""

        return self._extract_pdf(raw)

    # -- IPDFParser ----------------------------------------------------------

    def pdf_to_text(self, pdf_bytes: bytes) -> str:
        """Converte bytes PDF para texto."""
        return self._extract_pdf(pdf_bytes)

    def pdf_to_markdown(self, pdf_bytes: bytes) -> str:
        """Converte bytes PDF para Markdown."""
        if not HAS_PYMUPDF:
            logger.error("pymupdf nao instalado para conversao Markdown")
            return self.pdf_to_text(pdf_bytes)

        try:
            doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
            parts: list[str] = []

            for page_num, page in enumerate(doc, 1):
                try:
                    md = page.get_text("markdown")
                    if md.strip():
                        parts.append(md)
                except Exception:
                    text = page.get_text("text")
                    if text.strip():
                        parts.append(text)

                logger.debug(f"Pagina {page_num}/{len(doc)} processada")

            doc.close()
            return "\n\n".join(parts)

        except Exception as e:
            logger.error(f"Erro ao converter PDF para Markdown: {e}")
            return ""

    # -- Metodos internos ----------------------------------------------------

    def _download(self, url: str) -> bytes:
        """Baixa PDF da URL usando downloader injetado."""
        try:
            return self._downloader(url)
        except Exception as e:
            logger.error(f"Erro ao baixar PDF {url[:80]}: {e}")
            return b""

    def _extract_pdf(self, raw: bytes) -> str:
        """Extrai texto de bytes PDF com fallchain."""
        if self._pdfplumber_first and HAS_PDFPLUMBER:
            try:
                return self._extract_pdfplumber(raw)
            except Exception as e:
                logger.warning(f"pdfplumber falhou: {e}")

        if HAS_PYMUPDF:
            try:
                return self._extract_pymupdf(raw)
            except Exception as e:
                logger.error(f"pymupdf tambem falhou: {e}")

        if not self._pdfplumber_first and HAS_PDFPLUMBER:
            try:
                return self._extract_pdfplumber(raw)
            except Exception as e:
                logger.warning(f"pdfplumber falhou (2a tentativa): {e}")

        logger.error("Nenhum extrator de PDF disponivel ou ambos falharam")
        return ""

    def _extract_pdfplumber(self, raw: bytes) -> str:
        """Extrai texto via pdfplumber."""
        textos: list[str] = []
        with pdfplumber.open(BytesIO(raw)) as pdf:  # type: ignore
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    textos.append(text)
        return "\n".join(textos)

    def _extract_pymupdf(self, raw: bytes) -> str:
        """Extrai texto via pymupdf."""
        textos: list[str] = []
        with pymupdf.open(stream=raw, filetype="pdf") as doc:  # type: ignore
            for page in doc:
                text = page.get_text()
                if text:
                    textos.append(text)
        return "\n".join(textos)

    # -- Factory -------------------------------------------------------------

    @classmethod
    def create_default(cls) -> "PDFExtractor":
        """Cria instancia com configuracao padrao (pdfplumber first)."""
        return cls(pdfplumber_first=True)

    @classmethod
    def create_markdown_only(cls) -> "PDFExtractor":
        """Cria extrator focado em Markdown (pymupdf first)."""
        return cls(pdfplumber_first=False)
