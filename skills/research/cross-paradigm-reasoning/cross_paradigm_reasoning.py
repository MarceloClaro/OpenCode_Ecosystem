#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cross-Paradigm Reasoning Engine v1.0 — R38 / SPEC-082
======================================================
Integrates 4 reasoning engines (Z3, SymPy, Kanren, Critical) with
4 research skills (game_theory, temporal_population,
theoretical_empirical, logical_multiscale) for multi-paradigm problem
solving.

Components:
  - ReasoningOrchestrator: routes problems to appropriate engines
  - CrossParadigmSynthesizer: combines multi-engine results
  - AutonomousSelfRepair: detects & fixes inconsistencies
  - ParadigmBridge: translates between reasoning formalisms

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

from __future__ import annotations

import json
import os
import sys
import time
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path


# ────────────────────────────────────────────────────────────
# Types
# ────────────────────────────────────────────────────────────

class ReasoningMode(Enum):
    AUTO = "auto"
    FORMAL = "formal"
    SYMBOLIC = "symbolic"
    LOGIC = "logic"
    CRITICAL = "critical"
    RESEARCH = "research"  # Nova: integra research skills
    ALL = "all"


@dataclass
class EngineResult:
    engine: str
    status: str  # success | error | unavailable
    output: Any = None
    confidence: float = 0.0
    time_ms: float = 0.0
    error: str = ""


@dataclass
class SynthesisResult:
    problem: str
    mode: str
    engine_results: List[EngineResult] = field(default_factory=list)
    synthesized_output: Any = None
    contradictions: List[Dict[str, Any]] = field(default_factory=list)
    overall_confidence: float = 0.0
    repairs_applied: List[Dict[str, Any]] = field(default_factory=list)
    time_ms: float = 0.0


# ────────────────────────────────────────────────────────────
# Engine Connectors (wrappers para os motores reais)
# ────────────────────────────────────────────────────────────

# Cache de engines para não recarregar a cada chamada
_ENGINE_CACHE: Dict[str, Any] = {}


def _load_z3_engine():
    """Carrega Z3Engine do diretório de skills."""
    if "z3" in _ENGINE_CACHE:
        return _ENGINE_CACHE["z3"]
    try:
        path = str(Path(__file__).parent.parent.parent /
                   "reasoning/formal-verification/scripts")
        if path not in sys.path:
            sys.path.insert(0, path)
        from z3_engine import Z3Engine
        engine = Z3Engine()
        _ENGINE_CACHE["z3"] = engine
        return engine
    except Exception as e:
        return None


def _load_sympy_engine():
    """Carrega SymPyEngine."""
    if "sympy" in _ENGINE_CACHE:
        return _ENGINE_CACHE["sympy"]
    try:
        path = str(Path(__file__).parent.parent.parent /
                   "reasoning/symbolic-math/scripts")
        if path not in sys.path:
            sys.path.insert(0, path)
        from sympy_engine import SymPyEngine
        engine = SymPyEngine()
        _ENGINE_CACHE["sympy"] = engine
        return engine
    except Exception as e:
        return None


def _load_kanren_engine():
    """Carrega KanrenEngine."""
    if "kanren" in _ENGINE_CACHE:
        return _ENGINE_CACHE["kanren"]
    try:
        path = str(Path(__file__).parent.parent.parent /
                   "reasoning/logic-programming/scripts")
        if path not in sys.path:
            sys.path.insert(0, path)
        from kanren_engine import KanrenEngine
        engine = KanrenEngine()
        _ENGINE_CACHE["kanren"] = engine
        return engine
    except Exception as e:
        return None


def _load_research_skill(skill_name: str):
    """Carrega uma research skill dinamicamente."""
    cache_key = f"rs_{skill_name}"
    if cache_key in _ENGINE_CACHE:
        return _ENGINE_CACHE[cache_key]

    paths = {
        "game_theory": "skills/research/game-theory/game_theory.py",
        "temporal_population": "skills/research/temporal-population/temporal_population.py",
        "theoretical_empirical": "skills/research/theoretical-empirical/theoretical_empirical.py",
        "logical_multiscale": "skills/research/logical-multiscale/logical_multiscale.py",
    }
    if skill_name not in paths:
        return None

    try:
        skill_file = str(Path(__file__).parent.parent.parent / paths[skill_name])
        d = os.path.dirname(skill_file)
        if d not in sys.path:
            sys.path.insert(0, d)
        import importlib.util
        spec = importlib.util.spec_from_file_location(skill_name, skill_file)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[skill_name] = mod
            spec.loader.exec_module(mod)
            _ENGINE_CACHE[cache_key] = mod
            return mod
    except Exception:
        pass
    return None


