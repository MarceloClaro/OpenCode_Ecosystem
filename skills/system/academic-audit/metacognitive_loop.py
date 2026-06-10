#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MetacognitiveLoop v1.0 — SPEC-036: Auto-Observacao e Auto-Correcao
===================================================================
Implementa o gap critico 'raciocinio.Metacognitivo' identificado pelo scanner.

Arquitetura:
  1. ExecutionTrace  — registro imutavel de cada execucao do pipeline
  2. AnomalyDetector — detecta padroes anomalos em outputs do pipeline
  3. ConfidenceEstimator — estima confianca por dimensao do scanner
  4. CorrectionEngine — dispara correcoes automaticas quando anomalias detectadas
  5. MetacognitiveMonitor — orquestrador do loop metacognitivo

Principios:
  - Self-observation: todo output do pipeline e registrado e analisado
  - Anomaly detection: desvios de padroes historicos disparam alertas
  - Auto-correction: correcoes sao aplicadas e re-avaliadas
  - Feedback loop: cada correcao alimenta o modelo de confianca

Autor: OpenCode Ecosystem (2026) — R21: Metacognicao
Integracao: SPEC-028 a SPEC-035
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


BRAZIL_TZ = timezone.utc


# ═══════════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ExecutionTrace:
    """Registro imutavel de uma execucao do pipeline."""
    trace_id: str
    timestamp: str
    pipeline: str               # "noological", "teleological", "evolutionary", etc.
    input_hash: str             # hash do input para deduplicacao
    output_summary: dict[str, Any]  # metricas consolidadas
    duration_ms: float
    anomaly_flags: list[str] = field(default_factory=list)
    confidence: float = 1.0     # 0-1


@dataclass
class AnomalyPattern:
    """Padrao anomalo detectado."""
    pattern_id: str
    dimension: str              # qual dimensao do scanner
    expected_range: tuple[float, float]  # (min, max) esperado
    actual_value: float
    severity: str               # "critical" | "high" | "moderate" | "low"
    description: str
    detected_at: str = ""


@dataclass
class CorrectionAction:
    """Acao corretiva aplicada."""
    action_id: str
    target_dimension: str
    action_type: str            # "recalibrate" | "rerun" | "expand_keywords" | "adjust_weights"
    description: str
    applied_at: str = ""
    success: bool = False
    delta_improvement: float = 0.0  # melhoria na metrica apos correcao


# ═══════════════════════════════════════════════════════════════════════════
# ANOMALY DETECTOR
# ═══════════════════════════════════════════════════════════════════════════

class AnomalyDetector:
    """Detecta anomalias em outputs do pipeline comparando com historico."""

    def __init__(self):
        self._history: list[dict[str, Any]] = []
        self._patterns: list[AnomalyPattern] = []

    def record(self, scan_output: dict[str, Any]) -> None:
        """Registra um output no historico."""
        self._history.append({
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            "overall_density": scan_output.get("overall_density", 0),
            "dimensions": scan_output.get("dimensions", {}),
        })

    def detect(self, scan_output: dict[str, Any]) -> list[AnomalyPattern]:
        """Detecta anomalias comparando com historico."""
        anomalies: list[AnomalyPattern] = []

        if len(self._history) < 2:
            return anomalies  # precisa de historico minimo

        # Anomalia 1: Queda brusca de densidade global (>30% abaixo da media)
        densities = [h["overall_density"] for h in self._history[-5:]]
        avg_density = sum(densities) / len(densities)
        current = scan_output.get("overall_density", 0)

        if avg_density > 0 and current < avg_density * 0.7:
            anomalies.append(AnomalyPattern(
                pattern_id="ANOM-001",
                dimension="global",
                expected_range=(avg_density * 0.7, 1.0),
                actual_value=current,
                severity="critical",
                description=f"Queda brusca de densidade: {current:.0%} vs media {avg_density:.0%}",
            ))

        # Anomalia 2: Dimensao que era coberta ficou ausente
        dims = scan_output.get("dimensions", {})
        for h in self._history[-3:]:
            h_dims = h.get("dimensions", {})
            for dk, dd in dims.items():
                hd = h_dims.get(dk, {})
                prev_covered = set(hd.get("covered", []))
                curr_covered = set(dd.get("covered", []))
                lost = prev_covered - curr_covered
                if len(lost) >= 2:
                    anomalies.append(AnomalyPattern(
                        pattern_id="ANOM-002",
                        dimension=dk,
                        expected_range=(0, len(prev_covered)),
                        actual_value=len(curr_covered),
                        severity="high",
                        description=f"Dimensao {dk} perdeu {len(lost)} categorias: {lost}",
                    ))

        # Anomalia 3: Comfort zone estagnada (mesmas categorias por 3+ scans)
        if len(self._history) >= 3:
            last_covered = set()
            for dk, dd in dims.items():
                last_covered.update(dd.get("covered", []))
            prev_covered_sets = []
            for h in self._history[-3:]:
                s = set()
                for dk, dd in h.get("dimensions", {}).items():
                    s.update(dd.get("covered", []))
                prev_covered_sets.append(s)

            if all(last_covered == s for s in prev_covered_sets):
                anomalies.append(AnomalyPattern(
                    pattern_id="ANOM-003",
                    dimension="global",
                    expected_range=(0, 0),
                    actual_value=0,
                    severity="moderate",
                    description="Comfort zone estagnada: mesmas categorias ha 3+ scans",
                ))

        self._patterns.extend(anomalies)
        return anomalies


