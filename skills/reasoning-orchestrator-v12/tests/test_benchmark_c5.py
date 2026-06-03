#!/usr/bin/env python
# =====================================================================
# TESTES DE SANIDADE — Benchmark C5 (Integração do Pipeline)
# =====================================================================
# Verifica que o benchmark empírico produz métricas consistentes.
#
# Uso: pytest tests/test_benchmark_c5.py -v
# =====================================================================
import sys, os, time, json
import pytest

# Path
V12_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents")
sys.path.insert(0, V12_PATH)

from full_pipeline import FullPipeline, ProblemProfile, BenchmarkResult


# =====================================================================
# CONFIG
# =====================================================================

REQUIRED_BENCHMARK_KEYS = [
    "total_elapsed_ms", "chain_times_ms", "synthesis_time_ms",
    "speedup_vs_sequential", "chain_pci_scores", "mean_pci",
    "strategy_used", "synthesis_confidence", "chain_count", "final_answer",
]

DOMAIN_STRATEGY_MAP = {
    "code":       "weighted_vote",
    "math":       "weighted_vote",
    "physics":    "weighted_vote",
    "debate":     "debate",
    "controversy":"debate",
    "creative":   "ensemble",
    "exploration":"ensemble",
    "quick":      "best_of",
    "simple":     "best_of",
}

COMPLEXITY_STRATEGY_MAP = {
    "low":      "best_of",
    "medium":   "weighted_vote",
    "high":     "debate",
    "research": "ensemble",
}


# =====================================================================
# FIXTURES
# =====================================================================

@pytest.fixture
def pipeline():
    return FullPipeline()


@pytest.fixture
def sample_problems():
    return {
        "code":      "Implement a binary search tree in Python with O(log n) operations",
        "math":      "Prove that sqrt(2) is irrational using proof by contradiction",
        "debate":    "Should artificial general intelligence be regulated by international treaty?",
        "creative":  "Design a novel approach to renewable energy storage for urban environments",
        "simple":    "What is 2 + 2?",
        "physics":   "Calculate the escape velocity of a rocket from Earth's gravitational field",
    }


# =====================================================================
# B5-T1: W=1 produz speedup ≈ 1.0
# =====================================================================

def test_speedup_w1_near_one():
    """W=1 deve produzir speedup ≈ 1.0 (sem paralelismo)."""
    tasks = [(1.0, i) for i in range(4)]
    from tests.benchmark_c5 import run_benchmark_raw
    result = run_benchmark_raw(tasks, max_workers=1)
    assert result["speedup"] == pytest.approx(1.0, abs=0.2), \
        f"Speedup W=1 esperado ~1.0, obtido {result['speedup']:.3f}"
    assert result["efficiency"] == pytest.approx(1.0, abs=0.2), \
        f"Eficiência W=1 esperada ~1.0, obtida {result['efficiency']:.3f}"


# =====================================================================
# B5-T2: W=2 produz speedup > W=1
# =====================================================================

def test_speedup_w2_greater_than_w1():
    """W=2 deve ter speedup maior que W=1."""
    tasks = [(1.0, i) for i in range(4)]
    from tests.benchmark_c5 import run_benchmark_raw
    r1 = run_benchmark_raw(tasks, max_workers=1)
    r2 = run_benchmark_raw(tasks, max_workers=2)
    assert r2["speedup"] > r1["speedup"], \
        f"Speedup W=2 ({r2['speedup']:.3f}) deve ser > W=1 ({r1['speedup']:.3f})"


# =====================================================================
# B5-T3: W=4 produz speedup > W=2
# =====================================================================

def test_speedup_w4_greater_than_w2():
    """W=4 deve ter speedup maior que W=2."""
    tasks = [(1.0, i) for i in range(4)]
    from tests.benchmark_c5 import run_benchmark_raw
    r2 = run_benchmark_raw(tasks, max_workers=2)
    r4 = run_benchmark_raw(tasks, max_workers=4)
    assert r4["speedup"] > r2["speedup"], \
        f"Speedup W=4 ({r4['speedup']:.3f}) deve ser > W=2 ({r2['speedup']:.3f})"


# =====================================================================
# B5-T4: Eficiência > 0 em todas configurações
# =====================================================================

