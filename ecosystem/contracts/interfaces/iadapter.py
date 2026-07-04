"""
IAdapter — Contrato para adaptadores de entrypoints existentes.
"""

from abc import ABC, abstractmethod
from typing import Any


class IAdapter(ABC):
    """Interface para adaptadores que conectam módulos legados ao entrypoint canônico."""

    @abstractmethod
    def can_handle(self, command: str) -> bool:
        """Verifica se este adaptador pode processar o comando.

        Args:
            command: Nome do comando ou script

        Returns:
            True se puder processar
        """
        ...

    @abstractmethod
    def execute(self, command: str, args: list[str] | None = None, **kwargs: Any) -> Any:
        """Executa o comando mapeado.

        Args:
            command: Nome do comando
            args: Argumentos opcionais
            **kwargs: Parâmetros adicionais

        Returns:
            Resultado da execução
        """
        ...

    @abstractmethod
    def describe(self) -> dict[str, Any]:
        """Descreve as capacidades do adaptador.

        Returns:
            Dict com nome, comandos suportados, versão
        """
        ...
