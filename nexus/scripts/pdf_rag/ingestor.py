# -*- coding: utf-8 -*-
"""
INGESTOR v1.0 — Ingestão Paralela de PDFs com Chunking Inteligente

Processa 3000+ PDFs em paralelo, extrai texto, divide em chunks e
alimenta o CollectionManager (SQLite FTS5).

Estratégias de extração (fallback automático):
  1. pdfplumber (rápido, ~5s/PDF) — padrão
  2. PyMuPDF/fitz (se disponível)
  3. subprocess pdftotext (fallback)

Chunking:
  - Tamanho alvo: 1000 caracteres (configurável)
  - Overlap: 200 caracteres (contexto entre chunks)
  - Respeita quebras de parágrafo

Uso:
  from pdf_rag.ingestor import PDFIngestor
  ing = PDFIngestor("banco.db")
  ing.ingest_directory("/path/to/pdfs", collection="tributario")
  ing.ingest_file("/path/to/ctn.pdf", collection="tributario")
"""

import os
import re
import sys
import time
import hashlib
import logging
import subprocess
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Optional, Callable
from dataclasses import dataclass

from collections import CollectionManager

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Adicionar diretório pai ao path para imports do ecossistema
sys.path.insert(0, str(Path(__file__).parent.parent))


@dataclass
class IngestResult:
    file_path: str
    success: bool
    collection: str
    chunks: int = 0
    pages: int = 0
    duration_s: float = 0.0
    error: str = ""
    skipped: bool = False


@dataclass
class IngestConfig:
    chunk_size: int = 1000       # caracteres por chunk
    chunk_overlap: int = 200     # overlap entre chunks
    max_workers: int = 4         # threads paralelas
    skip_existing: bool = True   # pular PDFs já ingeridos
    min_chunk_chars: int = 50    # ignorar chunks muito curtos
    max_file_size_mb: int = 200  # ignorar PDFs > 200MB


# ── Extração de texto ─────────────────────────────────────

def _extract_pdfplumber(pdf_path: str) -> tuple[str, int]:
    """Extrai texto usando pdfplumber (rápido, ~5s/PDF)."""
    import pdfplumber
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        pages = len(pdf.pages)
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text_parts.append(t)
    return "\n\n".join(text_parts), pages


def _extract_pymupdf(pdf_path: str) -> tuple[str, int]:
    """Extrai texto usando PyMuPDF/fitz."""
    import fitz
    doc = fitz.open(pdf_path)
    pages = len(doc)
    text_parts = []
    for page in doc:
        t = page.get_text()
        if t:
            text_parts.append(t)
    doc.close()
    return "\n\n".join(text_parts), pages


def _extract_pdftotext(pdf_path: str) -> tuple[str, int]:
    """Extrai texto usando pdftotext (linha de comando)."""
    r = subprocess.run(
        ["pdftotext", "-layout", pdf_path, "-"],
        capture_output=True, text=True, timeout=60
    )
    if r.returncode != 0:
        raise RuntimeError(f"pdftotext falhou: {r.stderr[:200]}")
    text = r.stdout
    pages = text.count("\f") + 1
    return text, pages


def get_extractor() -> Callable:
    """Seleciona o melhor extrator disponível."""
    try:
        import pdfplumber
        return _extract_pdfplumber
    except ImportError:
        pass
    try:
        import fitz
        return _extract_pymupdf
    except ImportError:
        pass
    try:
        subprocess.run(["pdftotext", "-v"], capture_output=True, timeout=5)
        return _extract_pdftotext
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass
    raise ImportError(
        "Nenhum extrator de PDF encontrado. Instale um:\n"
        "  pip install pdfplumber    (recomendado, rápido)\n"
        "  pip install PyMuPDF       (alternativa)\n"
        "  Ou instale pdftotext no sistema"
    )


# ── Chunking ──────────────────────────────────────────────

def chunk_text(text: str, chunk_size: int = 1000,
               overlap: int = 200, min_chars: int = 50) -> list[str]:
    """
    Divide texto em chunks respeitando parágrafos.

    Estratégia:
    1. Divide por parágrafos (\\n\\n)
    2. Agrupa parágrafos até atingir chunk_size
    3. Adiciona overlap do chunk anterior
    """
    if not text or len(text.strip()) < min_chars:
        return []

    # Limpar texto
    text = re.sub(r'\n{3,}', '\n\n', text.strip())
    paragraphs = text.split('\n\n')

    chunks = []
    current = []
    current_len = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if current_len + len(para) > chunk_size and current:
            chunk_text_str = '\n\n'.join(current)
            if len(chunk_text_str) >= min_chars:
                chunks.append(chunk_text_str)

            # Overlap: manter últimos parágrafos que cabem no overlap
            overlap_parts = []
            overlap_len = 0
            for p in reversed(current):
                if overlap_len + len(p) > overlap:
                    break
                overlap_parts.insert(0, p)
                overlap_len += len(p)

            current = overlap_parts + [para]
            current_len = sum(len(p) for p in current)
        else:
            current.append(para)
            current_len += len(para)

    # Último chunk
    if current:
        chunk_text_str = '\n\n'.join(current)
        if len(chunk_text_str) >= min_chars:
            chunks.append(chunk_text_str)

    return chunks