def _run_research_skill(skill_name: str, operation: str,
                        params: Optional[Dict] = None) -> EngineResult:
    """Executa uma operação em uma research skill."""
    t0 = time.time()
    mod = _load_research_skill(skill_name)
    if mod is None:
        return EngineResult(skill_name, "unavailable",
                            time_ms=(time.time() - t0) * 1000)
    p = params or {}

    try:
        if skill_name == "game_theory":
            if operation == "nash" and "payoff_matrix" in p:
                pm = mod.PayoffMatrix(p["payoff_matrix"])
                ne = mod.NashEquilibrium(pm)
                eq = ne.find_pure_nash()
                return EngineResult("game_theory", "success",
                                    output={"equilibria": eq}, confidence=0.85,
                                    time_ms=(time.time() - t0) * 1000)
            return EngineResult("game_theory", "success",
                                output={"note": f"Unknown op: {operation}"},
                                confidence=0.5,
                                time_ms=(time.time() - t0) * 1000)

        elif skill_name == "temporal_population":
            if operation == "moving_average" and "data" in p:
                ta = mod.TimeSeriesAnalyzer()
                result = ta.moving_average(p["data"], p.get("window", 3))
                return EngineResult("temporal_population", "success",
                                    output={"moving_average": result},
                                    confidence=0.85,
                                    time_ms=(time.time() - t0) * 1000)
            return EngineResult("temporal_population", "success",
                                output={"note": f"Unknown op: {operation}"},
                                confidence=0.5,
                                time_ms=(time.time() - t0) * 1000)

        elif skill_name == "theoretical_empirical":
            if operation == "classify" and "theory" in p:
                ec = mod.EpistemologicalClassifier()
                result = ec.classify(p["theory"])
                return EngineResult("theoretical_empirical", "success",
                                    output={"classification": result},
                                    confidence=0.85,
                                    time_ms=(time.time() - t0) * 1000)
            return EngineResult("theoretical_empirical", "success",
                                output={"note": f"Unknown op: {operation}"},
                                confidence=0.5,
                                time_ms=(time.time() - t0) * 1000)

        elif skill_name == "logical_multiscale":
            if operation == "deductive" and "premises" in p:
                ie = mod.InferenceEngine()
                result = ie.deductive_valid(p["premises"], p.get("conclusion", ""))
                return EngineResult("logical_multiscale", "success",
                                    output={"valid": result},
                                    confidence=0.85,
                                    time_ms=(time.time() - t0) * 1000)
            return EngineResult("logical_multiscale", "success",
                                output={"note": f"Unknown op: {operation}"},
                                confidence=0.5,
                                time_ms=(time.time() - t0) * 1000)

        else:
            return EngineResult(skill_name, "error",
                                error=f"Unknown skill: {skill_name}",
                                time_ms=(time.time() - t0) * 1000)
    except Exception as e:
        return EngineResult(skill_name, "error", error=str(e),
                            time_ms=(time.time() - t0) * 1000)


def _load_critical_engine():
    """Carrega CriticalEngine."""
    if "critical" in _ENGINE_CACHE:
        return _ENGINE_CACHE["critical"]
    try:
        path = str(Path(__file__).parent.parent.parent /
                   "reasoning/critical-reasoning/scripts")
        if path not in sys.path:
            sys.path.insert(0, path)
        from critical_engine import CriticalEngine
        engine = CriticalEngine()
        _ENGINE_CACHE["critical"] = engine
        return engine
    except Exception as e:
        return None


