"""Camada 3: Armazenamento.

Estratégia híbrida:
- Markdown na pasta data/wiki/ é a source of truth (legível, versionável, exportável).
- SQLite em data/wiki.db indexa metadados e embeddings para busca rápida.

Ao iniciar a app, o índice é reconciliado com o filesystem (escaneamento). Edições
no filesystem fora da app são detectadas no próximo scan.
"""
from __future__ import annotations
import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
import frontmatter
import numpy as np

from src.config import DB_PATH, WIKI_DIR, RAW_DIR, ensure_dirs


SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS pages (
    path TEXT PRIMARY KEY,           -- caminho relativo a data/wiki/, ex: "topicos/react.md"
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    frontmatter_json TEXT,
    word_count INTEGER,
    embedding BLOB,                  -- numpy array serializado
    updated_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pages_category ON pages(category);
CREATE INDEX IF NOT EXISTS idx_pages_updated ON pages(updated_at);

CREATE TABLE IF NOT EXISTS sources (
    id TEXT PRIMARY KEY,             -- hash do conteúdo
    filename TEXT NOT NULL,
    raw_path TEXT NOT NULL,          -- caminho em data/raw/
    content_text TEXT,               -- texto extraído (para PDFs)
    file_format TEXT,                -- pdf, txt, md
    ingested_at TEXT,                -- NULL = não ingerida ainda
    summary_page TEXT,               -- caminho da página em wiki/fontes/ se ingerida
    notes TEXT
);

CREATE TABLE IF NOT EXISTS log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    operation TEXT NOT NULL,         -- ingest | query | lint | edit | delete
    summary TEXT,
    details_json TEXT
);

CREATE INDEX IF NOT EXISTS idx_log_timestamp ON log(timestamp);

