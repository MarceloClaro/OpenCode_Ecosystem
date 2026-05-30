"""BaseExtractor — classe abstrata para extratores de documentos."""

from abc import ABC, abstractmethod


class BaseExtractor(ABC):
    """Classe base abstrata para extratores de texto.

    Cada extrator implementa extract() para um formato específico
    (PDF, HTML, etc).
    """

    @abstractmethod
    def extract(self, raw: bytes | str) -> str:
        """Extrai texto do conteúdo bruto.

        Args:
            raw: Conteúdo bruto (bytes para PDF, str para HTML).

        Returns:
            Texto extraído.
        """
        ...