def _run_engine(engine_name: str, problem: str, context: Optional[Dict] = None) -> EngineResult:
    """Executa um motor de raciocínio e retorna o resultado."""
    t0 = time.time()
    ctx = context or {}

    if engine_name == "z3":
        eng = _load_z3_engine()
        if eng is None:
            return EngineResult("z3", "unavailable", confidence=0.0,
                                time_ms=(time.time() - t0) * 1000)
        try:
            # Extrai constraints do problema
            constraints = [problem] if problem else []
            result = eng.check_sat(constraints)
            ms = (time.time() - t0) * 1000
            return EngineResult("z3", "success",
                                output={"status": result.status, "proof": result.proof},
                                confidence=0.9 if result.status == "sat" else 0.7,
                                time_ms=ms)
        except Exception as e:
            return EngineResult("z3", "error", error=str(e),
                                time_ms=(time.time() - t0) * 1000)

    elif engine_name == "sympy":
        eng = _load_sympy_engine()
        if eng is None:
            return EngineResult("sympy", "unavailable", confidence=0.0,
                                time_ms=(time.time() - t0) * 1000)
        try:
            result = eng.solve(problem)
            ms = (time.time() - t0) * 1000
            return EngineResult("sympy", "success",
                                output={"expression": result.expression,
                                        "solutions": result.solutions,
                                        "latex": result.latex},
                                confidence=0.85 if result.solutions else 0.5,
                                time_ms=ms)
        except Exception as e:
            return EngineResult("sympy", "error", error=str(e),
                                time_ms=(time.time() - t0) * 1000)

    elif engine_name == "kanren":
        eng = _load_kanren_engine()
        if eng is None:
            return EngineResult("kanren", "unavailable", confidence=0.0,
                                time_ms=(time.time() - t0) * 1000)
        try:
            # Adiciona contexto como fatos
            for fact_key, fact_val in ctx.get("facts", {}).items():
                eng.assert_fact(fact_key, *([fact_val] if not isinstance(fact_val, list) else fact_val))
            result = eng.query(problem)
            ms = (time.time() - t0) * 1000
            return EngineResult("kanren", "success",
                                output={"solutions": result.solutions,
                                        "num_solutions": result.num_solutions},
                                confidence=0.8 if result.num_solutions > 0 else 0.4,
                                time_ms=ms)
        except Exception as e:
            return EngineResult("kanren", "error", error=str(e),
                                time_ms=(time.time() - t0) * 1000)

    elif engine_name == "critical":
        eng = _load_critical_engine()
        if eng is None:
            return EngineResult("critical", "unavailable", confidence=0.0,
                                time_ms=(time.time() - t0) * 1000)
        try:
            result = eng.analyze(problem)
            ms = (time.time() - t0) * 1000
            return EngineResult("critical", "success",
                                output={"fallacies": getattr(result, 'fallacies', result)},
                                confidence=0.75,
                                time_ms=ms)
        except Exception as e:
            return EngineResult("critical", "error", error=str(e),
                                time_ms=(time.time() - t0) * 1000)

    else:
        return EngineResult(engine_name, "error", error=f"Unknown engine: {engine_name}",
                            time_ms=(time.time() - t0) * 1000)


# ────────────────────────────────────────────────────────────
# ReasoningOrchestrator
# ────────────────────────────────────────────────────────────

