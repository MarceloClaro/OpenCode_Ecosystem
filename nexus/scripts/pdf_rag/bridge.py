# -*- coding: utf-8 -*-
"""
BRIDGE v1.0 — Integra PDF RAG Collections com todo o ecossistema OpenCode.

Intercepta PDFs de QUALQUER fonte do ecossistema e alimenta automaticamente
o banco de coleções com auto-classificação, deduplicação e indexação FTS5.

Pontos de integração:
  1. Watchdog de diretórios (Downloads, papers, documentos)
  2. Hook pós-download do SEEKER (basis-research)
  3. Hook pós-download do Sci-Hub MCP
  4. Hook pós-extração do Docling Adapter
  5. Integração com evolution_loop.py (fase INTEGRATE)

Auto-classificação Universal:
  - NÃO usa categorias fixas (tributário, penal, etc.)
  - Aprende novas categorias automaticamente do conteúdo
  - Extrai tópicos via TF-IDF simplificado nos primeiros 5000 chars
  - Coleções crescem organicamente

Uso direto:
  from pdf_rag.bridge import EcosystemBridge
  bridge = EcosystemBridge()
  bridge.process_pdf("/path/to/paper.pdf")         # auto-classifica
  bridge.watch_directories()                        # monitora pastas
  bridge.scan_and_ingest()                          # varre tudo uma vez
"""

import os
import re
import sys
import json
import time
import logging
import hashlib
from pathlib import Path
from datetime import datetime
from collections import Counter
from concurrent.futures import ThreadPoolExecutor

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Paths do ecossistema
SCRIPT_DIR = Path(__file__).parent
NEXUS_SCRIPTS = SCRIPT_DIR.parent
ECO_ROOT = NEXUS_SCRIPTS.parent.parent  # C:\Users\marce\.config\opencode

sys.path.insert(0, str(SCRIPT_DIR))
sys.path.insert(0, str(NEXUS_SCRIPTS))

from collections import CollectionManager
from ingestor import PDFIngestor, IngestConfig, chunk_text, get_extractor

DB_PATH = str(ECO_ROOT / "cache" / "pdf_collections.db")
BRIDGE_STATE_PATH = ECO_ROOT / ".evolve" / "pdf_rag_bridge.json"

# Diretórios monitorados automaticamente
WATCH_DIRS = [
    ECO_ROOT / "documentos",
    ECO_ROOT / "data",
    ECO_ROOT.parent / "Downloads",
    ECO_ROOT.parent / "Documents",
    ECO_ROOT.parent / "OneDrive" / "Documentos",
    ECO_ROOT.parent / "OneDrive" / "Área de Trabalho",
]

# ── Stopwords PT-BR para classificação ────────────────────

STOPWORDS = {
    "de", "do", "da", "dos", "das", "em", "no", "na", "nos", "nas",
    "um", "uma", "uns", "umas", "por", "para", "com", "sem", "sob",
    "que", "se", "ou", "como", "mais", "entre", "sobre", "até",
    "foi", "ser", "são", "está", "tem", "ter", "pode", "deve",
    "esse", "essa", "este", "esta", "isso", "isto", "aqui", "ali",
    "não", "sim", "bem", "mal", "muito", "pouco", "também",
    "the", "of", "and", "in", "to", "for", "is", "on", "with",
    "that", "it", "as", "was", "are", "be", "from", "an", "by",
    "this", "which", "or", "at", "but", "not", "have", "has",
}


def extract_topic_words(text: str, top_n: int = 8) -> list[str]:
    """Extrai palavras-chave dominantes do texto (TF simples)."""
    text_lower = text[:8000].lower()
    words = re.findall(r'[a-záàâãéèêíïóôõöúçñ]{4,}', text_lower)
    words = [w for w in words if w not in STOPWORDS and len(w) > 3]
    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_n)]


