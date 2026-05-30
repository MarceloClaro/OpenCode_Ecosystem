# -*- coding: utf-8 -*-
"""
COLLECTIONS v1.0 — Índice Hierárquico por Coleção (SQLite FTS5)

Organiza PDFs em coleções temáticas com busca full-text isolada.
Cada coleção é uma tabela FTS5 separada → zero contaminação entre coleções.

Schema:
  collections     — registro de coleções (nome, descrição, stats)
  documents       — metadados de cada PDF (título, autor, coleção, páginas)
  chunks          — pedaços de texto com FTS5 por coleção
  chunks_fts_{id} — tabela FTS5 por coleção (busca isolada)

Uso:
  from pdf_rag.collections import CollectionManager
  mgr = CollectionManager("caminho/para/banco.db")
  mgr.create_collection("tributario", "Direito Tributário")
  mgr.add_document("tributario", "CTN Comentado", "/path/to/ctn.pdf", chunks)
  results = mgr.search("tributario", "prescrição intercorrente", limit=10)
"""

import sqlite3
import json
import hashlib
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Collection:
    name: str
    description: str
    doc_count: int = 0
    chunk_count: int = 0
    created_at: str = ""
    keywords: list = field(default_factory=list)


@dataclass
class Document:
    doc_id: str
    title: str
    file_path: str
    collection: str
    pages: int = 0
    size_bytes: int = 0
    chunk_count: int = 0
    hash_md5: str = ""
    ingested_at: str = ""
    metadata: dict = field(default_factory=dict)


@dataclass
class Chunk:
    chunk_id: str
    doc_id: str
    collection: str
    page: int
    position: int
    content: str
    char_count: int = 0


@dataclass
class SearchResult:
    chunk_id: str
    doc_id: str
    doc_title: str
    collection: str
    page: int
    content: str
    score: float
    highlight: str = ""