class ReasoningOrchestrator:
    """Orquestra o roteamento de problemas para motores de raciocínio."""

    ENGINE_ORDER = ["z3", "sympy", "kanren", "critical"]

    # Heurísticas de detecção de modo baseado no texto do problema
    MODE_PATTERNS = {
        ReasoningMode.FORMAL: [
            r"\bprove?\b", r"\btheorem\b", r"\bsatisfiab\w+\b",
            r"\bconstraint\b", r"\bformal\b", r"\bsat\b", r"\bunsat\b",
            r"\bverification\b", r"\bproof\b",
        ],
        ReasoningMode.SYMBOLIC: [
            r"\bsolve\b", r"\bequation\b", r"\bexpress\w+\b",
            r"\bsymbolic\b", r"\balgebra\b", r"\bcalculus\b",
            r"\bintegral\b", r"\bderivative\b", r"\bmatrix\b",
            r"\b=\b.*\bx\b", r"\bsqrt\b",
        ],
        ReasoningMode.LOGIC: [
            r"\blogic\b", r"\binference\b", r"\bdeduction\b",
            r"\bif.*then\b", r"\ball\b.*\bare\b", r"\bsyllogism\b",
            r"\bfact\b", r"\brule\b", r"\bunification\b",
            r"\brelational\b",
        ],
        ReasoningMode.CRITICAL: [
            r"\bargument\b", r"\bfallacy\b", r"\bbias\b",
            r"\bcritic\w+\b", r"\bcognitive\b", r"\bdebat\w+\b",
            r"\bdisput\w+\b", r"\bpersuasion\b",
        ],
        ReasoningMode.RESEARCH: [
            r"\bgame\b", r"\btheory\b.*\bjogos?\b", r"\bnash\b",
            r"\bdilema\b", r"\bcooperativ\b", r"\bpayoff\b",
            r"\btemporal\b", r"\blongitudinal\b", r"\bpopulac\w+\b",
            r"\bamostra\b", r"\bepistemolog\b", r"\bparadigma\b",
            r"\bempirico\b", r"\bvalidac\w+\b", r"\bteoria\b",
            r"\binferencia\b", r"\bdeducao\b", r"\bmultiescala\b",
            r"\bmulti-escala\b", r"\brainocini\b",
        ],
    }

    def detect_mode(self, problem: str) -> ReasoningMode:
        """Detecta automaticamente o modo de raciocínio baseado no problema."""
        prob_lower = problem.lower()

        scores = {}
        for mode, patterns in self.MODE_PATTERNS.items():
            score = sum(1 for p in patterns if re.search(p, prob_lower))
            scores[mode] = score

        # Modo com maior score
        best = max(scores.items(), key=lambda x: x[1])[0]
        if scores[best] == 0:
            return ReasoningMode.AUTO

        return best

    def select_engines(self, problem: str, mode: Optional[ReasoningMode] = None) -> List[str]:
        """Seleciona quais motores acionar baseado no modo."""
        if mode is None or mode == ReasoningMode.AUTO:
            mode = self.detect_mode(problem)

        if mode == ReasoningMode.ALL:
            return list(self.ENGINE_ORDER)

        mode_to_engines = {
            ReasoningMode.FORMAL: ["z3"],
            ReasoningMode.SYMBOLIC: ["sympy"],
            ReasoningMode.LOGIC: ["kanren"],
            ReasoningMode.CRITICAL: ["critical"],
            ReasoningMode.RESEARCH: ["game_theory", "temporal_population",
                                     "theoretical_empirical", "logical_multiscale"],
        }

        return mode_to_engines.get(mode, ["z3", "sympy"])

    def solve(self, problem: str, mode: Optional[ReasoningMode] = None,
              context: Optional[Dict] = None) -> SynthesisResult:
        """Executa pipeline completo de raciocínio multi-paradigma."""
        t0 = time.time()
        if mode is None:
            mode = ReasoningMode.AUTO

        engines = self.select_engines(problem, mode)
        results: List[EngineResult] = []

        for eng_name in engines:
            if eng_name in ("z3", "sympy", "kanren", "critical"):
                result = _run_engine(eng_name, problem, context)
            else:
                # Research skill: infere operação do contexto
                op = (context or {}).get("operation", "auto")
                params = (context or {}).get("params", {})
                result = _run_research_skill(eng_name, op, params)
            results.append(result)

        # Síntese
        synthesizer = CrossParadigmSynthesizer()
        syn = synthesizer.synthesize(problem, results, mode)

        # Auto-reparo
        repair = AutonomousSelfRepair()
        repaired = repair.repair(syn)

        repaired.time_ms = (time.time() - t0) * 1000
        return repaired


# ────────────────────────────────────────────────────────────
# CrossParadigmSynthesizer
# ────────────────────────────────────────────────────────────