# ═══════════════════════════════════════════════════════════════════════════
# CONFIDENCE ESTIMATOR
# ═══════════════════════════════════════════════════════════════════════════

class ConfidenceEstimator:
    """Estima confianca por dimensao do scanner."""

    def __init__(self):
        self._dimension_confidence: dict[str, float] = {}
        self._global_confidence: float = 0.5

    def estimate(self, scan_output: dict[str, Any]) -> dict[str, float]:
        """Calcula confianca para cada dimensao baseado em:
        - Densidade de cobertura
        - Consistencia historica
        - Severidade de blind spots
        """
        dims = scan_output.get("dimensions", {})
        confidences: dict[str, float] = {}

        for dk, dd in dims.items():
            density = dd.get("density", 0)
            coverage = dd.get("coverage_pct", 0)
            blind_spot_score = dd.get("blind_spot_score", 0)

            # Confianca = combinacao ponderada
            confidence = (
                0.4 * density
                + 0.3 * (coverage / 100)
                + 0.3 * (1.0 - blind_spot_score)
            )
            confidences[dk] = round(min(1.0, max(0.0, confidence)), 4)

        self._dimension_confidence = confidences
        self._global_confidence = (
            sum(confidences.values()) / len(confidences) if confidences else 0.0
        )
        return confidences

    @property
    def global_confidence(self) -> float:
        return self._global_confidence

    def low_confidence_dimensions(self, threshold: float = 0.3) -> list[str]:
        """Dimensoes com confianca abaixo do threshold."""
        return [dk for dk, c in self._dimension_confidence.items() if c < threshold]


# ═══════════════════════════════════════════════════════════════════════════
# CORRECTION ENGINE
# ═══════════════════════════════════════════════════════════════════════════

class CorrectionEngine:
    """Dispara correcoes automaticas baseadas em anomalias detectadas."""

    def __init__(self):
        self._corrections: list[CorrectionAction] = []
        self._correction_count: int = 0

    def propose_corrections(
        self, anomalies: list[AnomalyPattern],
        low_confidence_dims: list[str],
    ) -> list[CorrectionAction]:
        """Propoe acoes corretivas para anomalias e baixa confianca."""
        actions: list[CorrectionAction] = []

        for anomaly in anomalies:
            if anomaly.severity == "critical":
                actions.append(CorrectionAction(
                    action_id=f"CORR-{self._correction_count + len(actions) + 1:03d}",
                    target_dimension=anomaly.dimension,
                    action_type="rerun",
                    description=f"Re-executar scan com parametros ajustados: {anomaly.description[:80]}",
                ))

            elif anomaly.pattern_id == "ANOM-002":
                actions.append(CorrectionAction(
                    action_id=f"CORR-{self._correction_count + len(actions) + 1:03d}",
                    target_dimension=anomaly.dimension,
                    action_type="expand_keywords",
                    description=f"Expandir keywords para recuperar categorias perdidas em {anomaly.dimension}",
                ))

            elif anomaly.pattern_id == "ANOM-003":
                actions.append(CorrectionAction(
                    action_id=f"CORR-{self._correction_count + len(actions) + 1:03d}",
                    target_dimension="global",
                    action_type="recalibrate",
                    description="Recalibrar pesos para forcar exploracao de novas dimensoes",
                ))

        # Baixa confianca → ajustar pesos
        for dim in low_confidence_dims:
            actions.append(CorrectionAction(
                action_id=f"CORR-{self._correction_count + len(actions) + 1:03d}",
                target_dimension=dim,
                action_type="adjust_weights",
                description=f"Aumentar peso da dimensao {dim} para melhorar cobertura",
            ))

        return actions

    def apply(self, action: CorrectionAction, scan_fn) -> CorrectionAction:
        """Aplica uma correcao e mede o resultado."""
        before = time.time()
        try:
            result = scan_fn(action)
            action.success = True
            action.delta_improvement = result.get("improvement", 0.0)
        except Exception as e:
            action.success = False
            action.description += f" [FAILED: {str(e)[:50]}]"

        action.applied_at = datetime.now(BRAZIL_TZ).isoformat()
        self._corrections.append(action)
        self._correction_count += 1
        return action

    @property
    def total_corrections(self) -> int:
        return self._correction_count

    @property
    def success_rate(self) -> float:
        if not self._corrections:
            return 1.0
        return sum(1 for c in self._corrections if c.success) / len(self._corrections)


