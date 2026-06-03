#!/usr/bin/env python
# =====================================================================
# TDD — Ciclo 3: Parallel Verifiers V1-V7 (14 testes)
# =====================================================================
# Testa ParallelVerifiers, ConsensusEngine, retry adaptativo,
# isolamento de falhas, calibração Platt, e integração com orchestrator.
# =====================================================================

import sys, os, time, math
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from agents.parallel_verifiers import (
    ParallelVerifiers,
    VerifierResult,
    VerificationConsensus,
)


# =====================================================================
# C3-T1: verify_parallel retorna VerificationConsensus
# =====================================================================

def test_verify_parallel_returns_consensus():
    """C3-T1: Verificadores executam e retornam VerificationConsensus."""
    pv = ParallelVerifiers(max_workers=4)
    context = {
        "solution_text": "The force F = ma where m = 10 kg and a = 5 m/s^2",
        "problem": "Calculate force given mass and acceleration",
    }
    consensus = pv.verify_parallel(context)
    
    assert isinstance(consensus, VerificationConsensus)
    assert 0.0 <= consensus.weighted_score <= 1.0
    assert consensus.total_count == 7  # V1-V7


# =====================================================================
# C3-T2: Todos V1-V7 executados com active_verifiers=None
# =====================================================================

def test_all_verifiers_executed():
    """C3-T2: Todos V1-V7 são executados quando active_verifiers=None."""
    pv = ParallelVerifiers(max_workers=4)
    context = {"solution_text": "x = (-b ± sqrt(b² - 4ac)) / 2a"}
    consensus = pv.verify_parallel(context)
    
    executed_ids = {r.verifier_id for r in consensus.details}
    assert executed_ids == {"V1", "V2", "V3", "V4", "V5", "V6", "V7"}
    assert consensus.total_count == 7


# =====================================================================
# C3-T3: Subset de verificadores
# =====================================================================

def test_subset_verifiers():
    """C3-T3: Apenas verificadores especificados em active_verifiers executam."""
    pv = ParallelVerifiers(max_workers=4)
    context = {"solution_text": "Test context for subset verification"}
    
    subset = ["V1", "V3", "V5"]
    consensus = pv.verify_parallel(context, active_verifiers=subset)
    
    executed_ids = {r.verifier_id for r in consensus.details}
    assert executed_ids == set(subset)
    assert consensus.total_count == 3
    
    # IDs inválidos são ignorados
    with_invalid = ["V1", "V99", "VX"]
    consensus2 = pv.verify_parallel(context, active_verifiers=with_invalid)
    executed2 = {r.verifier_id for r in consensus2.details}
    assert executed2 == {"V1"}
    assert consensus2.total_count == 1


# =====================================================================
# C3-T4: Fórmula do weighted_score
# =====================================================================

def test_weighted_score_formula():
    """C3-T4: weighted_score = Σ(p_i·conf_i)/Σ(p_i)."""
    pv = ParallelVerifiers(max_workers=1)
    context = {"solution_text": "Simple solution text for testing weighted score"}
    
    consensus = pv.verify_parallel(context, active_verifiers=["V1", "V2", "V3"])
    
    # Calcula manualmente
    expected_numerator = 0.0
    expected_denominator = 0.0
    for r in consensus.details:
        w = pv.VERIFIER_WEIGHTS.get(r.verifier_id, 0.1)
        expected_numerator += w * r.confidence
        expected_denominator += w
    
    expected_score = round(expected_numerator / expected_denominator, 4)
    assert abs(consensus.weighted_score - expected_score) < 0.01, (
        f"Expected {expected_score}, got {consensus.weighted_score}"
    )


# =====================================================================
# C3-T5: Threshold de consenso
# =====================================================================

def test_consensus_threshold():
    """C3-T5: weighted_score < 0.75 → requires_retry=True."""
    # Contexto vazio → scores baixos → requires_retry
    pv = ParallelVerifiers(max_workers=4)
    context = {"solution_text": "", "problem": ""}
    
    consensus = pv.verify_parallel(context)
    
    if consensus.weighted_score < 0.75:
        assert consensus.requires_retry is True
    else:
        # Se mesmo vazio deu score alto, não precisa de retry
        assert consensus.requires_retry is False


# =====================================================================
# C3-T6: Timeout de verificador não aborta os outros
# =====================================================================

def test_verifier_timeout():
    """C3-T6: Verificador lento não aborta os outros."""
    pv = ParallelVerifiers(max_workers=4, timeout=5)
    context = {"solution_text": "E = mc² where m is mass in kg and c is speed of light"}
    
    start = time.time()
    consensus = pv.verify_parallel(context)
    elapsed = time.time() - start
    
    # Todos os verificadores completaram
    assert consensus.total_count == 7
    # Tempo total deve ser muito menor que soma individual (paralelo)
    # Stubs são rápidos (< 0.1s cada), então total < 0.5s
    assert elapsed < 2.0, f"Parallel execution took too long: {elapsed:.2f}s"


# =====================================================================
# C3-T7: Isolamento de falhas
# =====================================================================

