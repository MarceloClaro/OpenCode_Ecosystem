"""
ICache — Contrato para cache com TTL.
"""

from abc import ABC, abstractmethod
from typing import Any


class ICache(ABC):
    """Interface para cache com time-to-live."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Recupera valor do cache."""
        ...

    @abstractmethod
    def set(self, key: str, value: Any, ttl: int | None = None) -> None:
        """Armazena valor no cache com TTL opcional."""
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove valor do cache."""
        ...

    @abstractmethod
    def has(self, key: str) -> bool:
        """Verifica se chave existe e não expirou."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Limpa todo o cache."""
        ...

    @abstractmethod
    def stats(self) -> dict[str, Any]:
        """Estatísticas de uso do cache."""
        ...
