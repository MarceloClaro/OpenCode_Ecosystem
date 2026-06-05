"""Testes do deduplicador de editais — Issue #19."""

import uuid
from datetime import UTC, datetime


def make_edital(titulo="Edital X", url=None, portal_id=None, pdf_url=None):
    """Helper: cria um objeto similar ao modelo Edital para testes."""
    return {
        "id": uuid.uuid4(),
        "portal_id": portal_id or uuid.uuid4(),
        "titulo": titulo,
        "url_original": url or f"https://exemplo.com/{uuid.uuid4().hex[:8]}",
        "pdf_url": pdf_url,
        "criado_em": datetime.now(UTC),
    }


def test_mesma_url_eh_duplicata():
    """Editais com mesma url_original são duplicatas."""
    from pipeline.deduplicator import is_duplicate

    url = "https://portal.gov.br/edital/2026/01"
    a = make_edital(url=url)
    b = make_edital(url=url)

    assert is_duplicate(a, b) is True


def test_urls_diferentes_nao_sao_duplicatas():
    """Editais com URLs diferentes não são duplicatas."""
    from pipeline.deduplicator import is_duplicate

    a = make_edital(url="https://a.com/1")
    b = make_edital(url="https://b.com/2")

    assert is_duplicate(a, b) is False


def test_titulos_identicos_mesmo_portal_sao_duplicatas():
    """Mesmo título no mesmo portal é duplicata."""
    from pipeline.deduplicator import is_duplicate

    portal = uuid.uuid4()
    a = make_edital(titulo="Edital de Fomento 2026", portal_id=portal)
    b = make_edital(titulo="Edital de Fomento 2026", portal_id=portal)

    assert is_duplicate(a, b) is True


def test_titulos_muito_similares_sao_duplicatas():
    """Títulos com alta similaridade (>90%) são duplicatas."""
    from pipeline.deduplicator import is_duplicate

    a = make_edital(titulo="Chamada Pública FAPEG 01/2026")
    b = make_edital(titulo="Chamada Pública FAPEG 01/2026 - Retificação")

    # Similaridade alta (>80%), mesmo portal → duplicata
    a["portal_id"] = b["portal_id"]
    assert is_duplicate(a, b) is True


def test_titulos_diferentes_nao_sao_duplicatas():
    """Títulos com baixa similaridade não são duplicatas."""
    from pipeline.deduplicator import is_duplicate

    a = make_edital(titulo="Edital de Fomento à Pesquisa")
    b = make_edital(titulo="Chamada para Startups Inovadoras")

    assert is_duplicate(a, b) is False


def test_pdf_url_igual_eh_duplicata():
    """Mesmo PDF URL é duplicata (portais diferentes podem linkar o mesmo PDF)."""
    from pipeline.deduplicator import is_duplicate

    pdf = "https://portal.gov.br/edital.pdf"
    a = make_edital(pdf_url=pdf)
    b = make_edital(pdf_url=pdf)

    assert is_duplicate(a, b) is True


def test_deduplicate_remove_duplicatas_da_lista():
    """deduplicate() remove itens duplicados, mantendo o primeiro."""
    from pipeline.deduplicator import deduplicate

    url = "https://portal.gov.br/edital/2026/01"
    editais = [
        make_edital(titulo="Original", url=url),
        make_edital(titulo="Duplicata", url=url),  # mesma URL
        make_edital(titulo="Outro edital"),
    ]

    resultado = deduplicate(editais)
    assert len(resultado) == 2
    assert resultado[0]["titulo"] == "Original"


def test_deduplicate_lista_vazia():
    """Lista vazia retorna vazia sem erro."""
    from pipeline.deduplicator import deduplicate

    assert deduplicate([]) == []
