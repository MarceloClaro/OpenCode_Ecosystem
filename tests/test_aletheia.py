"""
test_aletheia.py — TDD suite for SPEC-012 (Aletheia Math Research)
10 CTs covering Generator, Verifier, Reviser, and full pipeline.
"""
import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 
    '.config', 'opencode', 'skills', 'research', 'aletheia-math-research', 'scripts'))

from aletheia_engine import (
    AletheiaEngine, MathProblem, Generator, Verifier, Reviser,
    SolutionAttempt, VerificationResult, AutonomyLevel, BENCHMARK_PROBLEMS
)


class TestCT1_GeneratorProducesOutput:
    """CT-1: Generator produz solucao em linguagem natural."""
    
    def test_generator_produces_nonempty_solution(self):
        gen = Generator()
        problem = BENCHMARK_PROBLEMS["imo_2024_p1"]
        solution = gen.generate(problem)
        assert len(solution.content) > 100, "Solucao muito curta"
        assert "Solution" in solution.content, "Deve conter 'Solution'"
        assert len(solution.reasoning_types_used) >= 2, "Minimo 2 tipos raciocinio"


class TestCT2_GeneratorReasoningDiversity:
    """CT-2: Generator usa tipos de raciocinio diversos."""
    
    def test_reasoning_types_vary_by_domain(self):
        gen = Generator()
        nt = gen._select_reasoning_types("number_theory", 1)
        comb = gen._select_reasoning_types("combinatorics", 1)
        assert nt != comb, "Dominios diferentes devem usar raciocinios diferentes"
    
    def test_reasoning_expands_with_attempts(self):
        gen = Generator()
        early = gen._select_reasoning_types("number_theory", 1)
        late = gen._select_reasoning_types("number_theory", 5)
        assert len(late) >= len(early), "Tentativas tardias devem ter mais diversidade"


class TestCT3_VerifierDetectsFlaws:
    """CT-3: Verifier detecta flaws em solucoes incorretas."""
    
    def test_detects_division_by_zero(self):
        verifier = Verifier(strictness=0.7)
        problem = BENCHMARK_PROBLEMS["imo_2024_p1"]
        bad_solution = SolutionAttempt(
            attempt_id=1, phase="solution_generation",
            content="Divide by zero: 1/0 = ∞. Therefore the answer is 42.",
            reasoning_types_used=["deductive"], confidence=0.9, tool_calls=[]
        )
        result = verifier.verify(problem, bad_solution)
        assert not result.passed, "Deve detectar divisao por zero"
        assert len(result.flaws) >= 1
    
    def test_detects_missing_conclusion(self):
        verifier = Verifier(strictness=0.7)
        problem = BENCHMARK_PROBLEMS["thue_morse"]
        incomplete = SolutionAttempt(
            attempt_id=2, phase="solution_generation",
            content="We observe that t(n) has property P. This is interesting.",
            reasoning_types_used=["inductive"], confidence=0.7, tool_calls=[]
        )
        result = verifier.verify(problem, incomplete)
        assert not result.passed, "Deve detectar falta de conclusao"


class TestCT4_VerifierApprovesCorrect:
    """CT-4: Verifier aprova solucoes corretas."""
    
    def test_approves_well_structured_solution(self):
        verifier = Verifier(strictness=0.5)  # permissivo
        problem = BENCHMARK_PROBLEMS["imo_2024_p1"]
        good = SolutionAttempt(
            attempt_id=3, phase="solution_generation",
            content=(
                "## Theorem\nAll α ∈ ℤ satisfy the condition.\n\n"
                "## Proof\nLet α ∈ ℤ. Then floor(kα) = kα for each integer k. "
                "Therefore the sum = α·n(n+1)/2 which is a multiple of n. "
                "Conversely, if α ∉ ℤ, consider n=1 to see contradiction. "
                "Edge case: α=0 trivially works. Therefore the statement holds. ∎"
            ),
            reasoning_types_used=["deductive", "contradiction"], confidence=0.85, tool_calls=[]
        )
        result = verifier.verify(problem, good)
        assert result.passed, f"Solucao correta deveria passar. Score={result.score:.2f}, Flaws={result.flaws}"


