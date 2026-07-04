"""
ITaskQueue — Contrato para fila de tarefas.
"""

from abc import ABC, abstractmethod
from typing import Any, Callable


class ITaskQueue(ABC):
    """Interface para fila de tarefas assíncronas."""

    @abstractmethod
    def start(self) -> None:
        """Inicia o processamento da fila."""
        ...

    @abstractmethod
    def stop(self) -> None:
        """Para o processamento da fila."""
        ...

    @abstractmethod
    def enqueue(self, task: Any) -> str:
        """Adiciona uma tarefa à fila.

        Returns:
            ID único da tarefa.
        """
        ...

    @abstractmethod
    def get_task(self, task_id: str) -> Any | None:
        """Recupera o estado de uma tarefa."""
        ...

    @abstractmethod
    def cancel(self, task_id: str) -> bool:
        """Cancela uma tarefa pendente."""
        ...
