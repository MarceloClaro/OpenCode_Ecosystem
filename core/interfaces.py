"""
core/interfaces.py (proposto) - Contratos Abstratos para Injeção de Dependencia.
Define os contratos que StateManager, EventBus, Cache e TaskQueue devem implementar.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Callable


class IStateManager(ABC):
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any: ...
    @abstractmethod
    def set(self, key: str, data: Any) -> None: ...
    @abstractmethod
    def delete(self, key: str) -> bool: ...
    @abstractmethod
    def keys(self) -> list[str]: ...
    @abstractmethod
    def exists(self, key: str) -> bool: ...
    @abstractmethod
    def close(self) -> None: ...


    def transaction(self, key: str):
        ...

    def import_json(self, path, key=None) -> bool:
        ...

    def export_json(self, key, path=None) -> bool:
        ...


class IEventBus(ABC):
    @abstractmethod
    def subscribe(self, topic: str, handler: Callable) -> str: ...
    @abstractmethod
    def unsubscribe(self, topic: str, sub_id: str) -> bool: ...
    @abstractmethod
    async def publish(self, topic: str, data: Any = None, source: str = "") -> int: ...
    @abstractmethod
    def subscriber_count(self, topic: str) -> int: ...
    @abstractmethod
    def topics(self) -> list[str]: ...
    @abstractmethod
    def clear(self) -> int: ...


    @property
    def is_running(self) -> bool:
        return True


class ICache(ABC):
    @abstractmethod
    def get(self, key: str, default: Any = None) -> Any: ...
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Any = None) -> None: ...
    @abstractmethod
    def delete(self, key: str) -> bool: ...
    @abstractmethod
    def has(self, key: str) -> bool: ...
    @abstractmethod
    def clear(self) -> None: ...
    @abstractmethod
    def stats(self) -> dict[str, Any]: ...

    @property
    def size(self) -> int:
        return 0
    @property
    def hit_ratio(self) -> float:
        return 0.0


class ITaskQueue(ABC):
    @abstractmethod
    async def start(self) -> None: ...
    @abstractmethod
    async def stop(self, cancel_pending: bool = False) -> None: ...
    @abstractmethod
    async def enqueue(self, name: str, coro_fn: Callable, priority: Any = 50) -> str: ...
    @abstractmethod
    def get_task(self, task_id: str) -> Any: ...
    @abstractmethod
    def cancel(self, task_id: str) -> bool: ...

    @property
    def pending_count(self) -> int:
        return 0
    @property
    def running_count(self) -> int:
        return 0
    @property
    def is_running(self) -> bool:
        return False
