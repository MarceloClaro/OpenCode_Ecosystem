"""BaseConnector — classe abstrata para conectores de portais de editais.

Todos os conectores DEVEM herdar desta classe.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal


@dataclass
class EditalRaw:
    """Dados brutos de um edital extraído do portal, antes do processamento."""

    titulo: str
    url: str
    pdf_url: str | None = None
    data_publicacao: str | None = None


class BaseConnector(ABC):
    """Classe base abstrata para todos os conectores de portal.

    Attributes:
        mode: 'http' para portais sem proteção (httpx) ou 'browser' para portais com anti-bot (Camoufox).
        base_url: URL base do portal.
        crawl_interval_hours: intervalo mínimo entre crawls (em horas).
    """

    mode: Literal["http", "browser"] = "http"
    base_url: str = ""
    crawl_interval_hours: int = 24

    @abstractmethod
    def fetch_editais(self) -> list[EditalRaw]:
        """Busca a lista de editais do portal.

        Returns:
            Lista de editais brutos encontrados.
        """
        ...

    @abstractmethod
    def parse(self, content: str) -> list[EditalRaw]:
        """Converte o conteúdo HTML/JSON do portal em objetos EditalRaw.

        Args:
            content: Conteúdo bruto retornado pelo portal (HTML ou JSON).

        Returns:
            Lista de editais parseados.
        """
        ...