class TestCT5_ReviserImprovesSolution:
    """CT-5: Reviser incorpora feedback do Verifier."""
    
    def test_reviser_adds_addressed_flaws(self):
        reviser = Reviser()
        problem = BENCHMARK_PROBLEMS["imo_2024_p1"]
        original = SolutionAttempt(
            attempt_id=1, phase="solution_generation",
            content="Original proof.", reasoning_types_used=["deductive"],
            confidence=0.6, tool_calls=[]
        )
        verification = VerificationResult(
            solution_id=1, passed=False, score=0.4,
            flaws=["Missing edge cases", "No conclusion"],
            hallucination_detected=False,
            cora_checks={"V3_EdgeCaseCoverage": False, "V5_ProofCompleteness": False},
            suggestion="Add edge cases and conclusion"
        )
        revised = reviser.revise(problem, original, verification)
        assert "FIXED" in revised, "Deve marcar flaws como corrigidos"
        assert "Revision" in revised, "Deve indicar que e uma revisao"


class TestCT6_FullPipelineConverges:
    """CT-6: Pipeline completo converge em problemas Olympiad."""
    
    def test_solves_imo_problem_within_attempts(self):
        engine = AletheiaEngine(max_attempts=15, strictness=0.5, verbose=False)
        session = engine.solve(BENCHMARK_PROBLEMS["imo_2024_p1"])
        assert session.status == "solved", f"IMO deveria ser resolvido. Status={session.status}"
        assert session.current_attempt <= 15, "Deve convergir em <=15 tentativas"


class TestCT7_HallucinationDetection:
    """CT-7: Verifier detecta alucinacoes em citacoes."""
    
    def test_detects_fabricated_citations(self):
        verifier = Verifier(strictness=0.7)
        problem = BENCHMARK_PROBLEMS["erdos_1051"]
        hallucinated = SolutionAttempt(
            attempt_id=5, phase="solution_generation",
            content=(
                "As shown in [Author Unknown], [Title Unknown], "
                "arxiv:????.?????, the result follows trivially."
            ),
            reasoning_types_used=["deductive"], confidence=0.5, tool_calls=[]
        )
        result = verifier.verify(problem, hallucinated)
        assert result.hallucination_detected, "Deve detectar citacoes fabricadas"
        assert result.score < 0.5, "Score deve ser penalizado por alucinacao"


class TestCT8_AutonomyLevels:
    """CT-8: Niveis de autonomia sao atribuidos corretamente."""
    
    def test_perfect_solution_gets_publishable(self):
        verifier = Verifier(strictness=0.5)
        autonomy = verifier._determine_autonomy(0.96, False, 0)
        assert autonomy == AutonomyLevel.L2_PUBLISHABLE
    
    def test_flawed_solution_gets_negligible(self):
        verifier = Verifier(strictness=0.7)
        autonomy = verifier._determine_autonomy(0.5, True, 3)
        assert autonomy == AutonomyLevel.L0_NEGLIGIBLE


class TestCT9_BenchmarkAllProblems:
    """CT-9: Todos os 5 problemas do benchmark sao processados sem erro."""
    
    def test_all_problems_process_without_error(self):
        engine = AletheiaEngine(max_attempts=3, strictness=0.5, verbose=False)
        for key, problem in BENCHMARK_PROBLEMS.items():
            session = engine.solve(problem)
            assert session.status in ("solved", "failed"), \
                f"{key}: status invalido={session.status}"
            assert len(session.attempts) > 0, f"{key}: sem tentativas"
            assert len(session.verifications) > 0, f"{key}: sem verificacoes"


class TestCT10_MetricsAccuracy:
    """CT-10: Metricas do engine sao precisas."""
    
    def test_metrics_match_sessions(self):
        engine = AletheiaEngine(max_attempts=3, strictness=0.5, verbose=False)
        for key in list(BENCHMARK_PROBLEMS.keys())[:3]:
            engine.solve(BENCHMARK_PROBLEMS[key])
        
        metrics = engine.get_metrics()
        assert metrics["total_sessions"] == 3
        assert 0 <= metrics["solve_rate"] <= 1
        assert metrics["generator_count"] >= metrics["total_sessions"]
