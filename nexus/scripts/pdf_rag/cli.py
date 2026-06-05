# -*- coding: utf-8 -*-
"""
CLI v1.0 — Interface de linha de comando do PDF RAG Collection System

Uso:
  python -m pdf_rag.cli ingest /path/to/pdfs --collection tributario
  python -m pdf_rag.cli ingest /path/to/pdfs --auto              # auto-classifica
  python -m pdf_rag.cli search "prescrição intercorrente"
  python -m pdf_rag.cli search "prescrição" --collection tributario
  python -m pdf_rag.cli interactive                               # modo REPL
  python -m pdf_rag.cli collections                               # lista coleções
  python -m pdf_rag.cli stats                                     # estatísticas
  python -m pdf_rag.cli create-collection nome "Descrição"
"""

import argparse
import json
import sys
from pathlib import Path

# Garantir imports do diretório correto
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from collections import CollectionManager
from ingestor import PDFIngestor, IngestConfig
from router import QueryRouter


DEFAULT_DB = str(Path(__file__).parent.parent.parent.parent / "cache" / "pdf_collections.db")


def cmd_ingest(args):
    """Ingere PDFs de um diretório."""
    config = IngestConfig(
        chunk_size=args.chunk_size,
        chunk_overlap=args.overlap,
        max_workers=args.workers,
        skip_existing=not args.force,
    )
    collection = args.collection if not args.auto else None

    with PDFIngestor(args.db, config) as ing:
        if Path(args.path).is_file():
            result = ing.ingest_file(args.path, collection=collection)
            status = "✓" if result.success else "✗"
            print(f"{status} {result.file_path} → {result.collection} "
                  f"({result.chunks} chunks)")
        else:
            ing.ingest_directory(
                args.path,
                collection=collection,
                recursive=not args.no_recursive
            )
        print(f"\n{json.dumps(ing.stats(), indent=2, ensure_ascii=False)}")


def cmd_search(args):
    """Busca full-text com roteamento."""
    with QueryRouter(args.db) as router:
        result = router.query(
            args.query,
            top_k=args.limit,
            collection=args.collection
        )

        print(f"\nQuery: \"{result.query}\"")
        print(f"Tempo: {result.search_time_ms:.0f}ms")
        print(f"Coleções buscadas: {result.collections_searched}\n")

        for r in result.routes:
            print(f"  Rota: {r.collection} (confiança: {r.confidence:.0%})")

        if result.results:
            print(f"\n{'─'*60}")
            for i, hit in enumerate(result.results, 1):
                print(f"\n  [{i}] {hit.doc_title}")
                print(f"      Coleção: {hit.collection} | Página: {hit.page}")
                preview = hit.content[:300].replace("\n", " ")
                print(f"      {preview}...")
        else:
            print("\n  Nenhum resultado.")


def cmd_interactive(args):
    """Modo interativo."""
    with QueryRouter(args.db) as router:
        router.interactive()


def cmd_collections(args):
    """Lista coleções."""
    with CollectionManager(args.db) as mgr:
        cols = mgr.list_collections()
        if not cols:
            print("Nenhuma coleção encontrada.")
            return
        print(f"\n{'Nome':<20} {'Docs':>6} {'Chunks':>8} {'Criação'}")
        print("─" * 60)
        for c in cols:
            print(f"{c.name:<20} {c.doc_count:>6} {c.chunk_count:>8} "
                  f"{c.created_at[:10]}")
        print(f"\nTotal: {len(cols)} coleções, "
              f"{sum(c.doc_count for c in cols)} documentos, "
              f"{sum(c.chunk_count for c in cols)} chunks")


def cmd_create_collection(args):
    """Cria uma coleção."""
    with CollectionManager(args.db) as mgr:
        col = mgr.create_collection(args.name, args.description)
        print(f"Coleção '{col.name}' criada.")


def cmd_stats(args):
    """Mostra estatísticas."""
    with CollectionManager(args.db) as mgr:
        s = mgr.stats()
        print(json.dumps(s, indent=2, ensure_ascii=False))


def cmd_documents(args):
    """Lista documentos de uma coleção."""
    with CollectionManager(args.db) as mgr:
        docs = mgr.list_documents(args.collection)
        if not docs:
            print("Nenhum documento encontrado.")
            return
        print(f"\n{'Título':<40} {'Chunks':>6} {'Páginas':>7} {'Coleção'}")
        print("─" * 70)
        for d in docs:
            title = d.title[:38] + ".." if len(d.title) > 40 else d.title
            print(f"{title:<40} {d.chunk_count:>6} {d.pages:>7} {d.collection}")


def main():
    parser = argparse.ArgumentParser(
        description="PDF RAG Collection System v1.0 — Busca hierárquica em 3000+ PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s ingest ./pdfs --collection tributario     # ingerir com coleção fixa
  %(prog)s ingest ./pdfs --auto                      # auto-classificar
  %(prog)s search "prescrição intercorrente"         # busca roteada
  %(prog)s search "ICMS" -c tributario               # busca direta
  %(prog)s interactive                               # modo REPL
  %(prog)s collections                               # listar coleções
  %(prog)s stats                                     # estatísticas
        """
    )
    parser.add_argument("--db", default=DEFAULT_DB,
                        help=f"Caminho do banco SQLite (default: {DEFAULT_DB})")

    sub = parser.add_subparsers(dest="command")

    # Ingest
    p_ingest = sub.add_parser("ingest", help="Ingerir PDFs")
    p_ingest.add_argument("path", help="Arquivo ou diretório")
    p_ingest.add_argument("-c", "--collection", help="Coleção destino")
    p_ingest.add_argument("--auto", action="store_true",
                          help="Auto-classificar em coleções")
    p_ingest.add_argument("--chunk-size", type=int, default=1000)
    p_ingest.add_argument("--overlap", type=int, default=200)
    p_ingest.add_argument("--workers", type=int, default=4)
    p_ingest.add_argument("--force", action="store_true",
                          help="Re-ingerir mesmo se já existir")
    p_ingest.add_argument("--no-recursive", action="store_true")

    # Search
    p_search = sub.add_parser("search", help="Buscar nos PDFs")
    p_search.add_argument("query", help="Texto da busca")
    p_search.add_argument("-c", "--collection", help="Coleção específica")
    p_search.add_argument("-n", "--limit", type=int, default=10)

    # Interactive
    sub.add_parser("interactive", help="Modo interativo (REPL)")

    # Collections
    sub.add_parser("collections", help="Listar coleções")

    # Create Collection
    p_create = sub.add_parser("create-collection", help="Criar coleção")
    p_create.add_argument("name", help="Nome da coleção")
    p_create.add_argument("description", nargs="?", default="",
                          help="Descrição da coleção")

    # Stats
    sub.add_parser("stats", help="Estatísticas do banco")

    # Documents
    p_docs = sub.add_parser("documents", help="Listar documentos")
    p_docs.add_argument("-c", "--collection", help="Filtrar por coleção")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    commands = {
        "ingest": cmd_ingest,
        "search": cmd_search,
        "interactive": cmd_interactive,
        "collections": cmd_collections,
        "create-collection": cmd_create_collection,
        "stats": cmd_stats,
        "documents": cmd_documents,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
