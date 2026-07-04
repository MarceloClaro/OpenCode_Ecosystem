"""
IEventBus — Contrato para barramento de eventos.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable


class IEventBus(ABC):
    """Interface para barramento de eventos assíncrono."""

    @abstractmethod
    def subscribe(self, topic: str, callback: Callable) -> None:
        """Inscreve um callback em um tópico."""
        ...

    @abstractmethod
    def unsubscribe(self, topic: str, callback: Callable) -> None:
        """Remove inscrição de um callback."""
        ...

    @abstractmethod
    def publish(self, topic: str, data: Any = None) -> None:
        """Publica um evento em um tópico."""
        ...

    @abstractmethod
    def subscriber_count(self, topic: str) -> int:
        """Número de inscritos em um tópico."""
        ...

    @abstractmethod
    def topics(self) -> list[str]:
        """Lista todos os tópicos com inscrições."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Remove todas as inscrições."""
        ...