CREATE TABLE IF NOT EXISTS wikilinks (
    from_page TEXT NOT NULL,
    to_page TEXT NOT NULL,           -- pode ser página inexistente (link quebrado)
    PRIMARY KEY (from_page, to_page),
    FOREIGN KEY (from_page) REFERENCES pages(path) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_wikilinks_to ON wikilinks(to_page);
"""


def get_conn() -> sqlite3.Connection:
    """Conexão única, com schema inicializado."""
    ensure_dirs()
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA_SQL)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def hash_content(content: bytes) -> str:
    """SHA256 truncado para identificar fontes."""
    return hashlib.sha256(content).hexdigest()[:16]


def _normalize_path(rel_path: str) -> str:
    """Garante separator POSIX (/) independente de SO. Crítico para Windows."""
    return rel_path.replace("\\", "/")


# ---------- Sources ----------

def save_source(filename: str, content_bytes: bytes, content_text: str, file_format: str) -> str:
    """Persiste uma fonte. Retorna source_id (hash).

    Idempotente: se a fonte já existe (mesmo hash), retorna o ID sem reescrever
    nem disco nem DB.
    """
    source_id = hash_content(content_bytes)

    with get_conn() as conn:
        existing = conn.execute("SELECT id FROM sources WHERE id = ?", (source_id,)).fetchone()
        if existing:
            return source_id  # já existe — não reescreve

        # Só escreve no disco se for fonte nova
        raw_path = RAW_DIR / f"{source_id}_{filename}"
        raw_path.write_bytes(content_bytes)

        conn.execute(
            """INSERT INTO sources (id, filename, raw_path, content_text, file_format)
               VALUES (?, ?, ?, ?, ?)""",
            (source_id, filename, str(raw_path), content_text, file_format)
        )
    return source_id


def delete_source(source_id: str) -> bool:
    """Remove uma fonte e o arquivo bruto correspondente."""
    with get_conn() as conn:
        row = conn.execute("SELECT raw_path FROM sources WHERE id = ?", (source_id,)).fetchone()
        if not row:
            return False
        raw_path = Path(row["raw_path"])
        if raw_path.exists():
            raw_path.unlink()
        conn.execute("DELETE FROM sources WHERE id = ?", (source_id,))
    return True


def list_sources(only_pending: bool = False) -> list[dict]:
    """Lista fontes; se only_pending, apenas as não ingeridas."""
    with get_conn() as conn:
        query = "SELECT * FROM sources"
        if only_pending:
            query += " WHERE ingested_at IS NULL"
        query += " ORDER BY rowid DESC"
        return [dict(r) for r in conn.execute(query).fetchall()]


def get_source(source_id: str) -> Optional[dict]:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM sources WHERE id = ?", (source_id,)).fetchone()
        return dict(row) if row else None


def mark_source_ingested(source_id: str, summary_page: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE sources SET ingested_at = ?, summary_page = ? WHERE id = ?",
            (datetime.now().isoformat(timespec="seconds"), summary_page, source_id)
        )


# ---------- Pages ----------

def save_page(rel_path: str, content: str, embedding: Optional[np.ndarray] = None) -> None:
    """Persiste uma página de wiki: escreve no disco E indexa no SQLite.

    rel_path: caminho relativo a data/wiki/, ex: "topicos/react.md"
    """
    rel_path = _normalize_path(rel_path)
    full_path = WIKI_DIR / rel_path
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")

    # Parse frontmatter e título
    post = frontmatter.loads(content)
    fm = dict(post.metadata)
    body = post.content
    title = _extract_title(body) or Path(rel_path).stem.replace("-", " ").title()

    category = rel_path.split("/")[0] if "/" in rel_path else "outros"
    word_count = len(body.split())
    embedding_blob = embedding.tobytes() if embedding is not None else None

    with get_conn() as conn:
        conn.execute(
            """INSERT INTO pages (path, category, title, content, frontmatter_json,
                                  word_count, embedding, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)
               ON CONFLICT(path) DO UPDATE SET
                  category = excluded.category,
                  title = excluded.title,
                  content = excluded.content,
                  frontmatter_json = excluded.frontmatter_json,
                  word_count = excluded.word_count,
                  embedding = COALESCE(excluded.embedding, pages.embedding),
                  updated_at = excluded.updated_at""",
            (rel_path, category, title, content, json.dumps(fm, default=str),
             word_count, embedding_blob, datetime.now().isoformat(timespec="seconds"))
        )

        # Atualiza wikilinks
        conn.execute("DELETE FROM wikilinks WHERE from_page = ?", (rel_path,))
        for link in _extract_wikilinks(body):
            conn.execute(
                "INSERT OR IGNORE INTO wikilinks (from_page, to_page) VALUES (?, ?)",
                (rel_path, link)
            )


def get_page(rel_path: str) -> Optional[dict]:
    rel_path = _normalize_path(rel_path)
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM pages WHERE path = ?", (rel_path,)).fetchone()
        return dict(row) if row else None


def list_pages(category: Optional[str] = None) -> list[dict]:
    with get_conn() as conn:
        if category:
            rows = conn.execute(
                "SELECT path, category, title, word_count, updated_at FROM pages WHERE category = ? ORDER BY title",
                (category,)
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT path, category, title, word_count, updated_at FROM pages ORDER BY category, title"
            ).fetchall()
        return [dict(r) for r in rows]


def delete_page(rel_path: str) -> bool:
    rel_path = _normalize_path(rel_path)
    full_path = WIKI_DIR / rel_path
    existed = full_path.exists()
    if existed:
        full_path.unlink()
    with get_conn() as conn:
        conn.execute("DELETE FROM pages WHERE path = ?", (rel_path,))
    return existed


def search_pages_text(query: str, limit: int = 10) -> list[dict]:
    """Busca textual simples (LIKE) — OK para MVP, substituir por FTS5 depois."""
    pattern = f"%{query.lower()}%"
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT path, category, title, word_count, updated_at
               FROM pages
               WHERE LOWER(content) LIKE ? OR LOWER(title) LIKE ?
               ORDER BY updated_at DESC
               LIMIT ?""",
            (pattern, pattern, limit)
        ).fetchall()
        return [dict(r) for r in rows]


