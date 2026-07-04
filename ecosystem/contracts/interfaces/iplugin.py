"""
IPlugin — Contrato para plugins do ecossistema.
"""

from abc import ABC, abstractmethod
from typing import Any


class IPlugin(ABC):
    """Interface base para todos os plugins."""

    @abstractmethod
    def on_load(self, config: dict[str, Any]) -> None:
        """Called quando o plugin é carregado."""
        ...

    @abstractmethod
    def on_unload(self) -> None:
        """Called quando o plugin é descarregado."""
        ...

    @abstractmethod
    def execute_hook(self, hook: str, context: dict[str, Any]) -> Any | None:
        """Executa um hook específico do plugin.

        Args:
            hook: Nome do hook (ex: "pre_commit", "post_evolve")
            context: Contexto do hook

        Returns:
            Resultado opcional do hook
        """
        ...