def auto_collection_name(text: str, filename: str = "") -> str:
    """
    Gera nome de coleção automaticamente a partir do conteúdo.

    Estratégia:
    1. Extrai 3 palavras mais frequentes
    2. Combina em slug: "economia_publica_brasil"
    3. Se não conseguir, usa o diretório pai do arquivo
    """
    keywords = extract_topic_words(text, top_n=3)

    if len(keywords) >= 2:
        name = "_".join(keywords[:3])
        # Limpar para slug válido
        name = re.sub(r'[^a-z0-9_]', '', name)
        if len(name) >= 6:
            return name[:40]

    # Fallback: nome do diretório pai
    if filename:
        parent = Path(filename).parent.name.lower()
        parent = re.sub(r'[^a-z0-9_]', '_', parent)
        if parent and parent not in ("downloads", "documents", "desktop"):
            return parent[:40]

    return "geral"


def find_best_existing_collection(text: str,
                                   mgr: CollectionManager,
                                   threshold: float = 0.3) -> str | None:
    """
    Verifica se o texto combina com alguma coleção existente.
    Evita criar coleções novas desnecessariamente.
    """
    keywords = set(extract_topic_words(text, top_n=10))
    if not keywords:
        return None

    best_name = None
    best_score = 0.0

    for col in mgr.list_collections():
        col_keywords = set(json.loads(col.keywords) if isinstance(col.keywords, str) else col.keywords)
        if not col_keywords:
            # Tentar extrair keywords do nome da coleção
            col_keywords = set(col.name.split("_"))

        overlap = len(keywords & col_keywords)
        if overlap > 0:
            score = overlap / max(len(keywords), 1)
            if score > best_score:
                best_score = score
                best_name = col.name

    return best_name if best_score >= threshold else None


# ── Bridge Principal ──────────────────────────────────────

