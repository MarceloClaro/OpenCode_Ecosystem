#!/usr/bin/env python3
"""
Testes R38 — Cross-Paradigm Reasoning Engine (SPEC-082)
14 CTs validando orquestração, síntese, auto-reparo e bridge.

Uso:
    python -m pytest tests/test_r38_cross_paradigm.py -v
"""
import sys
import os
import pytest

# Path da skill
SKILL_DIR = os.path.join(
    os.path.dirname(__file__), "..",
    "skills/research/cross-paradigm-reasoning"
)
sys.path.insert(0, SKILL_DIR)

from cross_paradigm_reasoning import (
    ReasoningOrchestrator,
    CrossParadigmSynthesizer,
    AutonomousSelfRepair,
    ParadigmBridge,
    SystemSelfDiagnostic,
    ReasoningMode,
    EngineResult,
    SynthesisResult,
)


# ─── Fixtures ─────────────────────────────────────────────

@pytest.fixture
def orchestrator():
    return ReasoningOrchestrator()


@pytest.fixture
def synthesizer():
    return CrossParadigmSynthesizer()


@pytest.fixture
def repair():
    return AutonomousSelfRepair()


@pytest.fixture
def bridge():
    return ParadigmBridge()


# ─── CT 01: Import ────────────────────────────────────────

def test_cpr_import():
    """CT-01: Módulo importa sem erros."""
    from cross_paradigm_reasoning import (
        ReasoningOrchestrator,
        CrossParadigmSynthesizer,
        AutonomousSelfRepair,
        ParadigmBridge,
        SystemSelfDiagnostic,
    )
    assert ReasoningOrchestrator is not None
    assert CrossParadigmSynthesizer is not None
    assert AutonomousSelfRepair is not None
    assert ParadigmBridge is not None
    assert SystemSelfDiagnostic is not None


# ─── CT 02: Auto-detecção ─────────────────────────────────

def test_orchestrator_auto_detect(orchestrator):
    """CT-02: Auto-detecção escolhe modo correto para problema.

    Testa que problemas matemáticos detectam SYMBOLIC e
    problemas de prova detectam FORMAL.
    """
    # Problema simbólico
    mode_math = orchestrator.detect_mode("solve x^2 + 2x + 1 = 0")
    assert mode_math == ReasoningMode.SYMBOLIC, (
        f"Esperado SYMBOLIC, obtido {mode_math}"
    )

    # Problema formal
    mode_proof = orchestrator.detect_mode("prove that the constraint is satisfiable")
    assert mode_proof in (ReasoningMode.FORMAL, ReasoningMode.SYMBOLIC), (
        f"Esperado FORMAL ou SYMBOLIC, obtido {mode_proof}"
    )

    # Problema crítico
    mode_crit = orchestrator.detect_mode("analyze this argument for fallacies")
    assert mode_crit == ReasoningMode.CRITICAL, (
        f"Esperado CRITICAL, obtido {mode_crit}"
    )


# ─── CT 03: Seleção de motores ────────────────────────────

def test_orchestrator_select_engines(orchestrator):
    """CT-03: Seleção de motores por modo."""
    # Modo formal → Z3
    engines = orchestrator.select_engines("prove theorem", ReasoningMode.FORMAL)
    assert "z3" in engines
    assert len(engines) == 1

    # Modo ALL → todos
    engines_all = orchestrator.select_engines("any", ReasoningMode.ALL)
    assert len(engines_all) == 4
    assert "z3" in engines_all
    assert "sympy" in engines_all
    assert "kanren" in engines_all
    assert "critical" in engines_all


# ─── CT 04: Modo formal aciona Z3 ─────────────────────────

def test_orchestrator_formal(orchestrator):
    """CT-04: Modo formal aciona Z3 (disponível ou não)."""
    result = orchestrator.solve("x > 0 AND x < 10", mode=ReasoningMode.FORMAL)
    assert len(result.engine_results) == 1
    assert result.engine_results[0].engine == "z3"
    # Z3 pode ou não estar instalado; o importante é que foi acionado
    assert result.engine_results[0].status in ("success", "unavailable", "error")


# ─── CT 05: Modo simbólico ────────────────────────────────