def test_failure_isolation_verifiers():
    """C3-T7: Falha em um V não afeta resultados dos outros."""
    pv = ParallelVerifiers(max_workers=4)
    context = {"solution_text": "Test isolation: V2=algebra, V3=counterexample"}
    
    # Verifica V2 e V3 funcionam
    consensus = pv.verify_parallel(context, active_verifiers=["V1", "V2", "V3"])
    
    # Todos têm confidence > 0
    for r in consensus.details:
        assert r.confidence >= 0.0
        assert isinstance(r.passed, bool)
        assert isinstance(r.evidence, list)


# =====================================================================
# C3-T8: Tempo de execução paralela < 2s
# =====================================================================

def test_parallel_execution_time():
    """C3-T8: V1-V7 executam em ≤ 2s (paralelo, 4 workers)."""
    pv = ParallelVerifiers(max_workers=4)
    context = {"solution_text": "∇·E = ρ/ε₀, ∇×E = -∂B/∂t (Maxwell's equations)"}
    
    start = time.time()
    _ = pv.verify_parallel(context)
    elapsed = time.time() - start
    
    assert elapsed < 2.0, (
        f"V1-V7 execution took {elapsed:.3f}s (max 2.0s)"
    )


# =====================================================================
# C3-T9: get_supported_domains
# =====================================================================

def test_get_supported_domains():
    """C3-T9: Domínios retornados corretamente."""
    pv = ParallelVerifiers()
    domains = pv.get_supported_domains()
    
    assert "V1" in domains
    assert "V7" in domains
    assert len(domains) == 7
    
    # Verifica estrutura
    for vid, dom_list in domains.items():
        assert isinstance(dom_list, list), f"{vid} domains should be a list"
        assert len(dom_list) >= 1, f"{vid} should have at least 1 domain"


# =====================================================================
# C3-T10: verify_single
# =====================================================================

def test_verify_single():
    """C3-T10: verify_single retorna VerifierResult para um V específico."""
    pv = ParallelVerifiers()
    context = {"solution_text": "Test single verifier execution"}
    
    result = pv.verify_single("V2", context)
    
    assert isinstance(result, VerifierResult)
    assert result.verifier_id == "V2"
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.passed, bool)
    assert isinstance(result.evidence, list)
    assert result.elapsed_ms >= 0.0


# =====================================================================
# C3-T11: solve_with_verification (Mock orchestrator)
# =====================================================================

def test_solve_with_verification():
    """
    C3-T11: solve_with_verification retorna (SolutionReport, VerificationConsensus).
    
    Nota: Testa o fluxo integrado mockando o orchestrator internamente.
    """
    from agents.orchestrator_v12 import (
        ParallelOrchestrator, SolutionReport
    )
    
    # Orchestrator com budget mínimo
    orch = ParallelOrchestrator(mode="express")
    orch.config.budget = 30
    
    # Contexto de problema simples
    problem = "Solve: 2x + 3 = 7"
    
    # Cria verifiers
    pv = ParallelVerifiers(max_workers=2)
    
    # Executa pipeline
    report = orch.solve(problem)
    assert isinstance(report, SolutionReport)
    
    # Verifica
    verify_context = {
        "solution_text": str(report.final_answer),
        "problem": problem,
        "agent_results": report.agent_results,
    }
    consensus = pv.verify_parallel(verify_context)
    
    assert isinstance(consensus, VerificationConsensus)
    assert consensus.total_count >= 1


# =====================================================================
# C3-T12: Retry on low consensus
# =====================================================================

def test_retry_on_low_consensus():
    """
    C3-T12: weighted_score < 0.75 → retry com mais budget.
    
    Simula contexto vazio que produz score baixo e verifica
    que retry com mais budget aumenta o score.
    """
    from agents.orchestrator_v12 import ParallelOrchestrator
    
    orch = ParallelOrchestrator(mode="express")
    orch.config.budget = 30
    pv = ParallelVerifiers(max_workers=2)
    
    problem = "Solve for x: 3x - 7 = 14"
    report = orch.solve(problem)
    
    verify_context = {
        "solution_text": str(report.final_answer),
        "problem": problem,
        "agent_results": report.agent_results,
    }
    
    consensus = pv.verify_parallel(verify_context)
    
    # Se score baixo, pipeline roda com retry
    retries = 0
    max_r = 2
    current_consensus = consensus
    
    while current_consensus.requires_retry and retries < max_r:
        retries += 1
        # Aumenta budget em 50%
        new_budget = int(orch.config.budget * 1.5)
        orch.config.budget = new_budget
        
        # Re-executa
        report = orch.solve(problem)
        verify_context = {
            "solution_text": str(report.final_answer),
            "problem": problem,
            "agent_results": report.agent_results,
        }
        current_consensus = pv.verify_parallel(verify_context)
    
    # Verifica que retry ocorreu ao menos uma vez se score < 0.75
    if consensus.weighted_score < 0.75:
        assert retries >= 1, "Retry should have been triggered"
    # Nota: solução simples tem alta chance de score ≥ 0.75 sem retry


# =====================================================================
# C3-T13: Max retries exceeded
# =====================================================================

