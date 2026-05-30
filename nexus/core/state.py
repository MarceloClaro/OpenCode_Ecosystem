# -*- coding: utf-8 -*-
"""core.state - Gerenciamento de estado persistente via JSON."""

import json
import threading
from pathlib import Path
from typing import Any, Optional


class StateManager:
    """StateManager simples baseado em arquivos JSON com lock de thread."""

    def __init__(self, state_dir: Path):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, Any] = {}
        self._lock = threading.Lock()

    def _path(self, key: str) -> Path:
        safe = key.replace(":", "_").replace("/", "_").replace("\\", "_")
        return self.state_dir / f"{safe}.json"

    def get(self, key: str, default: Any = None) -> Any:
        with self._lock:
            if key in self._cache:
                return self._cache[key]
            p = self._path(key)
            if p.exists():
                try:
                    data = json.loads(p.read_text(encoding="utf-8"))
                    self._cache[key] = data
                    return data
                except (json.JSONDecodeError, OSError):
                    pass
            return default

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            self._cache[key] = value
            p = self._path(key)
            try:
                p.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
            except OSError:
                pass

    def delete(self, key: str) -> bool:
        with self._lock:
            self._cache.pop(key, None)
            p = self._path(key)
            if p.exists():
                p.unlink()
                return True
            return False

    def keys(self) -> list[str]:
        with self._lock:
            cached = set(self._cache.keys())
            disk = {f.stem.replace("_", ":") for f in self.state_dir.glob("*.json")}
            return list(cached | disk)

    def clear(self):
        with self._lock:
            self._cache.clear()
            for f in self.state_dir.glob("*.json"):
                f.unlink()
