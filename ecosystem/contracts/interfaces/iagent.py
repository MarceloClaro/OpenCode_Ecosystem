"""
IAgent — Contrato unificado para agentes do ecossistema.

Todos os 130 agentes devem implementar este contrato.
"""

from abc import ABC, abstractmethod
from typing import Any


class IAgent(ABC):
    """Interface base para todos os agentes do ecossistema."""

    @abstractmethod
    def initialize(self, config: dict[str, Any]) -> None:
        """Inicializa o agente com configuração.

        Args:
            config: Dicionário de configuração específico do agente
        """
        ...

    @abstractmethod
    def execute(self, context: dict[str, Any]) -> dict[str, Any]:
        """Executa a tarefa principal do agente.

        Args:
            context: Contexto de execução (entrada)

        Returns:
            Resultado da execução
        """
        ...

    @abstractmethod
    def health_check(self) -> dict[str, Any]:
        """Verifica a saúde do agente.

        Returns:
            Dict com status, métricas e timestamp
        """
        ...
