# -*- coding: utf-8 -*-
"""core.container - Container de injecao de dependencia (singleton)."""

from typing import Any, Optional


class Container:
    """Container DI singleton simples."""

    _instance: Optional["Container"] = None
    _services: dict[str, Any]

    def __init__(self):
        self._services = {}

    @classmethod
    def instance(cls) -> "Container":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    def register(self, name: str, service: Any) -> None:
        self._services[name] = service

    def resolve(self, name: str) -> Any:
        if name not in self._services:
            raise KeyError(f"Service '{name}' not registered in container")
        return self._services[name]

    def has(self, name: str) -> bool:
        return name in self._services

    def clear(self) -> None:
        self._services.clear()