# ═══════════════════════════════════════════════════════════════════════════
# METACOGNITIVE MONITOR (Orquestrador)
# ═══════════════════════════════════════════════════════════════════════════

class MetacognitiveMonitor:
    """Loop metacognitivo: observa → detecta → corrige → re-avalia.

    Uso:
        monitor = MetacognitiveMonitor()
        monitor.observe(pipeline_output)

        if monitor.has_anomalies():
            corrections = monitor.correct()
            for c in corrections:
                pipeline.rerun_with(c)
    """

    def __init__(self):
        self.detector = AnomalyDetector()
        self.confidence = ConfidenceEstimator()
        self.corrector = CorrectionEngine()
        self._traces: list[ExecutionTrace] = []
        self._trace_count: int = 1
        self._anomalies: list[AnomalyPattern] = []
        self._pending_corrections: list[CorrectionAction] = []

    def observe(self, pipeline_name: str, scan_output: dict[str, Any],
                input_data: Any = None) -> ExecutionTrace:
        """Observa uma execucao do pipeline.

        1. Registra no historico
        2. Detecta anomalias
        3. Estima confianca
        4. Cria trace de execucao
        """
        # Registrar no detector
        self.detector.record(scan_output)

        # Detectar anomalias
        self._anomalies = self.detector.detect(scan_output)

        # Estimar confianca
        confidences = self.confidence.estimate(scan_output)

        # Criar trace
        input_hash = str(hash(str(input_data)))[:12] if input_data else "no-input"
        trace = ExecutionTrace(
            trace_id=f"TRACE-{self._trace_count:04d}",
            timestamp=datetime.now(BRAZIL_TZ).isoformat(),
            pipeline=pipeline_name,
            input_hash=input_hash,
            output_summary={
                "overall_density": scan_output.get("overall_density", 0),
                "anomalies_detected": len(self._anomalies),
                "global_confidence": self.confidence.global_confidence,
                "low_confidence_dims": self.confidence.low_confidence_dimensions(),
            },
            duration_ms=0,
            anomaly_flags=[a.pattern_id for a in self._anomalies],
            confidence=self.confidence.global_confidence,
        )

        self._traces.append(trace)
        self._trace_count += 1
        return trace

    def has_anomalies(self) -> bool:
        """Retorna True se anomalias foram detectadas na ultima observacao."""
        return len(self._anomalies) > 0

    def has_low_confidence(self, threshold: float = 0.3) -> bool:
        """Retorna True se ha dimensoes com baixa confianca."""
        return len(self.confidence.low_confidence_dimensions(threshold)) > 0

    def correct(self) -> list[CorrectionAction]:
        """Propoe correcoes para anomalias e baixa confianca."""
        self._pending_corrections = self.corrector.propose_corrections(
            self._anomalies,
            self.confidence.low_confidence_dimensions(),
        )
        return self._pending_corrections

    @property
    def status(self) -> dict[str, Any]:
        """Status atual do monitor metacognitivo."""
        return {
            "traces_recorded": len(self._traces),
            "anomalies_detected": len(self._anomalies),
            "global_confidence": self.confidence.global_confidence,
            "corrections_applied": self.corrector.total_corrections,
            "correction_success_rate": self.corrector.success_rate,
            "low_confidence_dimensions": self.confidence.low_confidence_dimensions(),
            "pending_corrections": len(self._pending_corrections),
        }

    def report(self) -> str:
        """Relatorio metacognitivo em Markdown."""
        s = self.status
        lines = [
            "# Relatorio Metacognitivo",
            "",
            f"**Traces registrados**: {s['traces_recorded']}",
            f"**Anomalias detectadas**: {s['anomalies_detected']}",
            f"**Confianca global**: {s['global_confidence']:.0%}",
            f"**Correcoes aplicadas**: {s['corrections_applied']}",
            f"**Taxa de sucesso**: {s['correction_success_rate']:.0%}",
            "",
        ]
        if s["low_confidence_dimensions"]:
            lines.append("## Dimensoes com Baixa Confianca")
            for dim in s["low_confidence_dimensions"]:
                lines.append(f"- `{dim}`")
        if s["pending_corrections"]:
            lines.append(f"\n## Correcoes Pendentes ({s['pending_corrections']})")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════════════
# FACTORY
# ═══════════════════════════════════════════════════════════════════════════

def create_metacognitive_monitor() -> MetacognitiveMonitor:
    """Factory: cria monitor metacognitivo pronto para uso."""
    return MetacognitiveMonitor()
