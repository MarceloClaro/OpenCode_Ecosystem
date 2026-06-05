"""Testes dos extractors — Issue #10 (PDF) e #11 (HTML)."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

FIXTURES = Path(__file__).parents[1] / "fixtures"


def test_base_extractor_existe_e_eh_abc():
    """BaseExtractor deve existir, ser ABC, com extract()."""
    from abc import ABC

    from extractors.base import BaseExtractor

    assert issubclass(BaseExtractor, ABC)
    assert hasattr(BaseExtractor, "extract")


class TestPDFExtractor:
    """Testes do PDFExtractor."""

    def test_pdf_extractor_existe(self):
        """PDFExtractor deve ser importável."""

    def test_pdf_extractor_herda_base(self):
        """PDFExtractor deve herdar de BaseExtractor."""
        from extractors.base import BaseExtractor
        from extractors.pdf import PDFExtractor

        assert issubclass(PDFExtractor, BaseExtractor)

    @patch("extractors.pdf.pdfplumber")
    def test_extrai_texto_com_pdfplumber(self, mock_pdfplumber):
        """Deve usar pdfplumber como primeira opção."""
        from extractors.pdf import PDFExtractor

        # Mock: pdfplumber.open()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Texto extraído do PDF."
        mock_pdf = MagicMock()
        mock_pdf.pages = [mock_page]
        mock_pdf.__enter__ = MagicMock(return_value=mock_pdf)
        mock_pdf.__exit__ = MagicMock(return_value=False)
        mock_pdfplumber.open.return_value = mock_pdf

        extractor = PDFExtractor()
        result = extractor.extract(b"%PDF-1.4 fake pdf content")

        assert "Texto extraído" in result
        mock_pdfplumber.open.assert_called_once()

    @patch("extractors.pdf.pymupdf")
    @patch("extractors.pdf.pdfplumber")
    def test_fallback_pymupdf_quando_pdfplumber_falha(self, mock_plumber, mock_mupdf):
        """Quando pdfplumber falha, deve usar pymupdf como fallback."""
        from extractors.pdf import PDFExtractor

        # pdfplumber lança exceção
        mock_plumber.open.side_effect = Exception("PDF quebrado")

        # pymupdf funciona
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_page.get_text.return_value = "Texto via pymupdf."
        mock_doc.__iter__ = MagicMock(return_value=iter([mock_page]))
        mock_doc.__len__ = MagicMock(return_value=1)
        mock_doc.__enter__ = MagicMock(return_value=mock_doc)
        mock_doc.__exit__ = MagicMock(return_value=False)
        mock_mupdf.open.return_value = mock_doc

        extractor = PDFExtractor()
        result = extractor.extract(b"%PDF-1.4 fake pdf content")

        assert "Texto via pymupdf" in result
        mock_plumber.open.assert_called_once()
        mock_mupdf.open.assert_called_once()

    @patch("extractors.pdf.pymupdf")
    @patch("extractors.pdf.pdfplumber")
    def test_retorna_string_vazia_quando_ambos_falham(self, mock_plumber, mock_mupdf):
        """Quando ambos falham, retorna string vazia."""
        from extractors.pdf import PDFExtractor

        mock_plumber.open.side_effect = Exception("plumber fail")
        mock_mupdf.open.side_effect = Exception("mupdf fail")

        extractor = PDFExtractor()
        result = extractor.extract(b"%PDF-1.4 fake pdf content")

        assert result == ""

    def test_extrai_de_arquivo_pdf_real(self):
        """Teste com um PDF fixture real (se existir)."""
        pdf_path = FIXTURES / "exemplo.pdf"
        if not pdf_path.exists():
            pytest.skip("Fixture exemplo.pdf não encontrada")

        from extractors.pdf import PDFExtractor

        extractor = PDFExtractor()
        result = extractor.extract(pdf_path.read_bytes())

        assert isinstance(result, str)
        assert len(result) > 0


class TestHTMLExtractor:
    """Testes do HTMLExtractor — Issue #11."""

    def test_html_extractor_existe(self):
        """HTMLExtractor deve ser importável."""

    def test_html_extractor_herda_base(self):
        """HTMLExtractor deve herdar de BaseExtractor."""
        from extractors.base import BaseExtractor
        from extractors.html import HTMLExtractor

        assert issubclass(HTMLExtractor, BaseExtractor)

    def test_extrai_texto_de_html_simples(self):
        """Deve extrair texto de HTML simples."""
        from extractors.html import HTMLExtractor

        html = "<html><body><p>Edital de fomento 2026</p></body></html>"
        extractor = HTMLExtractor()
        result = extractor.extract(html)

        assert "Edital de fomento 2026" in result

    def test_remove_scripts_e_styles(self):
        """Deve remover tags script e style."""
        from extractors.html import HTMLExtractor

        html = """
        <html>
        <head><style>.classe { color: red; }</style></head>
        <body>
        <script>console.log('teste');</script>
        <p>Texto visível</p>
        </body>
        </html>
        """
        extractor = HTMLExtractor()
        result = extractor.extract(html)

        assert "Texto visível" in result
        assert "console.log" not in result
        assert "color: red" not in result

    def test_texto_limpo_sem_tags(self):
        """Resultado não deve conter tags HTML."""
        from extractors.html import HTMLExtractor

        html = '<div><h1>Título</h1><p>Parágrafo <strong>negrito</strong>.</p></div>'
        extractor = HTMLExtractor()
        result = extractor.extract(html)

        assert "<h1>" not in result
        assert "<strong>" not in result
        assert "Título" in result
        assert "negrito" in result

    def test_aceita_bytes(self):
        """Deve aceitar conteúdo em bytes."""
        from extractors.html import HTMLExtractor

        html = b"<html><body><p>Conteudo</p></body></html>"
        extractor = HTMLExtractor()
        result = extractor.extract(html)

        assert "Conteudo" in result

    def test_html_vazio_retorna_string_vazia(self):
        """HTML vazio retorna string vazia."""
        from extractors.html import HTMLExtractor

        extractor = HTMLExtractor()
        assert extractor.extract("") == ""

    def test_extrai_de_arquivo_html_real(self):
        """Teste com um HTML fixture real (se existir)."""
        html_path = FIXTURES / "exemplo.html"
        if not html_path.exists():
            pytest.skip("Fixture exemplo.html não encontrada")

        from extractors.html import HTMLExtractor

        extractor = HTMLExtractor()
        result = extractor.extract(html_path.read_bytes())

        assert isinstance(result, str)
        assert len(result) > 0
