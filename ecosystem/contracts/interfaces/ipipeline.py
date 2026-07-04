"""
IPipeline — Contrato para pipelines do ecossistema.
"""

from abc import ABC, abstractmethod
from typing import Any


class IPipeline(ABC):
    """Interface base para pipelines."""

    @abstractmethod
    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """Executa o pipeline completo.

        Args:
            inputs: Parâmetros de entrada

        Returns:
            Resultados do pipeline
        """
        ...

    @abstractmethod
    def validate(self, inputs: dict[str, Any]) -> list[str]:
        """Valida os parâmetros de entrada.

        Returns:
            Lista de erros de validação (vazia se válido)
        """
        ...

    @abstractmethod
    def get_status(self) -> dict[str, Any]:
        """Retorna o status atual do pipeline.

        Returns:
            Dict com estado atual, progresso e métricas
        """
        ...
