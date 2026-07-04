"""
IStateManager — Contrato para gerenciamento de estado.

Refatorado de core/interfaces.py para o contract registry central.
"""

from abc import ABC, abstractmethod
from typing import Any


class IStateManager(ABC):
    """Interface para gerenciamento de estado persistente."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Recupera um valor do estado."""
        ...

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Armazena um valor no estado."""
        ...

    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove um valor do estado.

        Returns:
            True se o valor existia, False caso contrário.
        """
        ...

    @abstractmethod
    def keys(self) -> list[str]:
        """Lista todas as chaves armazenadas."""
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Verifica se uma chave existe."""
        ...

    @abstractmethod
    def close(self) -> None:
        """Fecha a conexão com o backend de estado."""
        ...