def test_efficiency_positive():
    """Todas configs devem ter eficiência > 0."""
    tasks = [(1.0, i) for i in range(4)]
    from tests.benchmark_c5 import run_benchmark_raw
    for w in [1, 2, 4]:
        r = run_benchmark_raw(tasks, max_workers=w)
        assert r["efficiency"] > 0, f"Eficiência zero para W={w}"


# =====================================================================
# B5-T5 a B5-T6: Seleção de estratégia
# =====================================================================

def test_strategy_code():
    """Domínio 'code' deve selecionar weighted_vote."""
    pipeline = FullPipeline()
    profile = pipeline.analyze_problem("Write a Python function to sort a list")
    strategy = pipeline.select_strategy(profile)
    assert strategy == "weighted_vote", \
        f"Esperado weighted_vote, obtido {strategy}"


def test_strategy_debate():
    """Domínio 'debate' deve selecionar debate."""
    pipeline = FullPipeline()
    profile = pipeline.analyze_problem("Debate the ethical implications of AI in healthcare")
    strategy = pipeline.select_strategy(profile)
    assert strategy == "debate", \
        f"Esperado debate, obtido {strategy}"


def test_strategy_simple():
    """Domínio 'simple' deve selecionar best_of."""
    pipeline = FullPipeline()
    profile = pipeline.analyze_problem("What is the capital of France?")
    strategy = pipeline.select_strategy(profile)
    assert strategy == "best_of", \
        f"Esperado best_of, obtido {strategy}"


def test_strategy_research():
    """Complexidade 'research' deve selecionar ensemble."""
    pipeline = FullPipeline()
    profile = ProblemProfile(complexity="research", domain="physics", num_chains=4)
    strategy = pipeline.select_strategy(profile)
    assert strategy == "ensemble", \
        f"Esperado ensemble, obtido {strategy}"


# =====================================================================
# B5-T7: Resultados têm estrutura correta
# =====================================================================

def test_benchmark_result_structure(pipeline):
    """Resultado do benchmark deve ter todos os campos obrigatórios."""
    result = pipeline.run_with_benchmark("Prove that the square root of 2 is irrational")
    for key in REQUIRED_BENCHMARK_KEYS:
        assert hasattr(result, key), f"Campo obrigatório ausente: {key}"


# =====================================================================
# B5-T8: Valores em faixa esperada
# =====================================================================

def test_benchmark_values_in_range(pipeline):
    """Métricas do benchmark devem estar em faixas plausíveis."""
    result = pipeline.run_with_benchmark("What is the derivative of x^2?")
    assert result.total_elapsed_ms > 0, "Tempo total deve ser > 0"
    assert result.speedup_vs_sequential > 0, "Speedup deve ser > 0"
    if result.chain_count > 1:
        assert result.speedup_vs_sequential >= 0.5, \
            f"Speedup muito baixo: {result.speedup_vs_sequential:.3f}"
    assert 0 <= result.mean_pci <= 100, \
        f"PCI fora de [0,100]: {result.mean_pci:.3f}"
    assert 0 <= result.synthesis_confidence <= 1, \
        f"Confiança fora de [0,1]: {result.synthesis_confidence:.3f}"


# =====================================================================
# B5-T9: Seleção consistente com heurísticas
# =====================================================================

def test_domain_strategy_consistency():
    """Todos os domínios conhecidos devem mapear para estratégias válidas."""
    from full_pipeline import STRATEGY_RULES
    valid_strategies = {"weighted_vote", "debate", "ensemble", "best_of"}
    for domain, strategy in STRATEGY_RULES.items():
        assert strategy in valid_strategies, \
            f"Domínio {domain} mapeia para estratégia inválida: {strategy}"


# =====================================================================
# B5-T10: Todos os profiles geram estratégias
# =====================================================================

def test_all_profiles_produce_strategies(pipeline):
    """Qualquer ProblemProfile deve produzir uma estratégia."""
    domains = ["code", "math", "physics", "debate", "creative", "simple", "general"]
    complexities = ["low", "medium", "high", "research"]
    for domain in domains:
        for complexity in complexities:
            profile = ProblemProfile(complexity=complexity, domain=domain)
            strategy = pipeline.select_strategy(profile)
            assert strategy in {"weighted_vote", "debate", "ensemble", "best_of"}, \
                f"Estratégia inválida para {domain}/{complexity}: {strategy}"
