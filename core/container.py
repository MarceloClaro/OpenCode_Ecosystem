"""
core/container.py (proposto) - Container de Injeção de Dependencia Leve.
Thread-safe: operacoes protegidas por Lock.
Singleton: gerenciado via classe.
"""

from __future__ import annotations
import threading
from typing import Any, Callable, Optional


class ContainerError(Exception): ...
class ServiceNotFoundError(ContainerError): ...


class Container:
    _instance: Optional['Container'] = None
    _init_lock = threading.Lock()

    def __init__(self) -> None:
        self._services: dict[str, Any] = {}
        self._factories: dict[str, Callable[[], Any]] = {}
        self._lock = threading.Lock()

    @classmethod
    def instance(cls) -> 'Container':
        if cls._instance is None:
            with cls._init_lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    def register(self, name: str, instance: Any) -> None:
        with self._lock:
            self._services[name] = instance
            self._factories.pop(name, None)

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        with self._lock:
            self._factories[name] = factory
            self._services.pop(name, None)

    def resolve(self, name: str) -> Any:
        with self._lock:
            if name in self._services:
                return self._services[name]
            if name in self._factories:
                instance = self._factories[name]()
                self._services[name] = instance
                del self._factories[name]
                return instance
        raise ServiceNotFoundError(f"Service '{name}' not registered")

    def registered(self) -> list[str]:
        with self._lock:
            return sorted(list(self._services.keys()) + list(self._factories.keys()))

    def is_registered(self, name: str) -> bool:
        with self._lock:
            return name in self._services or name in self._factories

    def reset(self) -> None:
        with self._lock:
            self._services.clear()
            self._factories.clear()