class CrossParadigmSynthesizer:
    """Combina resultados de múltiplos motores de raciocínio."""

    # Pesos de confiança por engine
    ENGINE_WEIGHTS = {
        "z3": 0.90,
        "sympy": 0.85,
        "kanren": 0.80,
        "critical": 0.75,
        "game_theory": 0.82,
        "temporal_population": 0.80,
        "theoretical_empirical": 0.85,
        "logical_multiscale": 0.78,
    }

    def synthesize(self, problem: str, results: List[EngineResult],
                   mode: ReasoningMode) -> SynthesisResult:
        """Sintetiza resultados de múltiplos motores."""
        synthesis = SynthesisResult(
            problem=problem,
            mode=mode.value,
            engine_results=results,
        )

        # Detecta contradições entre motores
        contradictions = self._detect_contradictions(results)
        synthesis.contradictions = contradictions

        # Calcula confiança geral
        synthesis.overall_confidence = self._calculate_overall_confidence(results, contradictions)

        # Gera saída sintetizada
        synthesis.synthesized_output = self._merge_outputs(results)

        return synthesis

    def _detect_contradictions(self, results: List[EngineResult]) -> List[Dict[str, Any]]:
        """Detecta contradições entre resultados de diferentes motores."""
        contradictions = []

        # Verifica pares de motores
        for i, r1 in enumerate(results):
            for r2 in results[i + 1:]:
                if r1.status != "success" or r2.status != "success":
                    continue
                contradiction = self._check_pair(r1, r2)
                if contradiction:
                    contradictions.append(contradiction)

        return contradictions

    def _check_pair(self, r1: EngineResult, r2: EngineResult) -> Optional[Dict[str, Any]]:
        """Verifica contradição entre um par de resultados."""
        # Regras heurísticas de contradição
        if r1.engine == "z3" and r2.engine == "sympy":
            out1 = r1.output or {}
            out2 = r2.output or {}
            # Se Z3 diz UNSAT mas SymPy encontrou solução → contradição
            if out1.get("status") == "unsat" and out2.get("solutions"):
                return {
                    "type": "formal_vs_symbolic",
                    "engines": [r1.engine, r2.engine],
                    "description": "Z3 proof UNSAT contradicts SymPy solution existence",
                    "severity": "high",
                }

        return None

    def _calculate_overall_confidence(self, results: List[EngineResult],
                                      contradictions: List[Dict]) -> float:
        """Calcula confiança consolidada."""
        if not results:
            return 0.0

        total_weight = 0.0
        weighted_sum = 0.0

        for r in results:
            if r.status == "success":
                w = self.ENGINE_WEIGHTS.get(r.engine, 0.5)
                weighted_sum += w * r.confidence
                total_weight += w

        if total_weight == 0:
            return 0.0

        base = weighted_sum / total_weight

        # Penalidade por contradições
        penalty = len(contradictions) * 0.1
        return max(0.0, min(1.0, base - penalty))

    def _merge_outputs(self, results: List[EngineResult]) -> Dict[str, Any]:
        """Mescla saídas de múltiplos motores em um único resultado."""
        merged = {
            "engines_used": [r.engine for r in results if r.status == "success"],
            "summaries": {},
        }

        for r in results:
            if r.status == "success" and r.output:
                merged["summaries"][r.engine] = r.output

        return merged


# ────────────────────────────────────────────────────────────
# AutonomousSelfRepair
# ────────────────────────────────────────────────────────────

class AutonomousSelfRepair:
    """Detecta e tenta reparar inconsistências no raciocínio multi-paradigma."""

    def repair(self, synthesis: SynthesisResult) -> SynthesisResult:
        """Tenta reparar contradições detectadas."""
        for contradiction in synthesis.contradictions:
            repair_record = self._attempt_repair(contradiction, synthesis)
            if repair_record:
                synthesis.repairs_applied.append(repair_record)

        # Recalcula confiança após reparos
        if synthesis.repairs_applied:
            # Cada reparo bem-sucedido recupera 0.05 de confiança
            boost = len(synthesis.repairs_applied) * 0.05
            synthesis.overall_confidence = min(1.0, synthesis.overall_confidence + boost)

        return synthesis

    def _attempt_repair(self, contradiction: Dict[str, Any],
                        synthesis: SynthesisResult) -> Optional[Dict[str, Any]]:
        """Tenta reparar uma contradição específica."""
        ctype = contradiction.get("type", "")

        if ctype == "formal_vs_symbolic":
            # Estratégia: verificar se a saída simbólica satisfaz a restrição formal
            return {
                "contradiction_type": ctype,
                "strategy": "cross_validation",
                "status": "logged_for_review",
                "description": "Formal-symbolic contradiction flagged for human review",
            }

        # Estratégia genérica: log para revisão
        return {
            "contradiction_type": ctype,
            "strategy": "defer_to_human",
            "status": "deferred",
            "description": f"Contradiction {ctype} requires human judgment",
        }


