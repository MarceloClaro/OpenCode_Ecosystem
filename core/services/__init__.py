"""
core/services/ — Pacote de Serviços do Core.

Este pacote contém a camada de serviços do OpenCode.
Cada serviço encapsula uma funcionalidade de domínio com
injeção de dependência via Container.

Uso:
    from core.services import get_service_registry, ServiceRegistry
    registry = get_service_registry()
    registry.register("evolution", EvolutionService(db=...))
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from core.container import Container

logger = logging.getLogger(__name__)


class ServiceRegistry:
    """Registro centralizado de serviços do ecossistema.

    Atua como um catálogo de serviços disponíveis, mantendo
    compatibilidade com o Container DI do core.

    Args:
        container: Instância do Container DI (usa singleton se omitido).
    """

    def __init__(self, container: Optional[Container] = None) -> None:
        self._container = container or Container.instance()

    def register(self, name: str, service: Any) -> None:
        """Registra um serviço no container.

        Args:
            name: Nome do serviço (ex: "evolution", "scoring").
            service: Instância do serviço.
        """
        self._container.register(f"service.{name}", service)
        logger.debug("Registered service '%s'", name)

    def resolve(self, name: str) -> Any:
        """Resolve um serviço registrado."""
        return self._container.resolve(f"service.{name}")

    def is_registered(self, name: str) -> bool:
        return self._container.is_registered(f"service.{name}")

    def list_services(self) -> list[str]:
        """Lista todos os serviços registrados."""
        return sorted(
            s.split(".", 1)[1] for s in self._container.registered()
            if s.startswith("service.")
        )

    @property
    def count(self) -> int:
        return len(self.list_services())

    def __repr__(self) -> str:
        return f"ServiceRegistry(services={self.list_services()})"


# ── Singleton ─────────────────────────────────────────────────────

_registry: Optional[ServiceRegistry] = None


def get_service_registry() -> ServiceRegistry:
    """Retorna o singleton do ServiceRegistry."""
    global _registry
    if _registry is None:
        _registry = ServiceRegistry()
    return _registry


def reset_service_registry() -> None:
    """Reseta o singleton (uso em testes)."""
    global _registry
    _registry = None


__all__ = [
    "ServiceRegistry",
    "get_service_registry",
    "reset_service_registry",
]
