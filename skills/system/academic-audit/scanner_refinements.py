#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ScannerRefinements v2.0 — Evolution Tracker + Timeline Estimator

Eixo 3: EvolutionTracker — tracking temporal de scans
Eixo 4: TimelineEstimator — estimativa de duracao para rotas evolutivas
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

BRAZIL_TZ = timezone.utc


# ═══════════════════════════════════════════════════════════════════════════
# EIXO 3 — EVOLUTION TRACKER
# ═══════════════════════════════════════════════════════════════════════════

@dataclass
class ScanSnapshot:
    """Snapshot de um scan noologico em um ponto no tempo."""
    timestamp: str
    noological_coverage: float
    teleological_score: float
    total_gaps: int
    bottlenecks: list[str]
    dimensions: dict[str, dict]  # {dim_key: {coverage_pct, density, covered, absent}}


@dataclass
class DeltaReport:
    """Relatorio de delta entre dois scans."""
    time_delta_days: float
    coverage_delta: float          # positivo = melhoria
    gaps_delta: int                # negativo = melhoria (menos gaps)
    improved_dims: list[str]       # dimensoes que melhoraram >5%
    degraded_dims: list[str]       # dimensoes que pioraram >5%
    new_bottlenecks: list[str]
    resolved_bottlenecks: list[str]


@dataclass
class TrendLine:
    """Linha de tendencia para uma dimensao."""
    dimension: str
    slope: float           # % de melhoria por dia
    direction: str         # "improving" | "stable" | "degrading"
    confidence: float      # 0-1 baseado no numero de pontos


class EvolutionTracker:
    """Rastreia evolucao do ecossistema ao longo do tempo.

    Registra snapshots de scans e compara para detectar tendencias.
    """

    def __init__(self):
        self.snapshots: list[ScanSnapshot] = []

    def record_scan(self, snapshot: ScanSnapshot) -> None:
        """Registra um snapshot de scan."""
        self.snapshots.append(snapshot)

    def compare_scans(self, idx1: int = -2, idx2: int = -1) -> DeltaReport:
        """Compara dois scans e retorna delta.

        Args:
            idx1: indice do scan anterior (default: penultimo)
            idx2: indice do scan posterior (default: ultimo)
        """
        if len(self.snapshots) < 2:
            return DeltaReport(0, 0, 0, [], [], [], [])

        s1 = self.snapshots[idx1]
        s2 = self.snapshots[idx2]

        # Time delta
        try:
            t1 = datetime.fromisoformat(s1.timestamp.replace('Z', '+00:00'))
            t2 = datetime.fromisoformat(s2.timestamp.replace('Z', '+00:00'))
            days = (t2 - t1).total_seconds() / 86400
        except Exception:
            days = 0

        coverage_delta = round(s2.noological_coverage - s1.noological_coverage, 3)
        gaps_delta = s2.total_gaps - s1.total_gaps

        # Dimensoes que mudaram
        improved, degraded = [], []
        for dk in s1.dimensions:
            if dk in s2.dimensions:
                delta_pct = s2.dimensions[dk].get("coverage_pct", 0) - s1.dimensions[dk].get("coverage_pct", 0)
                if delta_pct > 5:
                    improved.append(dk)
                elif delta_pct < -5:
                    degraded.append(dk)

        # Bottlenecks
        new_bn = [b for b in s2.bottlenecks if b not in s1.bottlenecks]
        resolved_bn = [b for b in s1.bottlenecks if b not in s2.bottlenecks]

        return DeltaReport(
            time_delta_days=round(days, 1),
            coverage_delta=coverage_delta,
            gaps_delta=gaps_delta,
            improved_dims=improved,
            degraded_dims=degraded,
            new_bottlenecks=new_bn,
            resolved_bottlenecks=resolved_bn,
        )

    def trend_analysis(self) -> list[TrendLine]:
        """Calcula tendencia para cada dimensao ao longo do tempo."""
        if len(self.snapshots) < 2:
            return []

        trends: list[TrendLine] = []
        all_dims = set()
        for s in self.snapshots:
            all_dims.update(s.dimensions.keys())

        for dim_key in all_dims:
            points: list[tuple[float, float]] = []  # (days_from_start, coverage_pct)
            t0 = None
            for s in self.snapshots:
                if dim_key not in s.dimensions:
                    continue
                try:
                    ts = datetime.fromisoformat(s.timestamp.replace('Z', '+00:00'))
                except Exception:
                    continue
                if t0 is None:
                    t0 = ts
                days = (ts - t0).total_seconds() / 86400
                pct = s.dimensions[dim_key].get("coverage_pct", 0)
                points.append((days, pct))

            if len(points) < 2:
                continue

            # Simple linear regression slope
            n = len(points)
            sum_x = sum(p[0] for p in points)
            sum_y = sum(p[1] for p in points)
            sum_xy = sum(p[0] * p[1] for p in points)
            sum_x2 = sum(p[0] * p[0] for p in points)

            denom = n * sum_x2 - sum_x * sum_x
            slope = ((n * sum_xy - sum_x * sum_y) / denom) if denom != 0 else 0

            direction = "improving" if slope > 0.1 else "degrading" if slope < -0.1 else "stable"
            confidence = min(1.0, n / 5.0)  # mais pontos = mais confianca

            trends.append(TrendLine(
                dimension=dim_key,
                slope=round(slope, 3),
                direction=direction,
                confidence=round(confidence, 2),
            ))

        return sorted(trends, key=lambda t: t.slope, reverse=True)

    def velocity(self) -> float:
        """Taxa de melhoria: reducao de gaps por dia (media)."""
        if len(self.snapshots) < 2:
            return 0.0
        first = self.snapshots[0]
        last = self.snapshots[-1]
        try:
            t1 = datetime.fromisoformat(first.timestamp.replace('Z', '+00:00'))
            t2 = datetime.fromisoformat(last.timestamp.replace('Z', '+00:00'))
            days = max(1, (t2 - t1).total_seconds() / 86400)
        except Exception:
            return 0.0
        gap_reduction = first.total_gaps - last.total_gaps
        return round(gap_reduction / days, 2)


