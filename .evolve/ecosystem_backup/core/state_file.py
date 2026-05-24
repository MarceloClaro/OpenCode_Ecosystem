"""
core/state_file.py — Persistência de Estado em Arquivos JSON.

Implementa ``IStateManager`` com armazenamento em arquivos JSON
individuais (uma chave = um arquivo ``.json``). Thread-safe com
escrita atômica via *tempfile + replace*.

Ideal para estados semi-estruturados, configs de usuário, e dados
que precisam ser inspecionados/editados manualmente.

Uso:
    sm = FileStateManager(Path(".reversa/context"))
    sm.set("surface", {"modules": 12, "language": "Python"})
    data = sm.get("surface")  # -> {"modules": 12, ...}
"""

from __future__ import annotations

import json
import logging
import tempfile
import threading
from pathlib import Path
from typing import Any, Optional

from core.interfaces import IStateManager
from core.errors import StateError

logger = logging.getLogger(__name__)


class FileStateManager(IStateManager):
    """State manager baseado em arquivos JSON individuais.

    Cada chave é armazenada em um arquivo ``.json`` separado dentro
    do diretório base. Escrita atômica via *tempfile + rename*
    para evitar corrupção em caso de queda.

    Args:
        base_dir: Diretório para armazenar os arquivos de estado.
    """

    def __init__(self, base_dir: str | Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        logger.info("FileStateManager initialized at %s", self._base_dir)

    # --- API Pública (IStateManager) ---

    def get(self, key: str, default: Any = None) -> Any:
        """Retorna o valor associado à chave ou *default*."""
        path = self._path_for(key)
        if not path.exists():
            return default
        try:
            data = path.read_text(encoding="utf-8")
            return json.loads(data)
        except (json.JSONDecodeError, OSError) as e:
            raise StateError(
                f"Failed to read state file {path}: {e}",
                original=e,
                details={"key": key, "path": str(path)},
            )

    def set(self, key: str, data: Any) -> None:
        """Persiste o valor associado à chave (escrita atômica)."""
        path = self._path_for(key)
        serialized = json.dumps(data, ensure_ascii=False, indent=2, default=str)
        with self._lock:
            fd, tmp_path = tempfile.mkstemp(
                suffix=".json",
                prefix=f"{key}_",
                dir=self._base_dir,
            )
            try:
                with open(fd, "w", encoding="utf-8") as f:
                    f.write(serialized)
                Path(tmp_path).replace(path)
            except OSError as e:
                try:
                    Path(tmp_path).unlink(missing_ok=True)
                except OSError:
                    pass
                raise StateError(
                    f"Failed to write state file {path}: {e}",
                    original=e,
                    details={"key": key, "path": str(path)},
                )

    def delete(self, key: str) -> bool:
        """Remove o arquivo de estado. Retorna True se existia."""
        path = self._path_for(key)
        if path.exists():
            path.unlink()
            return True
        return False

    def keys(self) -> list[str]:
        """Lista todas as chaves disponíveis."""
        return sorted(
            p.stem for p in self._base_dir.glob("*.json")
            if p.is_file() and not p.name.startswith(".")
        )

    def exists(self, key: str) -> bool:
        """Verifica se a chave possui arquivo de estado."""
        return self._path_for(key).exists()

    def close(self) -> None:
        pass

    # --- Métodos Auxiliares ---

    def _path_for(self, key: str) -> Path:
        safe = (
            key.replace("/", "_")
            .replace("\\", "_")
            .replace(":", "_")
            .replace(" ", "_")
            .replace("..", "_")
        )
        return self._base_dir / f"{safe}.json"

    def import_json(self, path: str | Path, key: Optional[str] = None) -> bool:
        """Importa um arquivo JSON externo como estado.

        Suporta arquivos ``.json`` e ``.json.gz``.
        """
        import gzip
        src = Path(path)
        target_key = key or src.stem.replace(".json", "")
        try:
            if src.suffix == ".gz":
                with gzip.open(src, "rt", encoding="utf-8") as f:
                    data = json.load(f)
            else:
                data = json.loads(src.read_text(encoding="utf-8"))
            self.set(target_key, data)
            logger.info("Imported %s -> key=%s", src.name, target_key)
            return True
        except (json.JSONDecodeError, OSError, ImportError) as e:
            logger.warning("Failed to import %s: %s", src, e)
            return False

    def export_json(self, key: str, path: Optional[str | Path] = None) -> bool:
        """Exporta uma chave de estado para arquivo JSON externo."""
        data = self.get(key)
        if data is None:
            logger.warning("No data for key=%s, cannot export", key)
            return False
        dest = Path(path) if path else self._path_for(key)
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            dest.write_text(
                json.dumps(data, ensure_ascii=False, indent=2, default=str),
                encoding="utf-8",
            )
            logger.info("Exported key=%s -> %s", key, dest)
            return True
        except OSError as e:
            logger.error("Failed to export key=%s to %s: %s", key, dest, e)
            return False

    def __repr__(self) -> str:
        return f"FileStateManager(dir={self._base_dir}, keys={len(self.keys())})"
