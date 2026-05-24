"""
core/state_manager.py — Proxy Unificado de Gerenciamento de Estado.

Oferece uma interface única que combina:
- SQLiteStateManager (primário, para dados estruturados e consultas)
- FileStateManager (secundário, para dados semi-estruturados e arquivos JSON)

Mantém compatibilidade reversa com `from core import state_manager`.

Uso:
    from core.state_manager import get_state_manager

    sm = get_state_manager()
    sm.set("key", {"data": 42})
    value = sm.get("key")
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

from core.config import settings
from core.interfaces import IStateManager
from core.state import SQLiteStateManager
from core.state_file import FileStateManager

logger = logging.getLogger(__name__)


class UnifiedStateManager(IStateManager):
    """Proxy que unifica SQLite (primário) e JSON file (secundário).

    Estratégia:
    - Chaves com prefixo `file:` são roteadas para o FileStateManager.
    - Demais chaves usam SQLiteStateManager como padrão.
    - `keys()` e `exists()" consultam ambos os backends.
    """

    FILE_PREFIX = "file:"

    def __init__(
        self,
        db_path: Optional[str | Path] = None,
        file_base_dir: Optional[str | Path] = None,
    ) -> None:
        self._sqlite = SQLiteStateManager(db_path or settings.state_db_path())
        self._file = FileStateManager(
            file_base_dir or settings.EVOLVE_DIR / "file_state"
        )
        logger.info(
            "UnifiedStateManager: sqlite=%s file=%s",
            self._sqlite._db_path,
            self._file._base_dir,
        )

    # --- Roteamento ---

    def _resolve(self, key: str) -> IStateManager:
        if key.startswith(self.FILE_PREFIX):
            return self._file
        return self._sqlite

    def _strip_prefix(self, key: str) -> str:
        if key.startswith(self.FILE_PREFIX):
            return key[len(self.FILE_PREFIX):]
        return key

    # --- API IStateManager ---

    def get(self, key: str, default: Any = None) -> Any:
        return self._resolve(key).get(self._strip_prefix(key), default)

    def set(self, key: str, data: Any) -> None:
        self._resolve(key).set(self._strip_prefix(key), data)

    def delete(self, key: str) -> bool:
        return self._resolve(key).delete(self._strip_prefix(key))

    def keys(self) -> list[str]:
        sqlite_keys = [k for k in self._sqlite.keys()]
        file_keys = [f"{self.FILE_PREFIX}{k}" for k in self._file.keys()]
        return sorted(sqlite_keys + file_keys)

    def exists(self, key: str) -> bool:
        return self._resolve(key).exists(self._strip_prefix(key))

    def close(self) -> None:
        self._sqlite.close()
        # FileStateManager.close() é no-op

    # --- Acesso direto aos backends ---

    @property
    def sqlite(self) -> SQLiteStateManager:
        return self._sqlite

    @property
    def file(self) -> FileStateManager:
        return self._file

    def __repr__(self) -> str:
        return (
            f"UnifiedStateManager(sqlite_keys={len(self._sqlite.keys())}, "
            f"file_keys={len(self._file.keys())})"
        )


# ── Singleton da aplicação ─────────────────────────────────────
# Mantido para compatibilidade reversa com código legado.

_instance: Optional[UnifiedStateManager] = None


def get_state_manager(
    db_path: Optional[str | Path] = None,
    file_base_dir: Optional[str | Path] = None,
) -> UnifiedStateManager:
    """Retorna a instância singleton do UnifiedStateManager.

    Args:
        db_path: Caminho do banco SQLite (opcional, usa config se omitido).
        file_base_dir: Diretório para FileStateManager (opcional).

    Returns:
        Instância única de UnifiedStateManager.
    """
    global _instance
    if _instance is None:
        _instance = UnifiedStateManager(
            db_path=db_path,
            file_base_dir=file_base_dir,
        )
    return _instance


def reset_state_manager() -> None:
    """Reseta o singleton (uso em testes)."""
    global _instance
    if _instance is not None:
        _instance.close()
    _instance = None
