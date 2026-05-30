"""
core/state.py (refatorado - proposto) - SQLite State Manager com DI.
Implementa IStateManager. Remove padrao singleton.
"""

from __future__ import annotations
import json
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Optional
from core.interfaces import IStateManager


class SQLiteStateManager(IStateManager):
    def __init__(self, db_path: str | Path) -> None:
        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._local = threading.local()
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn: Optional[sqlite3.Connection] = getattr(self._local, 'conn', None)
        if conn is None:
            conn = sqlite3.connect(str(self._db_path), timeout=10)
            conn.execute('PRAGMA journal_mode=WAL')
            conn.execute('PRAGMA synchronous=NORMAL')
            conn.execute('PRAGMA busy_timeout=5000')
            conn.row_factory = sqlite3.Row
            self._local.conn = conn
        return conn

    def _init_db(self) -> None:
        conn = self._get_conn()
        conn.executescript('''
            CREATE TABLE IF NOT EXISTS state (
                key TEXT PRIMARY KEY,
                value BLOB NOT NULL,
                updated_at TEXT NOT NULL DEFAULT (datetime('now'))
            );
            PRAGMA auto_vacuum=INCREMENTAL;
        ''')
        conn.commit()

    def get(self, key: str, default: Any = None) -> Any:
        conn = self._get_conn()
        row = conn.execute('SELECT value FROM state WHERE key = ?', (key,)).fetchone()
        return json.loads(row['value']) if row else default

    def set(self, key: str, data: Any) -> None:
        conn = self._get_conn()
        blob = json.dumps(data, ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        conn.execute(
            'INSERT OR REPLACE INTO state (key, value, updated_at) VALUES (?, ?, datetime(\'now\'))',
            (key, blob),
        )
        conn.commit()

    def delete(self, key: str) -> bool:
        conn = self._get_conn()
        cursor = conn.execute('DELETE FROM state WHERE key = ?', (key,))
        conn.commit()
        return cursor.rowcount > 0

    def keys(self) -> list[str]:
        conn = self._get_conn()
        return [row['key'] for row in conn.execute('SELECT key FROM state ORDER BY key')]

    def exists(self, key: str) -> bool:
        conn = self._get_conn()
        row = conn.execute('SELECT 1 FROM state WHERE key = ?', (key,)).fetchone()
        return row is not None

    def close(self) -> None:
        conn: Optional[sqlite3.Connection] = getattr(self._local, 'conn', None)
        if conn is not None:
            try:
                conn.close()
            except sqlite3.Error:
                pass
            self._local.conn = None

    def get_updated_at(self, key: str) -> Optional[str]:
        conn = self._get_conn()
        row = conn.execute('SELECT updated_at FROM state WHERE key = ?', (key,)).fetchone()
        return row['updated_at'] if row else None

    @contextmanager
    def transaction(self, key: str):
        data = self.get(key, default={})
        yield data
        self.set(key, data)

    def vacuum(self) -> None:
        conn = self._get_conn()
        conn.execute('PRAGMA incremental_vacuum')

    def import_json(self, path: Path, key: Optional[str] = None) -> bool:
        import gzip
        if not path.exists():
            gz_path = path.with_suffix('.json.gz')
            if gz_path.exists():
                path = gz_path
            else:
                return False
        key = key or path.stem.replace('.json', '')
        try:
            if path.suffix == '.gz':
                with gzip.open(path, 'rt', encoding='utf-8') as f:
                    data = json.load(f)
            else:
                data = json.loads(path.read_text(encoding='utf-8'))
            self.set(key, data)
            return True
        except (json.JSONDecodeError, OSError):
            return False

    def export_json(self, key: str, path: Optional[Path] = None) -> bool:
        from core.config import settings
        data = self.get(key)
        if data is None and data != {}:
            return False
        path = path or settings.EVOLVE_DIR / f'{key}.json'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
        return True
