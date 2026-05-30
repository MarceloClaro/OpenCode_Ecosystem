"""Deduplicador de editais — detecta e remove duplicatas.

Estratégia:
1. URL original idêntica → duplicata (match exato)
2. PDF URL idêntica → duplicata (portais diferentes podem linkar o mesmo PDF)
3. Título muito similar (>85%) no mesmo portal → duplicata
"""

from difflib import SequenceMatcher

SIMILARITY_THRESHOLD = 0.85


def _normalize(text: str) -> str:
    """Normaliza texto: lowercase, remove espaços extras e pontuação."""
    import re

    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text


def _title_similarity(a: str, b: str) -> float:
    """Calcula similaridade entre dois títulos (0 a 1)."""
    return SequenceMatcher(None, _normalize(a), _normalize(b)).ratio()


def is_duplicate(a: dict, b: dict, threshold: float = SIMILARITY_THRESHOLD) -> bool:
    """Verifica se dois editais são duplicatas.

    Args:
        a: Dicionário representando o edital A.
        b: Dicionário representando o edital B.
        threshold: Limiar de similaridade para títulos (0 a 1).

    Returns:
        True se forem considerados duplicatas.
    """
    if a is b:
        return True

    # Regra 1: URL original idêntica
    url_a = a.get("url_original", "")
    url_b = b.get("url_original", "")
    if url_a and url_b and url_a == url_b:
        return True

    # Regra 2: PDF URL idêntica
    pdf_a = a.get("pdf_url")
    pdf_b = b.get("pdf_url")
    if pdf_a and pdf_b and pdf_a == pdf_b:
        return True

    # Regra 3: Título similar + mesmo portal
    titulo_a = a.get("titulo", "")
    titulo_b = b.get("titulo", "")
    portal_a = a.get("portal_id")
    portal_b = b.get("portal_id")

    if titulo_a and titulo_b and portal_a and portal_b:
        if portal_a == portal_b:
            # Um título contém o outro (ex: "Edital X" vs "Edital X - Retificação")
            norm_a = _normalize(titulo_a)
            norm_b = _normalize(titulo_b)
            if norm_a in norm_b or norm_b in norm_a:
                return True
            # Similaridade textual alta
            sim = _title_similarity(titulo_a, titulo_b)
            if sim >= threshold:
                return True

    return False


def deduplicate(editais: list[dict]) -> list[dict]:
    """Remove duplicatas de uma lista de editais, mantendo o primeiro de cada grupo.

    Args:
        editais: Lista de dicionários representando editais.

    Returns:
        Lista sem duplicatas.
    """
    unique: list[dict] = []

    for edital in editais:
        if not any(is_duplicate(edital, existente) for existente in unique):
            unique.append(edital)

    return unique
