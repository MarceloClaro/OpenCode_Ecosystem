"""
IScanner — Contrato para scanners do ecossistema.

Cobre os 5 scanners: Noológico, Teleológico, Evolutivo, Potentiality, Social Impact.
"""

from abc import ABC, abstractmethod
from typing import Any


class IScanner(ABC):
    """Interface base para todos os scanners."""

    @abstractmethod
    def scan(self, target: str | None = None) -> dict[str, Any]:
        """Executa a varredura principal.

        Args:
            target: Alvo opcional da varredura

        Returns:
            Resultados brutos da varredura
        """
        ...

    @abstractmethod
    def analyze(self, raw_data: dict[str, Any]) -> dict[str, Any]:
        """Analisa os dados da varredura.

        Args:
            raw_data: Dados brutos do scan()

        Returns:
            Análise estruturada
        """
        ...

    @abstractmethod
    def report(self, analysis: dict[str, Any]) -> str:
        """Gera relatório legível a partir da análise.

        Args:
            analysis: Dados analisados do analyze()

        Returns:
            Relatório formatado
        """
        ...
