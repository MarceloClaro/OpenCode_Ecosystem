"""PDFExtractor — extrai texto de arquivos PDF.

Estratégia: pdfplumber (principal) → pymupdf (fallback).
"""

import logging
from io import BytesIO

from extractors.base import BaseExtractor

logger = logging.getLogger(__name__)

try:
    import pdfplumber
except ImportError:  # pragma: no cover
    pdfplumber = None

try:
    import pymupdf
except ImportError:  # pragma: no cover
    pymupdf = None


class PDFExtractor(BaseExtractor):
    """Extrai texto de PDFs, com fallback entre bibliotecas.

    pdfplumber: melhor para PDFs com tabelas e layout complexo.
    pymupdf: mais rápido, melhor para PDFs com texto simples.
    """

    def extract(self, raw: bytes | str) -> str:
        """Extrai texto de um PDF.

        Args:
            raw: Conteúdo do PDF em bytes.

        Returns:
            Texto extraído, ou string vazia em caso de falha.
        """
        if isinstance(raw, str):
            raw = raw.encode("utf-8")

        # 1. Tenta pdfplumber
        if pdfplumber is not None:
            try:
                return self._extract_pdfplumber(raw)
            except Exception as e:
                logger.warning(f"pdfplumber falhou: {e}")

        # 2. Fallback: pymupdf
        if pymupdf is not None:
            try:
                return self._extract_pymupdf(raw)
            except Exception as e:
                logger.error(f"pymupdf também falhou: {e}")

        logger.error("Nenhum extrator de PDF disponível ou ambos falharam")
        return ""

    def _extract_pdfplumber(self, raw: bytes) -> str:
        """Extrai texto via pdfplumber."""
        with pdfplumber.open(BytesIO(raw)) as pdf:  # type: ignore
            textos = []
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    textos.append(text)
            return "\n".join(textos)

    def _extract_pymupdf(self, raw: bytes) -> str:
        """Extrai texto via pymupdf."""
        with pymupdf.open(stream=raw, filetype="pdf") as doc:  # type: ignore
            textos = []
            for page in doc:
                text = page.get_text()  # type: ignore
                if text:
                    textos.append(text)
            return "\n".join(textos)