# ═══════════════════════════════════════════════════════════════════════════
# EIXO 4 — TIMELINE ESTIMATOR
# ═══════════════════════════════════════════════════════════════════════════

SCENARIO_DURATION: dict[str, tuple[int, int]] = {
    "quick_win": (1, 2),       # 1-2 semanas
    "foundation": (3, 6),      # 3-6 semanas
    "convergent": (2, 4),      # 2-4 semanas
    "frontier": (8, 16),       # 8-16 semanas
}


@dataclass
class TimelinePhase:
    """Fase temporal do roadmap."""
    name: str
    duration_weeks: int
    scenario_types: list[str]


@dataclass
class EvolutionaryRouteV2:
    """Rota evolutiva com timeline e risco."""
    name: str
    description: str
    phases: list[TimelinePhase]
    total_weeks: int
    risk_level: str  # "low" | "medium" | "high"
    total_priority: float
    estimated_impact: float


class TimelineEstimator:
    """Estima duracao e risco de rotas evolutivas."""

    def estimate_duration(self, scenario_type: str) -> int:
        """Retorna duracao mediana em semanas para um tipo de cenario."""
        lo, hi = SCENARIO_DURATION.get(scenario_type, (4, 8))
        return (lo + hi) // 2

    def estimate_risk(self, total_weeks: int) -> str:
        """Classifica nivel de risco baseado na duracao total."""
        if total_weeks > 16:
            return "high"
        if total_weeks >= 8:
            return "medium"
        return "low"

    def build_timeline(self, route_name: str, description: str,
                       scenarios: list[Any],  # EvolutionaryScenario
                       total_priority: float,
                       estimated_impact: float) -> EvolutionaryRouteV2:
        """Constroi rota V2 com timeline e fases."""
        # Agrupar cenarios consecutivos do mesmo tipo em fases
        phases: list[TimelinePhase] = []
        current_type = None
        current_count = 0
        type_names = {"quick_win": "Quick Wins", "foundation": "Fundacoes",
                      "convergent": "Convergencias", "frontier": "Fronteiras"}

        for s in scenarios:
            if s.scenario_type != current_type:
                if current_type is not None and current_count > 0:
                    duration = self.estimate_duration(current_type) * current_count
                    phases.append(TimelinePhase(
                        name=f"Fase {len(phases)+1}: {type_names.get(current_type, current_type)}",
                        duration_weeks=duration,
                        scenario_types=[current_type] * current_count,
                    ))
                current_type = s.scenario_type
                current_count = 1
            else:
                current_count += 1

        # Ultima fase
        if current_type is not None and current_count > 0:
            duration = self.estimate_duration(current_type) * current_count
            phases.append(TimelinePhase(
                name=f"Fase {len(phases)+1}: {type_names.get(current_type, current_type)}",
                duration_weeks=duration,
                scenario_types=[current_type] * current_count,
            ))

        total_weeks = sum(p.duration_weeks for p in phases)
        risk = self.estimate_risk(total_weeks)

        return EvolutionaryRouteV2(
            name=route_name,
            description=description,
            phases=phases,
            total_weeks=total_weeks,
            risk_level=risk,
            total_priority=total_priority,
            estimated_impact=estimated_impact,
        )