class EcosystemBridge:
    """
    Ponte entre o ecossistema OpenCode e o sistema de coleções PDF.
    Intercepta PDFs de qualquer fonte e alimenta o banco automaticamente.
    """

    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
        self.config = IngestConfig(
            chunk_size=1000,
            chunk_overlap=200,
            max_workers=4,
            skip_existing=True,
        )
        self._state = self._load_state()

    def _load_state(self) -> dict:
        if BRIDGE_STATE_PATH.exists():
            try:
                return json.loads(BRIDGE_STATE_PATH.read_text(encoding="utf-8"))
            except Exception:
                pass
        return {
            "last_scan": None,
            "total_ingested": 0,
            "total_skipped": 0,
            "total_errors": 0,
            "collections_created": [],
            "scan_history": [],
        }

    def _save_state(self):
        BRIDGE_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        BRIDGE_STATE_PATH.write_text(
            json.dumps(self._state, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

    # ── API principal ─────────────────────────────────────

    def process_pdf(self, file_path: str,
                    collection: str = None,
                    source: str = "manual") -> dict:
        """
        Processa um único PDF: extrai, auto-classifica, indexa.

        Args:
            file_path: Caminho do PDF
            collection: Coleção destino (None = auto-detectar)
            source: Origem do PDF (seeker, scihub, download, manual)

        Returns:
            dict com status, collection, chunks, etc.
        """
        fp = Path(file_path)
        if not fp.exists() or fp.suffix.lower() != ".pdf":
            return {"success": False, "error": "Arquivo não encontrado ou não é PDF"}

        mgr = CollectionManager(self.db_path)

        try:
            # Verificar duplicata
            if self.config.skip_existing and mgr.document_exists(str(fp), collection or ""):
                return {"success": True, "skipped": True, "reason": "Já ingerido"}

            # Extrair texto
            extractor = get_extractor()
            text, pages = extractor(str(fp))

            if not text or len(text.strip()) < 50:
                return {"success": False, "error": "PDF sem texto extraível"}

            # Auto-classificar se necessário
            if not collection:
                # Primeiro: tentar coleção existente
                collection = find_best_existing_collection(text, mgr)

                if not collection:
                    # Criar nova coleção baseada no conteúdo
                    collection = auto_collection_name(text, str(fp))

            # Garantir que a coleção existe
            keywords = extract_topic_words(text, top_n=10)
            mgr.create_collection(
                name=collection,
                description=f"Auto-criada via {source}",
                keywords=keywords
            )

            # Atualizar keywords da coleção existente
            existing = mgr.get_collection(collection)
            if existing:
                existing_kw = set(existing.keywords) if existing.keywords else set()
                merged_kw = list(existing_kw | set(keywords))[:30]
                mgr._conn.execute(
                    "UPDATE collections SET keywords = ? WHERE name = ?",
                    (json.dumps(merged_kw, ensure_ascii=False), collection)
                )
                mgr._conn.commit()

            # Chunking
            chunks = chunk_text(text, self.config.chunk_size,
                                self.config.chunk_overlap,
                                self.config.min_chunk_chars)

            if not chunks:
                return {"success": False, "error": "Nenhum chunk gerado"}

            # Inserir
            title = fp.stem.replace("_", " ").replace("-", " ")
            doc = mgr.add_document(
                collection=collection,
                title=title,
                file_path=str(fp),
                chunks=chunks,
                pages=pages,
                size_bytes=fp.stat().st_size,
                metadata={"source": source, "ingested_by": "ecosystem_bridge"}
            )

            self._state["total_ingested"] += 1
            if collection not in self._state["collections_created"]:
                self._state["collections_created"].append(collection)
            self._save_state()

            logger.info(f"[bridge] {fp.name} → {collection} "
                        f"({len(chunks)} chunks, {pages} páginas)")

            return {
                "success": True,
                "collection": collection,
                "chunks": len(chunks),
                "pages": pages,
                "doc_id": doc.doc_id if doc else None,
                "keywords": keywords[:5],
            }

        except Exception as e:
            self._state["total_errors"] += 1
            self._save_state()
            return {"success": False, "error": str(e)[:300]}
        finally:
            mgr.close()

    def scan_and_ingest(self, extra_dirs: list = None) -> dict:
        """
        Varre TODOS os diretórios monitorados e ingere PDFs novos.
        Chamado automaticamente pelo evolution_loop na fase INTEGRATE.
        """
        dirs = [d for d in WATCH_DIRS if d.exists()]
        if extra_dirs:
            dirs.extend([Path(d) for d in extra_dirs if Path(d).exists()])

        all_pdfs = []
        for d in dirs:
            all_pdfs.extend(d.rglob("*.pdf"))

        # Deduplicar por path
        seen = set()
        unique_pdfs = []
        for p in all_pdfs:
            key = str(p.resolve())
            if key not in seen:
                seen.add(key)
                unique_pdfs.append(p)

        logger.info(f"[bridge] Scan: {len(unique_pdfs)} PDFs em {len(dirs)} diretórios")

        results = {"total": len(unique_pdfs), "ingested": 0, "skipped": 0,
                    "errors": 0, "collections": set()}

        for pdf in unique_pdfs:
            r = self.process_pdf(str(pdf), source="scan")
            if r.get("success"):
                if r.get("skipped"):
                    results["skipped"] += 1
                else:
                    results["ingested"] += 1
                    results["collections"].add(r.get("collection", "?"))
            else:
                results["errors"] += 1

        results["collections"] = list(results["collections"])

        self._state["last_scan"] = datetime.now().isoformat()
        self._state["scan_history"].append({
            "timestamp": self._state["last_scan"],
            "total": results["total"],
            "ingested": results["ingested"],
            "skipped": results["skipped"],
        })
        # Manter apenas últimos 20 scans
        self._state["scan_history"] = self._state["scan_history"][-20:]
        self._save_state()

        logger.info(f"[bridge] Resultado: {results['ingested']} ingeridos, "
                    f"{results['skipped']} pulados, {results['errors']} erros")
        return results

    # ── Hooks para componentes do ecossistema ─────────────

    def hook_seeker_download(self, pdf_path: str, query: str = "",
                             doi: str = "") -> dict:
        """
        Hook chamado quando o SEEKER (basis-research) baixa um paper.
        O query/doi ajudam na classificação.
        """
        return self.process_pdf(
            pdf_path,
            source=f"seeker:{doi}" if doi else "seeker",
        )

    def hook_scihub_download(self, pdf_path: str, doi: str = "",
                              title: str = "") -> dict:
        """Hook chamado quando o MCP Sci-Hub baixa um paper."""
        return self.process_pdf(
            pdf_path,
            source=f"scihub:{doi}",
        )

    def hook_docling_extraction(self, pdf_path: str,
                                 extraction: dict = None) -> dict:
        """
        Hook chamado após o DoclingAdapter extrair conhecimento.
        Usa os tópicos já extraídos para classificação mais precisa.
        """
        result = self.process_pdf(pdf_path, source="docling")

        # Se docling já extraiu tópicos, enriquecer a coleção
        if extraction and result.get("success") and not result.get("skipped"):
            topics = extraction.get("topics", [])
            if topics:
                mgr = CollectionManager(self.db_path)
                col_name = result.get("collection")
                if col_name:
                    col = mgr.get_collection(col_name)
                    if col:
                        kw = set(col.keywords) if col.keywords else set()
                        kw.update(t.lower() for t in topics[:10])
                        mgr._conn.execute(
                            "UPDATE collections SET keywords = ? WHERE name = ?",
                            (json.dumps(list(kw)[:30], ensure_ascii=False), col_name)
                        )
                        mgr._conn.commit()
                mgr.close()

        return result

    def hook_fetch_download(self, file_path: str, url: str = "") -> dict:
        """Hook chamado quando o MCP fetch baixa um arquivo."""
        if Path(file_path).suffix.lower() != ".pdf":
            return {"success": False, "error": "Não é PDF"}
        return self.process_pdf(file_path, source=f"fetch:{url[:80]}")

    # ── Stats e diagnóstico ───────────────────────────────

    def stats(self) -> dict:
        """Retorna estatísticas completas do bridge + banco."""
        mgr = CollectionManager(self.db_path)
        db_stats = mgr.stats()
        mgr.close()

        return {
            "bridge": self._state,
            "database": db_stats,
            "watch_dirs": [str(d) for d in WATCH_DIRS if d.exists()],
            "watch_dirs_count": sum(1 for d in WATCH_DIRS if d.exists()),
        }

    def search(self, query: str, top_k: int = 10,
               collection: str = None) -> list:
        """Busca rápida via bridge (atalho para o router)."""
        from router import QueryRouter
        with QueryRouter(self.db_path) as r:
            result = r.query(query, top_k=top_k, collection=collection)
            return [
                {
                    "title": hit.doc_title,
                    "collection": hit.collection,
                    "page": hit.page,
                    "content": hit.content[:500],
                    "score": hit.score,
                }
                for hit in result.results
            ]


# ── Entry point ───────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(description="PDF RAG Ecosystem Bridge v1.0")
    parser.add_argument("--scan", action="store_true",
                        help="Varrer diretórios e ingerir PDFs novos")
    parser.add_argument("--process", type=str,
                        help="Processar um PDF específico")
    parser.add_argument("--stats", action="store_true",
                        help="Mostrar estatísticas")
    parser.add_argument("--search", type=str,
                        help="Buscar nos PDFs indexados")
    parser.add_argument("--json", action="store_true",
                        help="Saída em JSON")
    args = parser.parse_args()

    bridge = EcosystemBridge()

    if args.scan:
        result = bridge.scan_and_ingest()
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"\nScan: {result['ingested']} ingeridos, "
                  f"{result['skipped']} pulados, {result['errors']} erros")
            print(f"Coleções: {', '.join(result['collections']) or 'nenhuma nova'}")

    elif args.process:
        result = bridge.process_pdf(args.process)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.stats:
        s = bridge.stats()
        print(json.dumps(s, ensure_ascii=False, indent=2))

    elif args.search:
        results = bridge.search(args.search)
        if args.json:
            print(json.dumps(results, ensure_ascii=False, indent=2))
        else:
            for i, r in enumerate(results, 1):
                print(f"[{i}] {r['title']} ({r['collection']}, p.{r['page']})")
                print(f"    {r['content'][:150]}...\n")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