# ── Classificador automático de coleção ───────────────────

DEFAULT_COLLECTION_KEYWORDS = {
    "tributario": ["tributo", "imposto", "icms", "iss", "irpf", "ctn", "tributário",
                   "fiscal", "fisco", "contribuinte", "alíquota", "base de cálculo"],
    "constitucional": ["constituição", "constitucional", "stf", "supremo", "emenda",
                       "direito fundamental", "art. 5", "mandado de segurança"],
    "civil": ["código civil", "contrato", "obrigação", "responsabilidade civil",
              "posse", "propriedade", "família", "sucessão", "herança"],
    "penal": ["código penal", "crime", "pena", "dosimetria", "tipicidade",
              "antijuridicidade", "culpabilidade", "prisão"],
    "processual": ["cpc", "processo", "recurso", "sentença", "tutela",
                   "citação", "intimação", "agravo", "apelação"],
    "trabalhista": ["clt", "trabalhista", "empregado", "empregador", "rescisão",
                    "férias", "fgts", "justa causa"],
    "administrativo": ["administrativo", "licitação", "contrato administrativo",
                       "servidor público", "concurso", "improbidade"],
    "ambiental": ["ambiental", "meio ambiente", "licenciamento", "ibama",
                  "desmatamento", "poluição", "sustentabilidade"],
    "tecnologia": ["software", "lgpd", "dados pessoais", "inteligência artificial",
                   "marco civil", "internet", "tecnologia", "digital"],
    "medicina": ["médico", "saúde", "diagnóstico", "tratamento", "paciente",
                 "farmacêutico", "epidemiologia", "clínico"],
    "engenharia": ["engenharia", "estrutural", "concreto", "projeto", "cálculo",
                   "resistência", "materiais", "construção"],
    "geral": [],  # fallback
}


def classify_collection(text: str,
                        keywords_map: dict = None) -> tuple[str, float]:
    """
    Classifica texto na coleção mais provável.
    Retorna (nome_coleção, confiança 0-1).
    """
    kw_map = keywords_map or DEFAULT_COLLECTION_KEYWORDS
    text_lower = text[:5000].lower()  # amostra dos primeiros 5k chars

    scores = {}
    for collection, keywords in kw_map.items():
        if not keywords:
            continue
        hits = sum(1 for kw in keywords if kw.lower() in text_lower)
        scores[collection] = hits / max(len(keywords), 1)

    if not scores or max(scores.values()) == 0:
        return "geral", 0.0

    best = max(scores, key=scores.get)
    return best, scores[best]


# ── Ingestor Principal ────────────────────────────────────