def get_page_embeddings() -> list[tuple[str, str, np.ndarray]]:
    """Retorna (path, title, embedding) para todas as páginas que têm embedding."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT path, title, embedding FROM pages WHERE embedding IS NOT NULL"
        ).fetchall()
        results = []
        for r in rows:
            arr = np.frombuffer(r["embedding"], dtype=np.float32)
            results.append((r["path"], r["title"], arr))
        return results


# ---------- Log ----------

def log_event(operation: str, summary: str, details: Optional[dict] = None) -> None:
    with get_conn() as conn:
        conn.execute(
            """INSERT INTO log (timestamp, operation, summary, details_json)
               VALUES (?, ?, ?, ?)""",
            (datetime.now().isoformat(timespec="seconds"),
             operation, summary, json.dumps(details, default=str) if details else None)
        )


def recent_log(limit: int = 50) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM log ORDER BY timestamp DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]


# ---------- Wikilinks ----------

def list_orphan_pages() -> list[str]:
    """Páginas que ninguém aponta (não têm inbound link)."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT p.path FROM pages p
            LEFT JOIN wikilinks w ON p.path = w.to_page
            WHERE w.to_page IS NULL
            ORDER BY p.path
        """).fetchall()
        return [r["path"] for r in rows]


def list_broken_links() -> list[tuple[str, str]]:
    """Links que apontam para páginas inexistentes."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT w.from_page, w.to_page FROM wikilinks w
            LEFT JOIN pages p ON w.to_page = p.path
            WHERE p.path IS NULL
        """).fetchall()
        return [(r["from_page"], r["to_page"]) for r in rows]


def get_graph_data() -> dict:
    """Retorna nós e arestas para o graph view."""
    with get_conn() as conn:
        nodes = [
            {"id": r["path"], "label": r["title"], "category": r["category"]}
            for r in conn.execute("SELECT path, title, category FROM pages").fetchall()
        ]
        edges = [
            {"from": r["from_page"], "to": r["to_page"]}
            for r in conn.execute(
                "SELECT w.from_page, w.to_page FROM wikilinks w "
                "INNER JOIN pages p ON w.to_page = p.path"
            ).fetchall()
        ]
    return {"nodes": nodes, "edges": edges}


# ---------- Helpers internos ----------

def _extract_title(body: str) -> Optional[str]:
    """Pega o primeiro `# H1` do corpo."""
    for line in body.splitlines():
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return None


def _extract_wikilinks(body: str) -> list[str]:
    """Extrai todos os [[wikilinks]] do corpo. Retorna paths normalizados (POSIX, .md)."""
    import re
    links = []
    for match in re.finditer(r"\[\[([^\]]+)\]\]", body):
        link = match.group(1).split("|")[0].strip()  # ignora alias depois de |
        link = link.replace("\\", "/")  # normaliza separator
        # Normaliza: garante .md no final
        if not link.endswith(".md"):
            link += ".md"
        links.append(link)
    return links


def reconcile_filesystem() -> dict:
    """Reescaneia data/wiki/ e atualiza o índice **sem disparar saves redundantes**.

    Diferenças críticas em relação a save_page:
    - Normaliza path para POSIX (crítico em Windows).
    - Só insere se a página não existe E o arquivo .md tem conteúdo válido.
    - Não recalcula embeddings (o save_page faria — caro e desnecessário aqui).
    - Não chama log_event (reconciliação não é uma operação do usuário).
    - Mantém updated_at do arquivo no disco (mtime), não datetime.now().
    """
    found = 0
    added = 0
    skipped = 0

    with get_conn() as conn:
        for md_file in WIKI_DIR.rglob("*.md"):
            found += 1
            # Normaliza path para POSIX (resolve bug Windows)
            rel_path = _normalize_path(str(md_file.relative_to(WIKI_DIR)))

            existing = conn.execute(
                "SELECT path FROM pages WHERE path = ?", (rel_path,)
            ).fetchone()

            if existing:
                skipped += 1
                continue

            # Página existe no disco mas não no índice — indexa de forma leve
            try:
                content = md_file.read_text(encoding="utf-8")
            except Exception:
                continue

            post = frontmatter.loads(content)
            body = post.content
            title = _extract_title(body) or md_file.stem.replace("-", " ").title()
            category = rel_path.split("/")[0] if "/" in rel_path else "outros"
            word_count = len(body.split())
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime).isoformat(timespec="seconds")

            conn.execute(
                """INSERT INTO pages (path, category, title, content, frontmatter_json,
                                      word_count, embedding, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, NULL, ?)""",
                (rel_path, category, title, content,
                 json.dumps(dict(post.metadata), default=str),
                 word_count, mtime)
            )
            # Indexa wikilinks também
            for link in _extract_wikilinks(body):
                conn.execute(
                    "INSERT OR IGNORE INTO wikilinks (from_page, to_page) VALUES (?, ?)",
                    (rel_path, _normalize_path(link))
                )
            added += 1

    return {"found": found, "added_to_index": added, "already_indexed": skipped}


def cleanup_corrupted_paths() -> dict:
    """Remove páginas com paths que contêm '\\' (legado de versão buggada no Windows).

    Estratégia:
    - Para cada página com '\\' no path, verifica se existe equivalente com '/'.
    - Se a versão com '/' existe, apaga a versão com '\\' (é a corrompida).
    - Se só existe a versão com '\\', renomeia para '/' (preserva o conteúdo).
    - Limpa wikilinks que apontam para paths corrompidos.
    """
    removed = 0
    renamed = 0
    fixed_links = 0

    with get_conn() as conn:
        # Páginas com '\' no path
        bad_paths = [r["path"] for r in conn.execute(
            "SELECT path FROM pages WHERE path LIKE '%\\%' ESCAPE '!'"
        ).fetchall()]
        # SQLite usa '\' como literal por padrão, vamos buscar de outro jeito
        if not bad_paths:
            all_paths = [r["path"] for r in conn.execute("SELECT path FROM pages").fetchall()]
            bad_paths = [p for p in all_paths if "\\" in p]

        for bad_path in bad_paths:
            good_path = bad_path.replace("\\", "/")
            existing_good = conn.execute(
                "SELECT path FROM pages WHERE path = ?", (good_path,)
            ).fetchone()

            if existing_good:
                # Versão correta já existe — apenas remove a corrompida
                conn.execute("DELETE FROM pages WHERE path = ?", (bad_path,))
                conn.execute("DELETE FROM wikilinks WHERE from_page = ?", (bad_path,))
                removed += 1
            else:
                # Só existe a versão ruim — renomeia
                conn.execute(
                    "UPDATE pages SET path = ?, category = ? WHERE path = ?",
                    (good_path, good_path.split("/")[0] if "/" in good_path else "outros", bad_path)
                )
                conn.execute(
                    "UPDATE wikilinks SET from_page = ? WHERE from_page = ?",
                    (good_path, bad_path)
                )
                renamed += 1

        # Limpa também wikilinks com '\' no to_page
        bad_targets = [r["to_page"] for r in conn.execute("SELECT DISTINCT to_page FROM wikilinks").fetchall() if "\\" in r["to_page"]]
        for bad_target in bad_targets:
            good_target = bad_target.replace("\\", "/")
            conn.execute("UPDATE wikilinks SET to_page = ? WHERE to_page = ?", (good_target, bad_target))
            fixed_links += 1

    return {"removed_duplicates": removed, "renamed": renamed, "fixed_wikilinks": fixed_links}
