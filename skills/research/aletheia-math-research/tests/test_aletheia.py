import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from aletheia_engine import (
    AletheiaEngine, Generator, Verifier, Reviser,
    MathProblem, SolutionAttempt, VerificationResult,
    AletheiaSession, Phase, AutonomyLevel,
    BENCHMARK_PROBLEMS, SEED
)


class TestAletheiaEngine:
    def setup_method(self):
        self.engine = AletheiaEngine(max_attempts=3, strictness=0.6, verbose=False)

    def test_engine_initialization(self):
        assert self.engine.max_attempts == 3
        assert self.engine.strictness == 0.6
        assert isinstance(self.engine.generator, Generator)
        assert isinstance(self.engine.verifier, Verifier)
        assert isinstance(self.engine.reviser, Reviser)

    def test_generator_produces_solution(self):
        problem = MathProblem(
            id="test-1", statement="Prove that 1+1=2.",
            domain="algebra", difficulty="olympiad"
        )
        gen = Generator()
        attempt = gen.generate(problem, attempt_number=1)
        assert isinstance(attempt, SolutionAttempt)
        assert len(attempt.content) > 50
        assert len(attempt.reasoning_types_used) > 0
        assert 0.0 <= attempt.confidence <= 1.0

    def test_verifier_scores_solution(self):
        problem = MathProblem(
            id="test-2", statement="Prove that gcd(21n+4, 14n+3)=1 for all n.",
            domain="number_theory", difficulty="olympiad"
        )
        gen = Generator()
        attempt = gen.generate(problem)
        verifier = Verifier(strictness=0.5)
        result = verifier.verify(problem, attempt)
        assert isinstance(result, VerificationResult)
        assert isinstance(result.passed, bool)
        assert 0.0 <= result.score <= 1.0
        assert len(result.cora_checks) == 7
        for check_id in ["V1_LogicalConsistency", "V2_MathematicalCorrectness",
                         "V3_EdgeCaseCoverage", "V4_CitationAccuracy",
                         "V5_ProofCompleteness", "V6_CounterexampleResistance",
                         "V7_ClarityAndRigor"]:
            assert check_id in result.cora_checks

    def test_engine_solve_pipeline(self):
        problem = MathProblem(
            id="test-solve", statement="Prove that 2+2=4.",
            domain="algebra", difficulty="olympiad"
        )
        session = self.engine.solve(problem)
        assert isinstance(session, AletheiaSession)
        assert session.status in ("solved", "failed")
        assert len(session.attempts) > 0
        assert len(session.verifications) > 0
        metrics = self.engine.get_metrics()
        assert metrics["total_sessions"] >= 1
        assert "solve_rate" in metrics

    def test_benchmark_problems_loaded(self):
        assert len(BENCHMARK_PROBLEMS) >= 3
        for key, problem in BENCHMARK_PROBLEMS.items():
            assert isinstance(problem, MathProblem)
            assert len(problem.statement) > 10
            assert problem.domain in ("number_theory", "combinatorics", "algebra")


class TestAletheiaEnhanced:
    def setup_method(self):
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
        from aletheia_enhanced import (
            EnhancedAletheiaEngine, EnhancedVerifier, EnhancedGenerator,
            RefinementTracker, detect_subdomain, ProblemSubDomain
        )
        self.EnhancedEngine = EnhancedAletheiaEngine
        self.EnhancedVerifier = EnhancedVerifier
        self.EnhancedGenerator = EnhancedGenerator
        self.RefinementTracker = RefinementTracker
        self.detect_subdomain = detect_subdomain
        self.ProblemSubDomain = ProblemSubDomain
        self.engine = EnhancedAletheiaEngine(max_attempts=3, strictness=0.6, verbose=False)

    def test_enhanced_engine_initialization(self):
        assert hasattr(self.engine, 'refiner')
        assert isinstance(self.engine.generator, self.EnhancedGenerator)
        assert isinstance(self.engine.verifier, self.EnhancedVerifier)
        assert self.engine.max_attempts == 3

    def test_detect_subdomain_gcd(self):
        problem = MathProblem(
            id="gcd-test", domain="number_theory",
            statement="Prove that the fraction (21n+4)/(14n+3) is irreducible for every natural number n.",
            difficulty="olympiad"
        )
        subdomain = self.detect_subdomain(problem)
        assert subdomain == self.ProblemSubDomain.GCD_EUCLIDEAN

    def test_detect_subdomain_induction(self):
        problem = MathProblem(
            id="ind-test", domain="combinatorics",
            statement="Prove by induction that for all n, 2^n > n.",
            difficulty="olympiad"
        )
        subdomain = self.detect_subdomain(problem)
        assert subdomain == self.ProblemSubDomain.INDUCTION

    def test_enhanced_verifier_has_semantic_checks(self):
        verifier = self.EnhancedVerifier(strictness=0.7)
        assert "V8_DomainSpecificCorrectness" in verifier.SEMANTIC_CHECKS
        assert "V9_ConclusionAlignment" in verifier.SEMANTIC_CHECKS
        assert "V10_ReasoningRelevance" in verifier.SEMANTIC_CHECKS
        assert "V11_StepByStepValidity" in verifier.SEMANTIC_CHECKS
        assert "V12_UniversalCoverage" in verifier.SEMANTIC_CHECKS

    def test_refinement_tracker_empty(self):
        tracker = self.RefinementTracker()
        report = tracker.report()
        assert "Nenhuma sess" in report

    def test_enhanced_engine_solve(self):
        problem = MathProblem(
            id="imo-gcd", domain="number_theory",
            statement="Prove that gcd(21n+4, 14n+3)=1 for all n.",
            difficulty="olympiad"
        )
        session = self.engine.solve(problem)
        assert session.status in ("solved", "failed")
        assert len(session.attempts) > 0
        report = self.engine.refiner.report()
        assert "Total sessions" in report
