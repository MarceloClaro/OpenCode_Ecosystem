"""
core/cache.py — Cache Layer com TTL, LRU Eviction, Estatísticas e DI.

Thread-safe. Suporta TTL por entrada, evicção LRU automática no limite
de tamanho, e coleta de estatísticas (hits/misses/hit_ratio).

Uso com DI (novo):
    container = Container.instance()
    cache = TTLCache(container=container, maxsize=500, default_ttl=600)
    cache.set("user:42", {"name": "Alice"})
    print(cache.get("user:42"))

Uso legado (compatível):
    cache = TTLCache(maxsize=500, default_ttl=600)
    cache.set("chave", {"data": 42})
"""

from __future__ import annotations

import logging
import threading
import time
from collections import OrderedDict
from typing import Any, Optional
from core.interfaces import ICache

logger = logging.getLogger(__name__)


class CacheEntry:
    """Entrada individual do cache com valor e TTL.

    Attributes:
        value: Dado armazenado.
        expires_at: Timestamp monotônico de expiração (None = eterno).
    """

    __slots__ = ("value", "expires_at")

    def __init__(self, value: Any, ttl: Optional[float] = None) -> None:
        self.value = value
        self.expires_at = (time.monotonic() + ttl) if ttl is not None else None

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.monotonic() > self.expires_at


class TTLCache(ICache):
    """Cache thread-safe com TTL e evicção LRU, com suporte a DI.

    Args:
        maxsize: Número máximo de entradas (0 = ilimitado).
        default_ttl: TTL padrão em segundos (None = sem expiração).
        container: Container DI opcional.

    Example:
        cache = TTLCache(maxsize=1000, default_ttl=300)
        cache.set("user:42", {"name": "Alice"})
        assert cache.get("user:42") == {"name": "Alice"}
        assert cache.hit_ratio > 0.5
    """

    def __init__(
        self,
        maxsize: int = 1000,
        default_ttl: Optional[float] = 300.0,
        container: Any = None,
    ) -> None:
        if maxsize < 0:
            raise ValueError("maxsize must be >= 0")
        self._maxsize = maxsize
        self._default_ttl = default_ttl
        self._data: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.Lock()
        self._hits = 0
        self._misses = 0
        self._container = container

        if container is not None and not container.is_registered('cache'):
            container.register('cache', self)

    # --- API Pública ---

    def get(self, key: str, default: Any = None) -> Any:
        """Retorna valor do cache ou *default* se ausente/expirado."""
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                self._misses += 1
                return default
            if entry.is_expired:
                del self._data[key]
                self._misses += 1
                return default
            self._data.move_to_end(key)
            self._hits += 1
            return entry.value

    def set(self, key: str, value: Any, ttl: Optional[float] = None) -> None:
        """Armazena valor no cache com TTL opcional."""
        with self._lock:
            self._data[key] = CacheEntry(value, ttl if ttl is not None else self._default_ttl)
            self._data.move_to_end(key)
            self._evict()

    def delete(self, key: str) -> bool:
        """Remove entrada do cache. Retorna True se a chave existia."""
        with self._lock:
            return self._data.pop(key, None) is not None

    def clear(self) -> None:
        """Esvazia todo o cache e zera estatísticas."""
        with self._lock:
            self._data.clear()
            self._hits = 0
            self._misses = 0

    def has(self, key: str) -> bool:
        """Verifica se a chave existe e não expirou."""
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return False
            if entry.is_expired:
                del self._data[key]
                return False
            return True

    # --- Propriedades ---

    @property
    def size(self) -> int:
        """Número atual de entradas válidas."""
        with self._lock:
            self._purge_expired()
            return len(self._data)

    @property
    def hits(self) -> int:
        with self._lock:
            return self._hits

    @property
    def misses(self) -> int:
        with self._lock:
            return self._misses

    @property
    def hit_ratio(self) -> float:
        with self._lock:
            total = self._hits + self._misses
            if total == 0:
                return 0.0
            return self._hits / total

    @property
    def keys(self) -> list[str]:
        with self._lock:
            self._purge_expired()
            return list(self._data.keys())

    @property
    def maxsize(self) -> int:
        return self._maxsize

    @property
    def default_ttl(self) -> Optional[float]:
        return self._default_ttl

    @property
    def is_empty(self) -> bool:
        return self.size == 0

    # --- Métodos Internos ---

    def _evict(self) -> None:
        if self._maxsize == 0:
            return
        while len(self._data) > self._maxsize:
            key, _ = self._data.popitem(last=False)
            logger.debug("Evicted LRU key: %s", key)

    def _purge_expired(self) -> None:
        now = time.monotonic()
        expired = [
            k for k, v in self._data.items()
            if v.expires_at is not None and now > v.expires_at
        ]
        for k in expired:
            del self._data[k]

    def stats(self) -> dict[str, Any]:
        with self._lock:
            self._purge_expired()
            total = self._hits + self._misses
            hit_ratio_val = round(self._hits / total, 4) if total > 0 else 0.0
            return {
                "size": len(self._data),
                "maxsize": self._maxsize,
                "default_ttl": self._default_ttl,
                "hits": self._hits,
                "misses": self._misses,
                "hit_ratio": hit_ratio_val,
                "keys_sample": list(self._data.keys())[:10],
            }

    def __repr__(self) -> str:
        return (
            f"TTLCache(size={self.size}/{self._maxsize}, "
            f"hit_ratio={self.hit_ratio:.2%})"
        )

    def __len__(self) -> int:
        return self.size

    def __contains__(self, key: str) -> bool:
        return self.has(key)
