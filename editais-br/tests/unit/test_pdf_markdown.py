"""Testes do PDFMarkdownExtractor."""

from unittest.mock import MagicMock, patch


def test_pdf_markdown_extractor_existe():
    from extractors.pdf_markdown import PDFMarkdownExtractor


def test_find_pdf_links():
    from extractors.pdf_markdown import PDFMarkdownExtractor

    ext = PDFMarkdownExtractor()
    html = """<a href="/edital.pdf">PDF</a><a href="https://x.com/doc.pdf?d=1">Doc</a><a href="/pag">N</a>"""
    links = ext.find_pdf_links(html, "https://fapesp.br")
    assert len(links) == 2


@patch("extractors.pdf_markdown.httpx.Client")
def test_download_pdf(mock_client):
    from extractors.pdf_markdown import PDFMarkdownExtractor

    mock_resp = MagicMock()
    mock_resp.content = b"%PDF-1.4"
    mock_resp.headers = {"content-type": "application/pdf"}
    mock_inst = MagicMock()
    mock_inst.get.return_value = mock_resp
    mock_inst.__enter__.return_value = mock_inst
    mock_inst.__exit__.return_value = False
    mock_client.return_value = mock_inst

    ext = PDFMarkdownExtractor()
    assert len(ext._download("https://ex.com/e.pdf")) > 0


def test_extract_pdf_integracao():
    """extract() deve baixar e converter PDF para Markdown."""
    from extractors.pdf_markdown import PDFMarkdownExtractor

    ext = PDFMarkdownExtractor()
    with patch.object(ext, "_download", return_value=b"%PDF-1.4"), patch.object(
        ext, "_pdf_to_markdown", return_value="# Edital Fomento\n\nConteúdo completo"
    ):
        result = ext.extract("https://ex.com/edital.pdf")
    assert "Edital Fomento" in result
    assert "Conteúdo completo" in result
