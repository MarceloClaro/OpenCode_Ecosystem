#!/usr/bin/env python
# =====================================================================
# TESTES CICLO 5 — Pipeline Integration (14 test IDs / 21 métodos)
# =====================================================================
# C5-T1  a  C5-T5:  Strategy selection rules
# C5-T6:           analyze_problem detects keywords
# C5-T7  a  C5-T9:  Pipeline execution (mocked)
# C5-T10 a C5-T11: Robustness tests
# C5-T12:          Different profiles generate different strategies
# C5-T13:          Scalability (1, 4 chains)
# C5-T14:          Sanity (result has non-empty answer)
# =====================================================================

import sys, os, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "agents"))

from unittest.mock import patch, MagicMock
import unittest

from full_pipeline import (
    FullPipeline,
    ProblemProfile,
    FullPipelineResult,
    BenchmarkResult,
    STRATEGY_RULES,
    COMPLEXITY_MAP,
)
from parallel_chain import ChainResult


# -------------------------------------------------------------------
# HELPERS
# -------------------------------------------------------------------

def make_chain(
    chain_id: int,
    mode: str = "standard",
    budget: int = 60,
    pci: float = 50.0,
    elapsed: float = 100.0,
    text: str = "Solution A",
    error: str | None = None,
) -> ChainResult:
    """Cria ChainResult fake para testes."""
    return ChainResult(
        chain_id=chain_id,
        mode=mode,
        budget=budget,
        solution_text=text,
        pci_score=pci,
        elapsed_ms=elapsed,
        num_agents=4,
        error=error,
    )


# ===================================================================
# C5-T1 a C5-T5: Strategy Selection Rules
# ===================================================================

class TestC5T1_T5_StrategySelection(unittest.TestCase):
    """Seleção de estratégia baseada em regras de domínio e complexidade."""

    def test_c5t1_domain_math_selects_weighted_vote(self):
        """C5-T1: Profile domínio 'math' → weighted_vote"""
        p = ProblemProfile(domain="math")
        fp = FullPipeline(profile=p)
        strategy = fp.select_strategy()
        self.assertEqual(strategy, "weighted_vote")

    def test_c5t2_domain_debate_selects_debate(self):
        """C5-T2: Profile domínio 'debate' → debate"""
        p = ProblemProfile(domain="debate")
        fp = FullPipeline(profile=p)
        strategy = fp.select_strategy()
        self.assertEqual(strategy, "debate")

    def test_c5t3_complexity_low_selects_best_of(self):
        """C5-T3: Profile complexidade 'low' → best_of"""
        p = ProblemProfile(complexity="low")
        fp = FullPipeline(profile=p)
        strategy = fp.select_strategy()
        self.assertEqual(strategy, "best_of")

    def test_c5t4_complexity_research_selects_ensemble(self):
        """C5-T4: Profile complexidade 'research' → ensemble"""
        p = ProblemProfile(complexity="research")
        fp = FullPipeline(profile=p)
        strategy = fp.select_strategy()
        self.assertEqual(strategy, "ensemble")

    def test_c5t5_default_profile_selects_weighted_vote(self):
        """C5-T5: Profile default → weighted_vote (complexity=medium)"""
        p = ProblemProfile()
        fp = FullPipeline(profile=p)
        strategy = fp.select_strategy()
        self.assertEqual(strategy, "weighted_vote")


# ===================================================================
# C5-T6: analyze_problem
# ===================================================================

class TestC5T6_AnalyzeProblem(unittest.TestCase):
    """analyze_problem detecta keywords e complexidade."""

    def test_detects_math_keywords(self):
        fp = FullPipeline()
        profile = fp.analyze_problem("Solve the equation x^2 = 4")
        self.assertEqual(profile.domain, "math")

    def test_detects_code_keywords(self):
        fp = FullPipeline()
        profile = fp.analyze_problem("Write a Python function to sort a list")
        self.assertEqual(profile.domain, "code")

    def test_detects_debate_keywords(self):
        fp = FullPipeline()
        profile = fp.analyze_problem("Debate: pros and cons of AI regulation")
        self.assertEqual(profile.domain, "debate")

    def test_complexity_short_is_low(self):
        fp = FullPipeline()
        profile = fp.analyze_problem("What is 2+2?")
        self.assertEqual(profile.complexity, "low")

    def test_complexity_medium_range(self):
        fp = FullPipeline()
        profile = fp.analyze_problem("This is a medium length problem with enough words to check.")
        # 14 words → medium (< 30)
        self.assertEqual(profile.complexity, "medium")

    def test_complexity_long_is_research(self):
        long_problem = "Analyze the impact of " + "A " * 60 + "and research implications"
        fp = FullPipeline()
        profile = fp.analyze_problem(long_problem)
        self.assertEqual(profile.complexity, "research")