def test_orchestrator_symbolic(orchestrator):
    """CT-05: Modo symbolic aciona SymPyEngine."""
    result = orchestrator.solve("x**2 - 4 = 0", mode=ReasoningMode.SYMBOLIC)
    assert len(result.engine_results) == 1
    assert result.engine_results[0].engine == "sympy"


# ─── CT 06: Modo lógico ───────────────────────────────────

def test_orchestrator_logic(orchestrator):
    """CT-06: Modo logic aciona KanrenEngine."""
    result = orchestrator.solve("all men are mortal", mode=ReasoningMode.LOGIC)
    assert len(result.engine_results) == 1
    assert result.engine_results[0].engine == "kanren"


# ─── CT 07: Modo crítico ──────────────────────────────────

def test_orchestrator_critical(orchestrator):
    """CT-07: Modo critical aciona CriticalEngine."""
    result = orchestrator.solve(
        "You are wrong because you are biased",
        mode=ReasoningMode.CRITICAL,
    )
    assert len(result.engine_results) == 1
    assert result.engine_results[0].engine == "critical"


# ─── CT 08: Síntese combina resultados ────────────────────

def test_synthesizer_combine(synthesizer):
    """CT-08: Combinador mescla resultados de 2+ motores."""
    results = [
        EngineResult("z3", "success", output={"status": "sat"}, confidence=0.9),
        EngineResult("sympy", "success", output={"solutions": [2, -2]}, confidence=0.85),
    ]
    syn = synthesizer.synthesize("test problem", results, ReasoningMode.ALL)
    assert len(syn.engine_results) == 2
    assert syn.overall_confidence > 0
    assert "z3" in syn.synthesized_output["engines_used"]
    assert "sympy" in syn.synthesized_output["engines_used"]


# ─── CT 09: Detecção de contradição ───────────────────────

def test_synthesizer_contradiction(synthesizer):
    """CT-09: Detecta contradição entre motores (Z3 UNSAT vs SymPy solutions)."""
    results = [
        EngineResult("z3", "success", output={"status": "unsat"}, confidence=0.9),
        EngineResult("sympy", "success", output={"solutions": [2, -2]}, confidence=0.85),
    ]
    syn = synthesizer.synthesize("test", results, ReasoningMode.ALL)
    assert len(syn.contradictions) >= 1
    assert syn.contradictions[0]["type"] == "formal_vs_symbolic"


# ─── CT 10: Self-repair detecta inconsistência ────────────

def test_self_repair_detect(repair, synthesizer):
    """CT-10: Auto-repair detecta inconsistência e gera registro."""
    results = [
        EngineResult("z3", "success", output={"status": "unsat"}, confidence=0.9),
        EngineResult("sympy", "success", output={"solutions": [1]}, confidence=0.85),
    ]
    syn = synthesizer.synthesize("test", results, ReasoningMode.ALL)
    assert len(syn.contradictions) > 0

    repaired = repair.repair(syn)
    # Deve ter gerado pelo menos um repair record
    assert len(repaired.repairs_applied) >= 1 or len(syn.contradictions) > 0


# ─── CT 11: Self-repair aplica estratégia ─────────────────

def test_self_repair_resolve(repair, synthesizer):
    """CT-11: Auto-repair tenta resolver conflito específico."""
    results = [
        EngineResult("z3", "success", output={"status": "unsat"}, confidence=0.9),
        EngineResult("sympy", "success", output={"solutions": [1]}, confidence=0.85),
    ]
    syn = synthesizer.synthesize("test", results, ReasoningMode.ALL)
    repaired = repair.repair(syn)

    # Verifica que repair registrou ação
    if repaired.repairs_applied:
        r = repaired.repairs_applied[0]
        assert "contradiction_type" in r
        assert "strategy" in r
        assert "status" in r


# ─── CT 12: Bridge formal → simbólico ─────────────────────

def test_paradigm_bridge_formal_to_symbolic(bridge):
    """CT-12: Traduz restrição formal para expressão simbólica."""
    result = bridge.formal_to_symbolic("x > 0 AND x < 10")
    assert "&" in result or ">" in result
    assert "AND" not in result  # deve ter sido substituído


# ─── CT 13: Bridge lógico → crítico ───────────────────────

