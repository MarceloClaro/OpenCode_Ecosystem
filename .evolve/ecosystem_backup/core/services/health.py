"""
core/services/health.py — Serviço de Health Check.

Monitora a saúde de componentes do ecossistema com thresholds.
Exemplo de serviço de domínio registrável via ServiceRegistry.

Uso:
    from core.services import get_service_registry
    from core.services.health import HealthService

    registry = get_service_registry()
    registry.register("health", HealthService())
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ComponentHealth:
    """Estado de saúde de um componente."""
    name: str
    score: float
    status: str  # healthy, attention, alert, critical
    last_check: float = field(default_factory=time.time)
    details: dict[str, Any] = field(default_factory=dict)


class HealthService:
    """Monitora saúde dos componentes do ecossistema.

    Thresholds definidos em `core.config.HealthThresholds`:
    - healthy: >= 95
    - attention: >= 85
    - alert: >= 70
    - critical: < 70
    """

    def __init__(self) -> None:
        self._components: dict[str, ComponentHealth] = {}

    def report_health(self, name: str, score: float,
                      details: Optional[dict[str, Any]] = None) -> ComponentHealth:
        """Registra o estado de saúde de um componente.

        Args:
            name: Nome do componente.
            score: Score de saúde (0-100).
            details: Detalhes adicionais.

        Returns:
            ComponentHealth registrado.
        """
        thresholds = settings.health_thresholds
        if score >= thresholds.healthy:
            status = "healthy"
        elif score >= thresholds.attention:
            status = "attention"
        elif score >= thresholds.alert:
            status = "alert"
        else:
            status = "critical"

        health = ComponentHealth(
            name=name,
            score=score,
            status=status,
            details=details or {},
        )
        self._components[name] = health

        if status != "healthy":
            logger.warning("Health for '%s': %.1f (%s)", name, score, status)
        else:
            logger.debug("Health for '%s': %.1f (%s)", name, score, status)

        return health

    def get_health(self, name: str) -> Optional[ComponentHealth]:
        """Retorna o último health check de um componente."""
        return self._components.get(name)

    def get_all_health(self) -> dict[str, ComponentHealth]:
        """Retorna health de todos os componentes."""
        return dict(self._components)

    @property
    def healthy_count(self) -> int:
        return sum(1 for c in self._components.values() if c.status == "healthy")

    @property
    def attention_count(self) -> int:
        return sum(1 for c in self._components.values() if c.status == "attention")

    @property
    def alert_count(self) -> int:
        return sum(1 for c in self._components.values() if c.status == "alert")

    @property
    def critical_count(self) -> int:
        return sum(1 for c in self._components.values() if c.status == "critical")

    def summary(self) -> dict[str, Any]:
        """Resumo do estado de saúde geral do ecossistema."""
        return {
            "total": len(self._components),
            "healthy": self.healthy_count,
            "attention": self.attention_count,
            "alert": self.alert_count,
            "critical": self.critical_count,
            "average_score": self.average_score,
        }

    @property
    def average_score(self) -> float:
        if not self._components:
            return 0.0
        return sum(c.score for c in self._components.values()) / len(self._components)

    def __repr__(self) -> str:
        return (
            f"HealthService(components={len(self._components)}, "
            f"avg_score={self.average_score:.1f})"
        )