# ===================================================================
# C5-T7 a C5-T9: Pipeline Execution (mocked ParallelChain)
# ===================================================================

class TestC5T7_T9_PipelineExecution(unittest.TestCase):
    """Execução do pipeline completo com ParallelChain mockado."""

    def setUp(self):
        self.fake_chains = [
            make_chain(1, "express",  30,  45.0,  50,   "Math solution A"),
            make_chain(2, "standard", 60,  55.0,  100,  "Math solution B"),
            make_chain(3, "magnum",   100, 65.0,  200,  "Math solution C"),
            make_chain(4, "research", 200, 75.0,  400,  "Math solution D"),
        ]

    @patch("full_pipeline.ParallelChain.run_chains")
    def test_c5t7_run_returns_FullPipelineResult(self, mock_run):
        """C5-T7: FullPipeline.run() → FullPipelineResult com answer."""
        mock_run.return_value = self.fake_chains

        fp = FullPipeline()
        result = fp.run("Solve 2x + 3 = 7")

        self.assertIsInstance(result, FullPipelineResult)
        self.assertIsNotNone(result.answer)
        self.assertGreater(len(result.answer), 0)
        self.assertIn(result.strategy, ["weighted_vote", "debate", "ensemble", "best_of"])
        self.assertIsInstance(result.total_elapsed_ms, float)

    @patch("full_pipeline.ParallelChain.run_chains")
    def test_c5t8_run_with_benchmark_returns_BenchmarkResult(self, mock_run):
        """C5-T8: run_with_benchmark() → BenchmarkResult com speedup."""
        mock_run.return_value = self.fake_chains

        fp = FullPipeline()
        result = fp.run_with_benchmark("Solve 2x + 3 = 7")

        self.assertIsInstance(result, BenchmarkResult)
        self.assertIsInstance(result.speedup_vs_sequential, float)
        self.assertIsInstance(result.chain_times_ms, list)
        self.assertEqual(len(result.chain_times_ms), 4)
        self.assertIsInstance(result.chain_pci_scores, list)
        self.assertEqual(len(result.chain_pci_scores), 4)

    @patch("full_pipeline.ParallelChain.run_chains")
    def test_c5t9_benchmark_speedup_gt_1(self, mock_run):
        """C5-T9: speedup > 1.0 com dados simulados."""
        mock_run.return_value = self.fake_chains

        fp = FullPipeline()
        result = fp.run_with_benchmark("Solve 2x + 3 = 7")

        # Sequencial = 50+100+200+400 = 750ms, Paralelo = max(50,100,200,400) = 400ms
        # speedup = 750/400 = 1.875
        self.assertGreater(result.speedup_vs_sequential, 1.0)
        self.assertAlmostEqual(result.speedup_vs_sequential, 1.875, places=2)


# ===================================================================
# C5-T10 a C5-T11: Robustness
# ===================================================================

class TestC5T10_T11_Robustness(unittest.TestCase):
    """Testes de robustez com falhas parciais."""

    @patch("full_pipeline.ParallelChain.run_chains")
    def test_c5t10_fallback_on_failures(self, mock_run):
        """C5-T10: Cadeias falham, pipeline ainda produz resposta."""
        chains = [
            make_chain(1, "express",  30,  0.0,  10,   "Error",              error="Failed"),
            make_chain(2, "standard", 60,  55.0, 100,  "Working solution B"),
            make_chain(3, "magnum",   100, 0.0,  10,   "Error",              error="Crashed"),
            make_chain(4, "research", 200, 75.0, 400,  "Working solution D"),
        ]
        mock_run.return_value = chains

        fp = FullPipeline()
        result = fp.run("Test problem")

        self.assertIsNotNone(result.answer)
        self.assertGreater(len(result.answer), 0)
        # weighted_vote deve ignorar cadeias com erro
        self.assertIn("Working", result.answer)

    @patch("full_pipeline.ParallelChain.run_chains")
    def test_c5t11_pipeline_flows_without_error(self, mock_run):
        """C5-T11: Pipeline executa sem exceção."""
        mock_run.return_value = [
            make_chain(1, "standard", 60, 50.0, 100, "Solution text here")
        ]

        fp = FullPipeline()
        try:
            result = fp.run("Simple problem")
            self.assertGreater(len(result.answer), 0)
        except Exception as e:
            self.fail(f"Pipeline raised exception: {e}")


