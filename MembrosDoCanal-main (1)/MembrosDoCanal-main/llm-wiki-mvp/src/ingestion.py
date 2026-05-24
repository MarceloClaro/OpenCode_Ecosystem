"""Camada 1: Ingestão.

Recebe arquivos em PDF, TXT ou MD e:
1. Extrai texto puro
2. Salva o original em data/raw/
3. Indexa em SQLite como uma "fonte" pendente

Esta camada NÃO chama o LLM. Apenas prepara a fonte para o motor de síntese.
"""
from __future__ import annotations
import io
from pathlib import Path
from typing import BinaryIO

from pypdf import PdfReader

from src.storage import save_source, log_event


SUPPORTED_FORMATS = {"pdf", "txt", "md", "markdown"}


def detect_format(filename: str) -> str:
    """Retorna a extensão (sem ponto) em minúscula. Lança ValueError se não suportado."""
    ext = Path(filename).suffix.lower().lstrip(".")
    if ext == "markdown":
        ext = "md"
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(
            f"Formato '{ext}' não suportado. Formatos aceitos: {sorted(SUPPORTED_FORMATS)}"
        )
    return ext


def extract_text_from_pdf(file_obj: BinaryIO) -> str:
    """Extrai texto de PDF usando pypdf. Retorna string consolidada."""
    reader = PdfReader(file_obj)
    pages_text = []
    for i, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception as e:
            text = f"[Erro extraindo página {i+1}: {e}]"
        pages_text.append(f"--- Página {i+1} ---\n{text}")
    return "\n\n".join(pages_text)


def extract_text(filename: str, content_bytes: bytes) -> str:
    """Despacha extração baseado no formato."""
    fmt = detect_format(filename)
    if fmt == "pdf":
        return extract_text_from_pdf(io.BytesIO(content_bytes))
    elif fmt in ("txt", "md"):
        # Tenta UTF-8 primeiro, fallback para latin-1
        try:
            return content_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return content_bytes.decode("latin-1", errors="replace")
    raise ValueError(f"Formato '{fmt}' sem extrator definido")


def ingest_upload(filename: str, content_bytes: bytes) -> dict:
    """Pipeline completo de ingestão de upload: extrai, salva, indexa.

    Retorna metadados da fonte criada (ou existente, se duplicada).
    """
    fmt = detect_format(filename)
    text = extract_text(filename, content_bytes)

    if not text.strip():
        raise ValueError(f"O arquivo '{filename}' parece estar vazio ou ilegível.")

    source_id = save_source(filename, content_bytes, text, fmt)

    log_event(
        operation="upload",
        summary=f"Upload: {filename}",
        details={"source_id": source_id, "format": fmt, "char_count": len(text)}
    )

    return {
        "source_id": source_id,
        "filename": filename,
        "format": fmt,
        "char_count": len(text),
        "preview": text[:500],
    }