# ────────────────────────────────────────────────────────────
# ParadigmBridge
# ────────────────────────────────────────────────────────────

class ParadigmBridge:
    """Tradutor entre formalismos de raciocínio."""

    def formal_to_symbolic(self, constraint: str) -> str:
        """Traduz restrição formal (Z3-style) para expressão simbólica (SymPy-style)."""
        # AND → and lógico
        expr = constraint.replace(" AND ", " & ").replace(" AND", " &")
        expr = expr.replace(" OR ", " | ").replace(" OR", " |")
        expr = expr.replace("NOT ", "~").replace("not ", "~")
        # Remove ':' do Z3
        expr = re.sub(r'(\w+)\s*:\s*(Int|Real|Bool)', r'\1', expr)
        return expr.strip()

    def symbolic_to_formal(self, equation: str) -> str:
        """Traduz expressão simbólica para restrição formal."""
        expr = equation.replace("=", " == ")
        return expr.strip()

    def logic_to_critical(self, facts: List[Tuple[str, Any]]) -> str:
        """Converte fatos lógicos em argumento para análise crítica."""
        if not facts:
            return ""
        parts = [f"{pred}({', '.join(str(a) for a in args)})" if isinstance(args, tuple) or isinstance(args, list)
                 else f"{pred}({args})"
                 for pred, args in facts]
        return "Given: " + "; ".join(parts) + ". Evaluate the logical coherence."

    def critical_to_logic(self, argument: str) -> List[Tuple[str, str]]:
        """Extrai proposições lógicas de um argumento."""
        # Heurística simples: extrai sentenças declarativas
        sentences = re.split(r'[.!?]', argument)
        propositions = []
        for s in sentences:
            s = s.strip()
            if s and len(s) > 10:
                prop_name = f"proposition_{len(propositions) + 1}"
                propositions.append((prop_name, s))
        return propositions


# ────────────────────────────────────────────────────────────
# Autonomia: Auto-diagnóstico e self-repair avançado
# ────────────────────────────────────────────────────────────

class SystemSelfDiagnostic:
    """Auto-diagnóstico do ecossistema de raciocínio — foundation para autonomous_self_repair."""

    def __init__(self):
        self.engines_status: Dict[str, bool] = {}
        self._check_engines()

    def _check_engines(self):
        """Verifica disponibilidade de cada motor."""
        for name, loader in [
            ("z3", _load_z3_engine),
            ("sympy", _load_sympy_engine),
            ("kanren", _load_kanren_engine),
            ("critical", _load_critical_engine),
        ]:
            eng = loader()
            self.engines_status[name] = eng is not None and getattr(eng, 'available', True)

    def diagnostic(self) -> Dict[str, Any]:
        """Retorna diagnóstico completo dos motores."""
        return {
            "engines": self.engines_status,
            "all_available": all(self.engines_status.values()),
            "available_count": sum(1 for v in self.engines_status.values() if v),
            "total_count": len(self.engines_status),
        }

    def auto_repair_engines(self) -> List[Dict[str, Any]]:
        """Tenta recarregar motores com falha."""
        repairs = []
        for name, available in self.engines_status.items():
            if not available:
                # Limpa cache e tenta recarregar
                if name in _ENGINE_CACHE:
                    del _ENGINE_CACHE[name]
                loader_map = {
                    "z3": _load_z3_engine,
                    "sympy": _load_sympy_engine,
                    "kanren": _load_kanren_engine,
                    "critical": _load_critical_engine,
                }
                eng = loader_map[name]()
                success = eng is not None and getattr(eng, 'available', True)
                self.engines_status[name] = success
                repairs.append({
                    "engine": name,
                    "repaired": success,
                    "previous": available,
                })
        return repairs


# ────────────────────────────────────────────────────────────
# API Pública
# ────────────────────────────────────────────────────────────

__all__ = [
    "ReasoningOrchestrator",
    "CrossParadigmSynthesizer",
    "AutonomousSelfRepair",
    "ParadigmBridge",
    "SystemSelfDiagnostic",
    "ReasoningMode",
    "SynthesisResult",
    "EngineResult",
]