class CollectionManager:
    """Gerencia coleções de PDFs com índice FTS5 isolado por coleção."""

    def __init__(self, db_path: str = "pdf_collections.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def _init_schema(self):
        """Cria tabelas base se não existirem."""
        self._conn.executescript("""
            CREATE TABLE IF NOT EXISTS collections (
                name        TEXT PRIMARY KEY,
                description TEXT NOT NULL DEFAULT '',
                doc_count   INTEGER DEFAULT 0,
                chunk_count INTEGER DEFAULT 0,
                created_at  TEXT NOT NULL,
                keywords    TEXT DEFAULT '[]'
            );

            CREATE TABLE IF NOT EXISTS documents (
                doc_id      TEXT PRIMARY KEY,
                title       TEXT NOT NULL,
                file_path   TEXT NOT NULL,
                collection  TEXT NOT NULL REFERENCES collections(name),
                pages       INTEGER DEFAULT 0,
                size_bytes  INTEGER DEFAULT 0,
                chunk_count INTEGER DEFAULT 0,
                hash_md5    TEXT DEFAULT '',
                ingested_at TEXT NOT NULL,
                metadata    TEXT DEFAULT '{}'
            );

            CREATE INDEX IF NOT EXISTS idx_doc_collection
                ON documents(collection);

            CREATE INDEX IF NOT EXISTS idx_doc_hash
                ON documents(hash_md5);

            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id   TEXT PRIMARY KEY,
                doc_id     TEXT NOT NULL REFERENCES documents(doc_id),
                collection TEXT NOT NULL REFERENCES collections(name),
                page       INTEGER DEFAULT 0,
                position   INTEGER DEFAULT 0,
                content    TEXT NOT NULL,
                char_count INTEGER DEFAULT 0
            );

            CREATE INDEX IF NOT EXISTS idx_chunk_collection
                ON chunks(collection);

            CREATE INDEX IF NOT EXISTS idx_chunk_doc
                ON chunks(doc_id);
        """)
        self._conn.commit()

    def _fts_table(self, collection: str) -> str:
        """Nome da tabela FTS5 para uma coleção."""
        safe = collection.replace("-", "_").replace(" ", "_")
        return f"chunks_fts_{safe}"

    def _ensure_fts(self, collection: str):
        """Cria tabela FTS5 para a coleção se não existir."""
        tbl = self._fts_table(collection)
        self._conn.execute(f"""
            CREATE VIRTUAL TABLE IF NOT EXISTS {tbl}
            USING fts5(
                chunk_id UNINDEXED,
                doc_id UNINDEXED,
                page UNINDEXED,
                content,
                tokenize='unicode61 remove_diacritics 2'
            )
        """)
        self._conn.commit()

    # ── Coleções ──────────────────────────────────────────────

    def create_collection(self, name: str, description: str = "",
                          keywords: list = None) -> Collection:
        """Cria uma nova coleção."""
        now = datetime.now().isoformat()
        kw = json.dumps(keywords or [], ensure_ascii=False)
        self._conn.execute(
            "INSERT OR IGNORE INTO collections (name, description, created_at, keywords) "
            "VALUES (?, ?, ?, ?)",
            (name, description, now, kw)
        )
        self._conn.commit()
        self._ensure_fts(name)
        return Collection(name=name, description=description, created_at=now,
                          keywords=keywords or [])

    def list_collections(self) -> list[Collection]:
        """Lista todas as coleções com stats."""
        rows = self._conn.execute(
            "SELECT name, description, doc_count, chunk_count, created_at, keywords "
            "FROM collections ORDER BY name"
        ).fetchall()
        result = []
        for r in rows:
            result.append(Collection(
                name=r[0], description=r[1], doc_count=r[2],
                chunk_count=r[3], created_at=r[4],
                keywords=json.loads(r[5]) if r[5] else []
            ))
        return result

    def get_collection(self, name: str) -> Optional[Collection]:
        """Retorna uma coleção pelo nome."""
        row = self._conn.execute(
            "SELECT name, description, doc_count, chunk_count, created_at, keywords "
            "FROM collections WHERE name = ?", (name,)
        ).fetchone()
        if not row:
            return None
        return Collection(
            name=row[0], description=row[1], doc_count=row[2],
            chunk_count=row[3], created_at=row[4],
            keywords=json.loads(row[5]) if row[5] else []
        )

    def delete_collection(self, name: str) -> bool:
        """Remove coleção e todos seus documentos/chunks."""
        tbl = self._fts_table(name)
        try:
            self._conn.execute(f"DROP TABLE IF EXISTS {tbl}")
            self._conn.execute("DELETE FROM chunks WHERE collection = ?", (name,))
            self._conn.execute("DELETE FROM documents WHERE collection = ?", (name,))
            self._conn.execute("DELETE FROM collections WHERE name = ?", (name,))
            self._conn.commit()
            return True
        except Exception:
            self._conn.rollback()
            return False

    # ── Documentos ────────────────────────────────────────────

    def add_document(self, collection: str, title: str, file_path: str,
                     chunks: list[str], pages: int = 0, size_bytes: int = 0,
                     metadata: dict = None) -> Document:
        """Adiciona documento com chunks à coleção."""
        file_p = Path(file_path)
        hash_md5 = ""
        if file_p.exists():
            hash_md5 = hashlib.md5(file_p.read_bytes()).hexdigest()

        # Verifica duplicata
        existing = self._conn.execute(
            "SELECT doc_id FROM documents WHERE hash_md5 = ? AND collection = ?",
            (hash_md5, collection)
        ).fetchone()
        if existing and hash_md5:
            return self.get_document(existing[0])

        doc_id = hashlib.sha256(
            f"{collection}:{file_path}:{datetime.now().isoformat()}".encode()
        ).hexdigest()[:16]
        now = datetime.now().isoformat()
        meta_json = json.dumps(metadata or {}, ensure_ascii=False)

        self._conn.execute(
            "INSERT INTO documents (doc_id, title, file_path, collection, pages, "
            "size_bytes, chunk_count, hash_md5, ingested_at, metadata) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (doc_id, title, str(file_path), collection, pages, size_bytes,
             len(chunks), hash_md5, now, meta_json)
        )

        # Inserir chunks
        self._ensure_fts(collection)
        tbl = self._fts_table(collection)
        for i, content in enumerate(chunks):
            chunk_id = f"{doc_id}_c{i:04d}"
            page_num = i + 1  # estimativa simplificada
            self._conn.execute(
                "INSERT INTO chunks (chunk_id, doc_id, collection, page, position, "
                "content, char_count) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (chunk_id, doc_id, collection, page_num, i, content, len(content))
            )
            self._conn.execute(
                f"INSERT INTO {tbl} (chunk_id, doc_id, page, content) "
                f"VALUES (?, ?, ?, ?)",
                (chunk_id, doc_id, page_num, content)
            )

        # Atualizar stats da coleção
        self._conn.execute(
            "UPDATE collections SET doc_count = doc_count + 1, "
            "chunk_count = chunk_count + ? WHERE name = ?",
            (len(chunks), collection)
        )
        self._conn.commit()

        return Document(doc_id=doc_id, title=title, file_path=str(file_path),
                        collection=collection, pages=pages, size_bytes=size_bytes,
                        chunk_count=len(chunks), hash_md5=hash_md5, ingested_at=now,
                        metadata=metadata or {})

    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retorna documento pelo ID."""
        row = self._conn.execute(
            "SELECT doc_id, title, file_path, collection, pages, size_bytes, "
            "chunk_count, hash_md5, ingested_at, metadata FROM documents WHERE doc_id = ?",
            (doc_id,)
        ).fetchone()
        if not row:
            return None
        return Document(
            doc_id=row[0], title=row[1], file_path=row[2], collection=row[3],
            pages=row[4], size_bytes=row[5], chunk_count=row[6], hash_md5=row[7],
            ingested_at=row[8], metadata=json.loads(row[9]) if row[9] else {}
        )

    def list_documents(self, collection: str = None) -> list[Document]:
        """Lista documentos, opcionalmente filtrados por coleção."""
        if collection:
            rows = self._conn.execute(
                "SELECT doc_id, title, file_path, collection, pages, size_bytes, "
                "chunk_count, hash_md5, ingested_at, metadata "
                "FROM documents WHERE collection = ? ORDER BY title",
                (collection,)
            ).fetchall()
        else:
            rows = self._conn.execute(
                "SELECT doc_id, title, file_path, collection, pages, size_bytes, "
                "chunk_count, hash_md5, ingested_at, metadata "
                "FROM documents ORDER BY collection, title"
            ).fetchall()
        return [Document(
            doc_id=r[0], title=r[1], file_path=r[2], collection=r[3],
            pages=r[4], size_bytes=r[5], chunk_count=r[6], hash_md5=r[7],
            ingested_at=r[8], metadata=json.loads(r[9]) if r[9] else {}
        ) for r in rows]

    def document_exists(self, file_path: str, collection: str) -> bool:
        """Verifica se PDF já foi ingerido (por hash MD5)."""
        fp = Path(file_path)
        if not fp.exists():
            return False
        h = hashlib.md5(fp.read_bytes()).hexdigest()
        row = self._conn.execute(
            "SELECT 1 FROM documents WHERE hash_md5 = ? AND collection = ?",
            (h, collection)
        ).fetchone()
        return row is not None

    # ── Busca ─────────────────────────────────────────────────

    def search(self, collection: str, query: str,
               limit: int = 10) -> list[SearchResult]:
        """Busca full-text em uma coleção específica (FTS5 isolado)."""
        tbl = self._fts_table(collection)
        try:
            rows = self._conn.execute(f"""
                SELECT f.chunk_id, f.doc_id, f.page, f.content,
                       rank, snippet({tbl}, 3, '<b>', '</b>', '...', 32),
                       d.title
                FROM {tbl} f
                JOIN documents d ON d.doc_id = f.doc_id
                WHERE {tbl} MATCH ?
                ORDER BY rank
                LIMIT ?
            """, (query, limit)).fetchall()
        except Exception:
            return []

        return [SearchResult(
            chunk_id=r[0], doc_id=r[1], collection=collection,
            page=r[2], content=r[3], score=abs(r[4]),
            highlight=r[5], doc_title=r[6]
        ) for r in rows]

    def search_all(self, query: str, limit_per_collection: int = 5) -> dict[str, list[SearchResult]]:
        """Busca em TODAS as coleções (para comparação/debug)."""
        results = {}
        for col in self.list_collections():
            hits = self.search(col.name, query, limit=limit_per_collection)
            if hits:
                results[col.name] = hits
        return results

    # ── Stats ─────────────────────────────────────────────────

    def stats(self) -> dict:
        """Retorna estatísticas globais do banco."""
        cols = self.list_collections()
        total_docs = sum(c.doc_count for c in cols)
        total_chunks = sum(c.chunk_count for c in cols)
        db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
        return {
            "collections": len(cols),
            "total_documents": total_docs,
            "total_chunks": total_chunks,
            "db_size_mb": round(db_size / 1048576, 2),
            "db_path": str(self.db_path),
            "collections_detail": [asdict(c) for c in cols],
        }

    def close(self):
        """Fecha conexão com o banco."""
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
