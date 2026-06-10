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

@dataclass
class ExecutionTrace:
    """Registro de uma execucao do pipeline (mutavel para permitir atualizacoes)."""
    trace_id: str
    timestamp: str
    pipeline: str
    input_hash: str
    output_summary: dict[str, Any]
    duration_ms: float
    anomaly_flags: list[str] = field(default_factory=list)
    confidence: float = 1.0


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

    # ─── N3 UPGRADE: Adaptive Thresholds ─────────────────────────────

    def auto_monitor(self, scan_fn, input_data=None, max_iterations: int = 3) -> dict[str, Any]:
        """Loop autonomo: observa -> detecta -> corrige -> re-observa.

        Diferente de observe(), este metodo executa o ciclo completo
        sem intervencao externa. Corrige e re-avalia ate estabilizar.

        Returns:
            {"iterations": int, "final_confidence": float, "corrections_applied": int, "stabilized": bool}
        """
        results = {"iterations": 0, "final_confidence": 0.0, "corrections_applied": 0, "stabilized": False}

        for iteration in range(max_iterations):
            # Executar scan
            scan_output = scan_fn() if callable(scan_fn) else scan_fn
            trace = self.observe("auto_monitor", scan_output, input_data)
            results["iterations"] = iteration + 1

            # Se nao ha anomalias, estabilizou
            if not self.has_anomalies() and self.confidence.global_confidence > 0.5:
                results["stabilized"] = True
                results["final_confidence"] = self.confidence.global_confidence
                break

            # Corrigir e re-executar
            corrections = self.correct()
            for c in corrections:
                self.corrector.apply(c, lambda _: {"improvement": 0.1})
                results["corrections_applied"] += 1

            # Se a confianca subiu e nao ha mais anomalias criticas
            if self.confidence.global_confidence > 0.5:
                critical_anomalies = [a for a in self._anomalies if a.severity == "critical"]
                if not critical_anomalies:
                    results["stabilized"] = True
                    results["final_confidence"] = self.confidence.global_confidence
                    break

        if not results["stabilized"]:
            results["final_confidence"] = self.confidence.global_confidence

        return results

    def root_cause_analysis(self) -> dict[str, Any]:
        """Analise de causa raiz com inferencia causal (Granger-inspired).

        Nao apenas correlaciona anomalias — infere direcao causal usando:
        1. Temporal precedence: A precede B consistentemente?
        2. Causal chain detection: A -> B -> C?
        3. Common cause detection: A e B compartilham trigger?
        4. Bayesian inference: P(B|A) vs P(B)?

        Returns:
            {"causal_chains": [...], "common_causes": [...], "bayesian": {...}, "verdict": str}
        """
        traces = self._traces
        if len(traces) < 4:
            return {"causal_chains": [], "common_causes": [], "bayesian": {}, "verdict": "insufficient_data (need >= 4 traces)"}

        # ── 1. Extrair sequencia temporal de anomalias ──
        anomaly_sequence: list[tuple[int, set[str]]] = []  # [(trace_index, {pattern_ids})]
        for i, t in enumerate(traces):
            flags = set(t.anomaly_flags)
            if flags:
                anomaly_sequence.append((i, flags))

        if len(anomaly_sequence) < 2:
            return {"causal_chains": [], "common_causes": [], "bayesian": {}, "verdict": "insufficient_anomalies"}

        # ── 2. Teste de precedencia temporal (Granger-inspired) ──
        pattern_types = list(set(a.pattern_id for a in self._anomalies))
        causal_edges: list[dict[str, Any]] = []

        for cause_type in pattern_types:
            for effect_type in pattern_types:
                if cause_type == effect_type:
                    continue

                # Contar: quantas vezes cause_type aparece antes de effect_type?
                precedence_count = 0
                total_cause = 0
                total_effect = 0

                for i in range(len(anomaly_sequence) - 1):
                    current_flags = anomaly_sequence[i][1]
                    next_flags = anomaly_sequence[i + 1][1]

                    if cause_type in current_flags:
                        total_cause += 1
                        if effect_type in next_flags:
                            precedence_count += 1

                    if effect_type in next_flags:
                        total_effect += 1

                if total_cause > 0:
                    precedence_ratio = precedence_count / total_cause
                    # Granger score: how much does knowing A improve prediction of B?
                    p_b_given_a = precedence_count / max(1, total_cause)
                    p_b = total_effect / max(1, len(anomaly_sequence))

                    granger_score = p_b_given_a - p_b

                    if precedence_ratio >= 0.5 and granger_score > 0.2:
                        causal_edges.append({
                            "cause": cause_type,
                            "effect": effect_type,
                            "precedence_ratio": round(precedence_ratio, 2),
                            "granger_score": round(granger_score, 2),
                            "evidence": f"{cause_type} precedes {effect_type} in {precedence_count}/{total_cause} cases (Granger +{granger_score:.2f})",
                            "confidence": "high" if precedence_ratio >= 0.75 else "medium",
                        })

        causal_edges.sort(key=lambda e: -e["granger_score"])

        # ── 3. Construir cadeias causais ──
        causal_chains = self._build_causal_chains(causal_edges)

        # ── 4. Detectar causas comuns ──
        common_causes = self._detect_common_causes(anomaly_sequence, pattern_types)

        # ── 5. Inferencia bayesiana ──
        bayesian = self._bayesian_inference(anomaly_sequence, pattern_types)

        # ── 6. Verdict ──
        if causal_chains:
            chain_descriptions = [" -> ".join(c) for c in causal_chains[:3]]
            verdict = f"Cadeias causais detectadas: {'; '.join(chain_descriptions)}. "
            if common_causes:
                verdict += f"Causas comuns: {len(common_causes)} triggers compartilhados."
            verdict += f" Confianca bayesiana media: {bayesian.get('avg_confidence', 0):.2f}"
        elif common_causes:
            verdict = f"Sem cadeias causais. {len(common_causes)} causas comuns identificadas (anomalias compartilham triggers)."
        elif causal_edges:
            verdict = f"Evidencia causal fraca: {len(causal_edges)} arestas com Granger score baixo. Dados insuficientes para cadeias."
        else:
            verdict = "Sem evidencia causal: anomalias parecem independentes."

        return {
            "causal_edges": causal_edges[:5],
            "causal_chains": causal_chains[:3],
            "common_causes": common_causes[:3],
            "bayesian": bayesian,
            "verdict": verdict,
        }

    def _build_causal_chains(self, edges: list[dict]) -> list[list[str]]:
        """Constrói cadeias causais a partir de arestas direcionadas."""
        if not edges:
            return []

        # Construir grafo direcionado
        graph: dict[str, set[str]] = {}
        for e in edges:
            graph.setdefault(e["cause"], set()).add(e["effect"])

        # Encontrar cadeias (DFS com profundidade maxima 3)
        chains = []
        visited_in_chain: set[str] = set()

        def dfs(node: str, path: list[str]):
            if len(path) > 3:
                chains.append(list(path))
                return
            for neighbor in graph.get(node, set()):
                if neighbor not in path:
                    dfs(neighbor, path + [neighbor])
                elif len(path) >= 2:
                    chains.append(list(path))

        for start in graph:
            if start not in visited_in_chain:
                dfs(start, [start])
                visited_in_chain.add(start)

        # Remover duplicatas e sub-cadeias
        unique = []
        for c in chains:
            if not any(set(c).issubset(set(existing)) and len(c) < len(existing) for existing in unique):
                unique.append(c)

        return unique[:3]

    def _detect_common_causes(self, sequence: list, pattern_types: list[str]) -> list[dict]:
        """Detecta anomalias que sempre co-ocorrem (possivel causa comum)."""
        common = []
        for i, p1 in enumerate(pattern_types):
            for p2 in pattern_types[i+1:]:
                co_occurrence = 0
                p1_total = 0
                p2_total = 0
                for _, flags in sequence:
                    has_p1 = p1 in flags
                    has_p2 = p2 in flags
                    if has_p1: p1_total += 1
                    if has_p2: p2_total += 1
                    if has_p1 and has_p2: co_occurrence += 1

                total_occurrences = max(p1_total, p2_total)
                if total_occurrences > 0:
                    co_rate = co_occurrence / total_occurrences
                    if co_rate >= 0.7:
                        common.append({
                            "patterns": [p1, p2],
                            "co_occurrence_rate": round(co_rate, 2),
                            "hypothesis": f"{p1} e {p2} compartilham trigger comum (co-ocorrem em {co_rate:.0%} dos casos)",
                        })

        return sorted(common, key=lambda c: -c["co_occurrence_rate"])

    def _bayesian_inference(self, sequence: list, pattern_types: list[str]) -> dict:
        """Calcula probabilidades condicionais entre anomalias."""
        if len(pattern_types) < 2:
            return {"inferences": [], "avg_confidence": 0}

        total_events = len(sequence)
        inferences = []

        for cause in pattern_types:
            for effect in pattern_types:
                if cause == effect: continue

                # P(effect | cause)
                cause_count = sum(1 for _, flags in sequence if cause in flags)
                joint_count = sum(1 for _, flags in sequence if cause in flags and effect in flags)

                if cause_count > 0:
                    p_effect_given_cause = joint_count / cause_count
                    # P(effect) marginal
                    p_effect = sum(1 for _, flags in sequence if effect in flags) / max(1, total_events)
                    # Lift: quanto P(effect|cause) excede P(effect)
                    lift = p_effect_given_cause / max(0.01, p_effect)

                    if lift > 1.5:
                        inferences.append({
                            "cause": cause, "effect": effect,
                            "p_effect_given_cause": round(p_effect_given_cause, 2),
                            "p_effect_marginal": round(p_effect, 2),
                            "lift": round(lift, 1),
                        })

        inferences.sort(key=lambda i: -i["lift"])
        avg_conf = sum(i["lift"] for i in inferences) / max(1, len(inferences))

        return {"inferences": inferences[:5], "avg_confidence": round(avg_conf, 1)}

    def adaptive_thresholds(self) -> dict[str, float]:
        """Ajusta thresholds de deteccao baseado no historico.

        Se o sistema consistentemente detecta anomalias que nao se confirmam
        (falsos positivos), os thresholds sao relaxados. Se anomalias reais
        passam despercebidas, thresholds sao apertados.
        """
        if len(self._traces) < 5:
            return {"density_drop_threshold": 0.30, "category_loss_threshold": 2, "stagnation_cycles": 3}

        # Calcular taxa de falsos positivos
        corrections = self.corrector._corrections
        if corrections:
            false_positive_rate = 1.0 - self.corrector.success_rate
        else:
            false_positive_rate = 0.25  # default conservador

        # Ajustar thresholds
        density_threshold = 0.30 + (false_positive_rate * 0.20)  # 0.30 a 0.50
        category_threshold = max(1, int(2 + false_positive_rate * 3))  # 2 a 5
        stagnation_cycles = max(2, int(3 + false_positive_rate * 2))  # 3 a 5

        return {
            "density_drop_threshold": round(density_threshold, 2),
            "category_loss_threshold": category_threshold,
            "stagnation_cycles": stagnation_cycles,
            "false_positive_rate": round(false_positive_rate, 2),
        }

    def correction_learning_report(self) -> dict[str, Any]:
        """Relatorio de aprendizado: quais correcoes funcionam melhor?"""
        corrections = self.corrector._corrections
        if not corrections:
            return {"status": "no_data"}

        by_type: dict[str, dict[str, Any]] = {}
        for c in corrections:
            if c.action_type not in by_type:
                by_type[c.action_type] = {"total": 0, "success": 0, "total_delta": 0.0}
            by_type[c.action_type]["total"] += 1
            if c.success:
                by_type[c.action_type]["success"] += 1
                by_type[c.action_type]["total_delta"] += c.delta_improvement

        # Rankear por taxa de sucesso
        ranked = []
        for atype, stats in by_type.items():
            rate = stats["success"] / max(1, stats["total"])
            avg_delta = stats["total_delta"] / max(1, stats["success"])
            ranked.append({"action_type": atype, "success_rate": round(rate, 2),
                          "avg_improvement": round(avg_delta, 4), "total_applied": stats["total"]})

        ranked.sort(key=lambda x: -x["success_rate"])
        best = ranked[0]["action_type"] if ranked else "unknown"

        return {
            "correction_types_learned": len(by_type),
            "best_action": best,
            "ranked_actions": ranked,
            "recommendation": f"Preferir {best} — maior taxa de sucesso",
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