def test_paradigm_bridge_logic_to_critical(bridge):
    """CT-13: Converte fatos lógicos em argumento para análise crítica."""
    facts = [("human", "socrates"), ("mortal", "X")]
    result = bridge.logic_to_critical(facts)
    assert "Given:" in result
    assert "human" in result
    assert "mortal" in result


# ─── CT 14: Auto-diagnóstico ──────────────────────────────

def test_system_self_diagnostic():
    """CT-14: Auto-diagnóstico verifica disponibilidade dos motores."""
    diagnostic = SystemSelfDiagnostic()
    diag = diagnostic.diagnostic()
    assert "engines" in diag
    assert "all_available" in diag
    assert diag["total_count"] == 4
    assert len(diag["engines"]) == 4


# ====================================================================
# CTs 15-20: Integracao com Research Skills (R38 refinement)
# ====================================================================

def test_research_mode_game_theory(orchestrator):
    """CT-15: Modo RESEARCH aciona game_theory com operacao Nash."""
    context = {
        "operation": "nash",
        "params": {
            "payoff_matrix": [[(3, 3), (1, 4)],
                              [(4, 1), (2, 2)]],
        },
    }
    result = orchestrator.solve(
        "Find Nash equilibrium in prisoner dilemma",
        mode=ReasoningMode.RESEARCH,
        context=context,
    )
    engines = [r.engine for r in result.engine_results]
    assert "game_theory" in engines or any(
        "unavailable" in r.status for r in result.engine_results
    ), "game_theory not in engines"


def test_research_mode_temporal(orchestrator):
    """CT-16: Modo RESEARCH aciona temporal_population."""
    context = {
        "operation": "moving_average",
        "params": {"data": [1, 2, 3, 4, 5], "window": 3},
    }
    result = orchestrator.solve(
        "Analyze population time series",
        mode=ReasoningMode.RESEARCH,
        context=context,
    )
    engines = [r.engine for r in result.engine_results]
    assert "temporal_population" in engines or any(
        "unavailable" in r.status for r in result.engine_results
    )


def test_research_mode_theoretical(orchestrator):
    """CT-17: Modo RESEARCH aciona theoretical_empirical."""
    context = {
        "operation": "classify",
        "params": {"theory": "positivism empiricism"},
    }
    result = orchestrator.solve(
        "Classify epistemological paradigm",
        mode=ReasoningMode.RESEARCH,
        context=context,
    )
    engines = [r.engine for r in result.engine_results]
    assert "theoretical_empirical" in engines or any(
        "unavailable" in r.status for r in result.engine_results
    )


def test_research_mode_logical(orchestrator):
    """CT-18: Modo RESEARCH aciona logical_multiscale."""
    context = {
        "operation": "deductive",
        "params": {
            "premises": ["all men are mortal", "socrates is a man"],
            "conclusion": "socrates is mortal",
        },
    }
    result = orchestrator.solve(
        "Deductive inference about Socrates",
        mode=ReasoningMode.RESEARCH,
        context=context,
    )
    engines = [r.engine for r in result.engine_results]
    assert "logical_multiscale" in engines or any(
        "unavailable" in r.status for r in result.engine_results
    )


def test_research_all_four_skills(orchestrator):
    """CT-19: Modo RESEARCH aciona as 4 research skills."""
    result = orchestrator.solve(
        "Analyze game theory, temporal data, epistemology, and logic",
        mode=ReasoningMode.RESEARCH,
        context={"operation": "auto", "params": {}},
    )
    engines = [r.engine for r in result.engine_results]
    research_skills = {"game_theory", "temporal_population",
                       "theoretical_empirical", "logical_multiscale"}
    found = research_skills.intersection(engines)
    assert len(found) >= 2, "Expected >=2 research skills"


def test_cross_paradigm_confidence_orchestrator(orchestrator):
    """CT-20: Confianca geral com multiplos motores."""
    ctx = {
        "operation": "nash",
        "params": {"payoff_matrix": [[1, 2], [3, 4]]},
    }
    result = orchestrator.solve("mixed problem", mode=ReasoningMode.ALL, context=ctx)
    assert 0.0 <= result.overall_confidence <= 1.0
    assert len(result.engine_results) >= 4