# ===================================================================
# C5-T12: Strategy Diversity
# ===================================================================

class TestC5T12_StrategyDiversity(unittest.TestCase):
    """Diferentes perfis geram diferentes estratégias."""

    def test_different_profiles_different_strategies(self):
        """C5-T12: Cada domínio mapeia para estratégia correta."""
        strategies_usadas = set()

        for domain, expected_strategy in STRATEGY_RULES.items():
            p = ProblemProfile(domain=domain)
            fp = FullPipeline(profile=p)
            strategy = fp.select_strategy()
            strategies_usadas.add(strategy)
            self.assertEqual(
                strategy, expected_strategy,
                f"Domínio '{domain}' deveria usar '{expected_strategy}', obteve '{strategy}'",
            )

        # Deve haver pelo menos 2 estratégias diferentes entre as regras
        self.assertGreater(len(strategies_usadas), 1,
                           "Deveria haver diversidade de estratégias")

    def test_domain_takes_precedence_over_complexity(self):
        """Regra de domínio sobrescreve regra de complexidade."""
        # low complexity + code → weighted_vote (domain) ≠ best_of (complexity)
        p = ProblemProfile(domain="code", complexity="low")
        fp = FullPipeline(profile=p)
        strategy = fp.select_strategy()
        self.assertEqual(strategy, "weighted_vote")


# ===================================================================
# C5-T13: Scalability
# ===================================================================

class TestC5T13_Scalability(unittest.TestCase):
    """Pipeline com diferentes números de cadeias."""

    @patch("full_pipeline.ParallelChain.run_chains")
    def test_with_one_chain(self, mock_run):
        """C5-T13: Funciona com 1 cadeia."""
        mock_run.return_value = [make_chain(1, "standard", 60, 50.0, 100, "Solo")]
        fp = FullPipeline()
        result = fp.run("Test")
        self.assertEqual(result.chain_count, 1)

    @patch("full_pipeline.ParallelChain.run_chains")
    def test_with_four_chains(self, mock_run):
        """C5-T13: Funciona com 4 cadeias."""
        chains = [
            make_chain(1, "express",  30,  45.0,  50,   "A"),
            make_chain(2, "standard", 60,  55.0,  100,  "B"),
            make_chain(3, "magnum",   100, 65.0,  200,  "C"),
            make_chain(4, "research", 200, 75.0,  400,  "D"),
        ]
        mock_run.return_value = chains
        fp = FullPipeline()
        result = fp.run("Test")
        self.assertEqual(result.chain_count, 4)

    @patch("full_pipeline.ParallelChain.run_chains")
    def test_with_empty_chains(self, mock_run):
        """Edge case: lista vazia de cadeias."""
        mock_run.return_value = []
        fp = FullPipeline()
        result = fp.run("Test")
        self.assertEqual(result.chain_count, 0)
        self.assertEqual(result.confidence, 0.0)


# ===================================================================
# C5-T14: Sanity
# ===================================================================

class TestC5T14_Sanity(unittest.TestCase):
    """Sanidade: resultado tem resposta não vazia."""

    @patch("full_pipeline.ParallelChain.run_chains")
    def test_result_has_answer(self, mock_run):
        """C5-T14: final_answer é string não vazia."""
        mock_run.return_value = [
            make_chain(1, "standard", 60, 50.0, 100, "A valid answer from chain")
        ]
        fp = FullPipeline()
        result = fp.run("What is the meaning of life?")
        self.assertGreater(len(result.answer), 0)
        self.assertIsInstance(result.answer, str)

    @patch("full_pipeline.ParallelChain.run_chains")
    def test_benchmark_has_answer(self, mock_run):
        """BenchmarkResult também tem final_answer não vazio."""
        mock_run.return_value = [
            make_chain(1, "standard", 60, 50.0, 100, "Benchmark answer text")
        ]
        fp = FullPipeline()
        result = fp.run_with_benchmark("Test benchmark")
        self.assertGreater(len(result.final_answer), 0)
        self.assertIsInstance(result.final_answer, str)


# ===================================================================
# BOOT
# ===================================================================

if __name__ == "__main__":
    unittest.main()
