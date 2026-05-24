"""
core/services/evolution.py — Serviço de Evolução (AutoEvolve).

Gerencia o pipeline evolutivo: PLAN → ACT → CORRECT → REFLECT → EVOLVE.
Exemplo de serviço de domínio registrável via ServiceRegistry.

Uso:
    from core.services import get_service_registry
    from core.services.evolution import EvolutionService

    registry = get_service_registry()
    registry.register("evolution", EvolutionService())
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any, Optional

from core.errors import ServiceError

logger = logging.getLogger(__name__)


@dataclass
class EvolutionRound:
    """Resultado de uma rodada de evolução."""
    round_number: int
    skill_name: str
    score: float
    insights: list[str] = field(default_factory=list)
    timestamp: float = field(default_factory=time.time)


class EvolutionService:
    """Serviço de evolução autônoma do ecossistema.

    Pipeline: PLAN → ACT → CORRECT → REFLECT → EXTRACT → EVOLVE.

    Attributes:
        rounds: Histórico de rodadas de evolução.
    """

    def __init__(self, max_history: int = 100) -> None:
        self._max_history = max_history
        self._rounds: list[EvolutionRound] = []

    @property
    def rounds(self) -> list[EvolutionRound]:
        return list(self._rounds)

    @property
    def latest_round(self) -> Optional[EvolutionRound]:
        return self._rounds[-1] if self._rounds else None

    @property
    def best_score(self) -> float:
        if not self._rounds:
            return 0.0
        return max(r.score for r in self._rounds)

    @property
    def average_score(self) -> float:
        if not self._rounds:
            return 0.0
        return sum(r.score for r in self._rounds) / len(self._rounds)

    def record_round(self, round_num: int, skill: str, score: float,
                     insights: Optional[list[str]] = None) -> EvolutionRound:
        """Registra uma rodada de evolução."""
        rec = EvolutionRound(
            round_number=round_num,
            skill_name=skill,
            score=score,
            insights=insights or [],
        )
        self._rounds.append(rec)
        if len(self._rounds) > self._max_history:
            self._rounds.pop(0)
        logger.info(
            "Evolution round %d: skill=%s score=%.1f insights=%d",
            round_num, skill, score, len(rec.insights),
        )
        return rec

    def __repr__(self) -> str:
        return (
            f"EvolutionService(rounds={len(self._rounds)}, "
            f"best={self.best_score:.1f}, avg={self.average_score:.1f})"
        )