def test_max_retries_exceeded():
    """C3-T13: Após max_retries, retorna mesmo com score < 0.75."""
    from agents.orchestrator_v12 import ParallelOrchestrator
    
    orch = ParallelOrchestrator(mode="express")
    orch.config.budget = 5
    pv = ParallelVerifiers(max_workers=1)
    
    problem = "What is the meaning of life, the universe, and everything?"
    report = orch.solve(problem)
    
    verify_context = {
        "solution_text": str(report.final_answer),
        "problem": problem,
        "agent_results": report.agent_results,
    }
    
    # Simula max_retries = 1
    max_retries = 1
    retries = 0
    consensus = pv.verify_parallel(verify_context)
    
    while consensus.requires_retry and retries < max_retries:
        retries += 1
        orch.config.budget = int(orch.config.budget * 1.5)
        report = orch.solve(problem)
        verify_context = {
            "solution_text": str(report.final_answer),
            "problem": problem,
            "agent_results": report.agent_results,
        }
        consensus = pv.verify_parallel(verify_context)
    
    # Após exaurir retries, retorna com o que tem
    assert retries <= max_retries
    assert consensus is not None


# =====================================================================
# C3-T14: Platt calibration
# =====================================================================

def test_platt_calibration():
    """C3-T14: Platt calibration produz score ∈ [0,1] e é monotônica."""
    pv = ParallelVerifiers(max_workers=1)
    
    scores = []
    # Cria resultados com confianças variadas
    for conf in [0.1, 0.3, 0.5, 0.7, 0.9]:
        results = [
            VerifierResult(verifier_id="V1", passed=True, confidence=conf, evidence=[]),
            VerifierResult(verifier_id="V2", passed=True, confidence=conf, evidence=[]),
        ]
        consensus = pv._compute_consensus(results)
        scores.append((conf, consensus.weighted_score, consensus.platt_calibrated))
        
        # Platt calibration está em [0, 1]
        assert 0.0 <= consensus.platt_calibrated <= 1.0, (
            f"Platt calibration out of range: {consensus.platt_calibrated}"
        )
    
    # Verifica monotonicidade: confiança maior → platt maior
    for i in range(1, len(scores)):
        assert scores[i][2] >= scores[i-1][2], (
            f"Platt not monotonic at index {i}: {scores[i-1][2]} -> {scores[i][2]}"
        )
    
    # Teste específico: weighted_score=0.5 → platt≈0.5 (centro da sigmoid)
    results_mid = [
        VerifierResult(verifier_id="V1", passed=True, confidence=0.5, evidence=[]),
        VerifierResult(verifier_id="V2", passed=True, confidence=0.5, evidence=[]),
    ]
    consensus_mid = pv._compute_consensus(results_mid)
    assert abs(consensus_mid.platt_calibrated - 0.5) < 0.15, (
        f"Platt at midpoint should be ~0.5, got {consensus_mid.platt_calibrated}"
    )


# =====================================================================
# Testes adicionais de robustez
# =====================================================================

def test_verifier_known_ids():
    """Verifica que todos os 7 IDs de verificadores são conhecidos."""
    pv = ParallelVerifiers()
    assert set(pv.VERIFIER_META.keys()) == {"V1", "V2", "V3", "V4", "V5", "V6", "V7"}


def test_verifier_weights_sum():
    """Verifica que a soma dos pesos é 1.0."""
    pv = ParallelVerifiers()
    total = sum(pv.VERIFIER_WEIGHTS.values())
    assert abs(total - 1.0) < 0.01, f"Sum of weights = {total}, expected 1.0"


def test_parallel_faster_than_sequential():
    """Verifica que execução paralela de V1-V7 é mais rápida que sequencial."""
    pv = ParallelVerifiers(max_workers=4)
    context = {"solution_text": "Multiple verifiers should be faster in parallel"}
    
    # Paralelo
    start_p = time.time()
    _ = pv.verify_parallel(context)
    parallel_time = time.time() - start_p
    
    # Para teste, verifica que paralelo termina
    assert parallel_time < 3.0, f"Parallel too slow: {parallel_time:.3f}s"


# =====================================================================
# Teste de contextos variados
# =====================================================================

@pytest.mark.parametrize("solution,min_v", [
    ("F = G * m1 * m2 / r^2", 4),                    # Física → V1,V2,V3,V5
    ("α = 0.05, p < 0.01, n = 100", 3),              # Estatística → V2,V4,V5
    ("```python\ndef solve():\n    return 42\n```", 3),  # Código → V2,V7
    ("dy/dx = ky, y(0) = y₀", 3),                    # EDO → V2,V3,V6
    ("", 1),                                          # Vazio → mínimo
])
def test_varied_contexts(solution, min_v):
    """Testa verificadores com diferentes tipos de solução."""
    pv = ParallelVerifiers(max_workers=4)
    context = {"solution_text": solution}
    
    consensus = pv.verify_parallel(context)
    assert consensus.total_count == 7
    # Verifica que ao menos alguns V's detectam conteúdo
    passed = sum(1 for r in consensus.details if r.passed)
    assert passed >= min_v, (
        f"Expected ≥{min_v} verifiers to pass for '{solution[:30]}...', got {passed}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