class PDFIngestor:
    """Ingestão paralela de PDFs com auto-classificação em coleções."""

    def __init__(self, db_path: str = "pdf_collections.db",
                 config: IngestConfig = None):
        self.mgr = CollectionManager(db_path)
        self.config = config or IngestConfig()
        self.extractor = get_extractor()
        self._results: list[IngestResult] = []

    def ingest_file(self, file_path: str, collection: str = None,
                    title: str = None, metadata: dict = None) -> IngestResult:
        """Ingere um único PDF."""
        fp = Path(file_path)
        start = time.time()

        # Validações
        if not fp.exists():
            return IngestResult(str(fp), False, collection or "?",
                                error="Arquivo não encontrado")
        if not fp.suffix.lower() == ".pdf":
            return IngestResult(str(fp), False, collection or "?",
                                error="Não é PDF")
        if fp.stat().st_size > self.config.max_file_size_mb * 1048576:
            return IngestResult(str(fp), False, collection or "?",
                                error=f"Arquivo > {self.config.max_file_size_mb}MB")

        try:
            # Extrair texto
            text, pages = self.extractor(str(fp))

            if not text or len(text.strip()) < self.config.min_chunk_chars:
                return IngestResult(str(fp), False, collection or "?",
                                    error="PDF sem texto extraível (escaneado?)")

            # Auto-classificar se coleção não especificada
            if not collection:
                collection, confidence = classify_collection(text)
                logger.info(f"Auto-classificado: {fp.name} → {collection} "
                            f"(confiança: {confidence:.0%})")

            # Criar coleção se necessário
            self.mgr.create_collection(collection)

            # Verificar duplicata
            if self.config.skip_existing and self.mgr.document_exists(str(fp), collection):
                return IngestResult(str(fp), True, collection, skipped=True)

            # Chunking
            chunks = chunk_text(
                text,
                chunk_size=self.config.chunk_size,
                overlap=self.config.chunk_overlap,
                min_chars=self.config.min_chunk_chars
            )

            if not chunks:
                return IngestResult(str(fp), False, collection,
                                    error="Nenhum chunk gerado")

            # Inserir no banco
            doc_title = title or fp.stem.replace("_", " ").replace("-", " ")
            doc = self.mgr.add_document(
                collection=collection,
                title=doc_title,
                file_path=str(fp),
                chunks=chunks,
                pages=pages,
                size_bytes=fp.stat().st_size,
                metadata=metadata or {}
            )

            duration = time.time() - start
            return IngestResult(
                str(fp), True, collection,
                chunks=len(chunks), pages=pages, duration_s=duration
            )

        except Exception as e:
            duration = time.time() - start
            return IngestResult(str(fp), False, collection or "?",
                                duration_s=duration, error=str(e)[:300])

    def ingest_directory(self, dir_path: str, collection: str = None,
                         recursive: bool = True,
                         progress_callback: Callable = None) -> list[IngestResult]:
        """
        Ingere todos os PDFs de um diretório em paralelo.

        Args:
            dir_path: Caminho do diretório
            collection: Coleção destino (None = auto-classificar)
            recursive: Buscar em subdiretórios
            progress_callback: fn(current, total, result) chamada a cada PDF
        """
        dp = Path(dir_path)
        if not dp.exists():
            logger.error(f"Diretório não existe: {dp}")
            return []

        pattern = "**/*.pdf" if recursive else "*.pdf"
        pdfs = sorted(dp.glob(pattern))
        total = len(pdfs)
        logger.info(f"Encontrados {total} PDFs em {dp}")

        if total == 0:
            return []

        results = []
        completed = 0

        with ThreadPoolExecutor(max_workers=self.config.max_workers) as pool:
            futures = {
                pool.submit(self.ingest_file, str(pdf), collection): pdf
                for pdf in pdfs
            }

            for future in as_completed(futures):
                pdf = futures[future]
                try:
                    result = future.result(timeout=300)
                except Exception as e:
                    result = IngestResult(str(pdf), False, collection or "?",
                                          error=f"Timeout/Exception: {e}")

                results.append(result)
                completed += 1

                # Log de progresso
                status = "✓" if result.success else "✗"
                skip = " [SKIP]" if result.skipped else ""
                logger.info(
                    f"[{completed}/{total}] {status} {pdf.name} "
                    f"→ {result.collection} "
                    f"({result.chunks} chunks, {result.duration_s:.1f}s){skip}"
                )

                if progress_callback:
                    progress_callback(completed, total, result)

        self._results = results
        self._print_summary(results)
        return results

    def ingest_with_mapping(self, mapping: dict[str, list[str]]) -> list[IngestResult]:
        """
        Ingere PDFs com mapeamento explícito coleção → arquivos.

        Args:
            mapping: {"tributario": ["/path/1.pdf", "/path/2.pdf"], ...}
        """
        all_results = []
        for collection, files in mapping.items():
            self.mgr.create_collection(collection)
            for f in files:
                result = self.ingest_file(f, collection=collection)
                all_results.append(result)
        self._print_summary(all_results)
        return all_results

    def _print_summary(self, results: list[IngestResult]):
        """Imprime resumo da ingestão."""
        total = len(results)
        success = sum(1 for r in results if r.success and not r.skipped)
        skipped = sum(1 for r in results if r.skipped)
        failed = sum(1 for r in results if not r.success)
        chunks = sum(r.chunks for r in results)
        duration = sum(r.duration_s for r in results)

        collections = set(r.collection for r in results if r.success)

        print(f"\n{'='*60}")
        print(f"  INGESTÃO CONCLUÍDA")
        print(f"{'='*60}")
        print(f"  Total:     {total} PDFs")
        print(f"  Sucesso:   {success}")
        print(f"  Pular:     {skipped} (já existiam)")
        print(f"  Falha:     {failed}")
        print(f"  Chunks:    {chunks}")
        print(f"  Coleções:  {', '.join(collections) if collections else '-'}")
        print(f"  Duração:   {duration:.1f}s ({duration/60:.1f} min)")
        if total > 0:
            print(f"  Média:     {duration/max(total-skipped,1):.1f}s/PDF")
        print(f"{'='*60}")

        if failed > 0:
            print(f"\n  ERROS ({failed}):")
            for r in results:
                if not r.success:
                    print(f"    ✗ {Path(r.file_path).name}: {r.error[:80]}")

    def stats(self) -> dict:
        """Retorna estatísticas do banco."""
        return self.mgr.stats()

    def close(self):
        self.mgr.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
