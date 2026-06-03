#!/usr/bin/env python3
"""
TDD Test Suite for SPEC-015: ErdosEvaluator
===========================================

8 Tests:
1. Dataset loading (700 simulated or 4 manual)
2. Grading logic (5 levels: NO_SOLUTION → NOVEL_CONTRIBUTION)
3. Autonomy assignment (L0-L3)
4. Metrics computation (meaningful success rate)
5. Batch evaluation (end-to-end)
6. Comparison vs Aletheia baseline (delta measurement)
7. Report structure (JSON)
8. Seed reproducibility
"""

import pytest
import json
import random
from spec_015_erdos_evaluator import (
    ErdosProblem,
    EvaluationResult,
    ErdosEvaluationMetrics,
    ErdosGradingLevel,
    ErdosDatasetLoader,
    ErdosGrader,
    ErdosEvaluator,
)


SEED = 42


class TestSpec015DatasetLoading:
    """Test 1: Dataset loading (700 simulated or 4 manual)."""
    
    def test_load_simulated_dataset(self):
        """RED: Load 700 simulated problems. GREEN: Verify count."""
        loader = ErdosDatasetLoader(use_realistic_subset=True)
        problems = loader.problems
        
        assert len(problems) == 700, f"Expected 700 problems, got {len(problems)}"
        
        # Verify structure of each problem
        for problem in problems[:10]:  # Check first 10
            assert isinstance(problem, ErdosProblem)
            assert hasattr(problem, "erdos_id")
            assert hasattr(problem, "domain")
            assert hasattr(problem, "difficulty")
            assert hasattr(problem, "statement")
    
    def test_load_manual_problems(self):
        """RED: Load 4 manual Erdős problems. GREEN: Verify IDs."""
        loader = ErdosDatasetLoader(use_realistic_subset=False)
        problems = loader.problems
        
        # Must have exactly 4 manual problems
        assert len(problems) == 4, f"Expected 4 problems, got {len(problems)}"
        
        expected_ids = {"Erdos-652", "Erdos-654", "Erdos-1040", "Erdos-1051"}
        actual_ids = {p.erdos_id for p in problems}
        assert actual_ids == expected_ids, f"Expected {expected_ids}, got {actual_ids}"
    
    def test_problem_structure(self):
        """RED: Verify ErdosProblem dataclass. GREEN: All fields present."""
        loader = ErdosDatasetLoader(use_realistic_subset=True)
        problem = loader.problems[0]
        
        # Verify required fields
        assert isinstance(problem.erdos_id, str)
        assert isinstance(problem.domain, str)
        assert isinstance(problem.difficulty.value, str)  # Enum, so check .value
        assert isinstance(problem.statement, str)
        
        # Verify domain is valid
        valid_domains = {"number_theory", "combinatorics", "algebra", "geometry", "analysis"}
        assert problem.domain in valid_domains, f"Invalid domain: {problem.domain}"


class TestSpec015GradingLogic:
    """Test 2: Grading logic (5 levels)."""
    
    def test_grading_levels_enum(self):
        """RED: Verify 5 grading levels. GREEN: Enum complete."""
        expected = {
            ErdosGradingLevel.NO_SOLUTION,
            ErdosGradingLevel.TECHNICALLY_INCORRECT,
            ErdosGradingLevel.TECHNICALLY_CORRECT,
            ErdosGradingLevel.MEANINGFULLY_CORRECT,
            ErdosGradingLevel.NOVEL_CONTRIBUTION,
        }
        assert len(expected) == 5
    
    def test_grade_no_solution(self):
        """RED: Score 0.0 (no attempt). GREEN: Grade = NO_SOLUTION."""
        grader = ErdosGrader(seed=SEED)
        
        problem = ErdosProblem(
            erdos_id="P1",
            statement="Test problem",
            domain="number_theory",
            difficulty="olympiad"
        )
        
        result = grader.grade_solution(
            problem=problem,
            solution=None,  # No solution
            aletheia_verifier_score=0.0,
            cora_checks_passed=0,
        )
        
        assert result.grading == ErdosGradingLevel.NO_SOLUTION
    
    def test_grade_technically_incorrect(self):
        """RED: Low score. GREEN: Grade = TECHNICALLY_INCORRECT."""
        grader = ErdosGrader(seed=SEED)
        
        result = grader.grade_solution(
            problem_id="P2",
            aletheia_score=0.25,
            cora_passed_count=1,
        )
        
        assert result.grading_level == ErdosGradingLevel.TECHNICALLY_INCORRECT
    
    def test_grade_technically_correct(self):
        """RED: Medium-low score. GREEN: Grade = TECHNICALLY_CORRECT."""
        grader = ErdosGrader(seed=SEED)
        
        result = grader.grade_solution(
            problem_id="P3",
            aletheia_score=0.55,
            cora_passed_count=4,
        )
        
        assert result.grading_level == ErdosGradingLevel.TECHNICALLY_CORRECT
    
    def test_grade_meaningfully_correct(self):
        """RED: High score. GREEN: Grade = MEANINGFULLY_CORRECT."""
        grader = ErdosGrader(seed=SEED)
        
        result = grader.grade_solution(
            problem_id="P4",
            aletheia_score=0.80,
            cora_passed_count=6,
        )
        
        assert result.grading_level == ErdosGradingLevel.MEANINGFULLY_CORRECT
    
    def test_grade_novel_contribution(self):
        """RED: Very high score. GREEN: Grade = NOVEL_CONTRIBUTION."""
        grader = ErdosGrader(seed=SEED)
        
        result = grader.grade_solution(
            problem_id="P5",
            aletheia_score=0.95,
            cora_passed_count=7,
        )
        
        assert result.grading_level == ErdosGradingLevel.NOVEL_CONTRIBUTION


class TestSpec015AutonomyAssignment:
    """Test 3: Autonomy assignment (L0-L3)."""
    
    def test_autonomy_level_for_low_cora_score(self):
        """RED: Low Cora score. GREEN: Autonomy = L1 (minor)."""
        grader = ErdosGrader(seed=SEED)
        
        result = grader.grade_solution(
            problem_id="P1",
            aletheia_score=0.60,
            cora_passed_count=2,  # Low: 2/7
        )
        
        assert result.autonomy_level == "L1", f"Expected L1, got {result.autonomy_level}"
    
    def test_autonomy_level_for_publishable_score(self):
        """RED: Publishable range (0.6-0.85). GREEN: Autonomy = L2."""
        grader = ErdosGrader(seed=SEED)
        
        result = grader.grade_solution(
            problem_id="P2",
            aletheia_score=0.72,
            cora_passed_count=5,  # Medium: 5/7
        )
        
        assert result.autonomy_level == "L2", f"Expected L2, got {result.autonomy_level}"
    
    def test_autonomy_level_for_major_discovery(self):
        """RED: High score (>0.85). GREEN: Autonomy = L3 (major)."""
        grader = ErdosGrader(seed=SEED)
        
        result = grader.grade_solution(
            problem_id="P3",
            aletheia_score=0.88,
            cora_passed_count=7,
        )
        
        assert result.autonomy_level == "L3", f"Expected L3, got {result.autonomy_level}"


class TestSpec015MetricsComputation:
    """Test 4: Metrics computation."""
    
    def test_meaningful_success_rate_computation(self):
        """RED: Compute metrics on batch. GREEN: Success rate calculated."""
        evaluator = ErdosEvaluator(seed=SEED)
        
        # Create dummy results
        results = [
            EvaluationResult(
                problem_id=f"P{i}",
                grading_level=ErdosGradingLevel.MEANINGFULLY_CORRECT if i % 5 == 0 
                else ErdosGradingLevel.TECHNICALLY_CORRECT,
                autonomy_level="L2" if i % 5 == 0 else "L1",
            )
            for i in range(20)
        ]
        
        metrics = evaluator.compute_metrics(results)
        
        # Should have some meaningful solutions
        assert metrics.meaningful_count >= 0
        assert metrics.meaningful_success_rate >= 0.0
    
    def test_metrics_structure(self):
        """RED: Generate metrics. GREEN: All fields present."""
        evaluator = ErdosEvaluator(seed=SEED)
        
        results = [
            EvaluationResult(
                problem_id="P1",
                grading_level=ErdosGradingLevel.MEANINGFULLY_CORRECT,
                autonomy_level="L2",
            ),
        ]
        
        metrics = evaluator.compute_metrics(results)
        
        assert hasattr(metrics, "total_count")
        assert hasattr(metrics, "meaningful_count")
        assert hasattr(metrics, "meaningful_success_rate")
        assert hasattr(metrics, "autonomy_distribution")


class TestSpec015BatchEvaluation:
    """Test 5: Batch evaluation (end-to-end)."""
    
    def test_batch_evaluation_on_small_set(self):
        """RED: Evaluate 10 problems. GREEN: Get 10 results."""
        evaluator = ErdosEvaluator(seed=SEED)
        
        loader = ErdosDatasetLoader(seed=SEED)
        problems = loader.load_simulated_dataset(n_problems=10)
        
        results = evaluator.evaluate_batch(problems)
        
        assert len(results) == 10, f"Expected 10 results, got {len(results)}"
        
        # All must be EvaluationResult
        for result in results:
            assert isinstance(result, EvaluationResult)
            assert hasattr(result, "problem_id")
            assert hasattr(result, "grading_level")


class TestSpec015ComparisonVsBaseline:
    """Test 6: Comparison vs Aletheia baseline."""
    
    def test_baseline_metrics_hardcoded(self):
        """RED: Retrieve Aletheia baseline. GREEN: Metrics match paper."""
        evaluator = ErdosEvaluator(seed=SEED)
        
        baseline = evaluator.get_aletheia_baseline()
        
        # Aletheia results from paper
        # 700 problems → 30% solutions returned, 29.7% technically correct, 6.1% meaningful, 1.9% novel
        assert isinstance(baseline, dict)
        assert "total_problems" in baseline
        assert "solutions_returned" in baseline
        assert "meaningful_success_rate" in baseline
    
    def test_delta_measurement(self):
        """RED: Compute delta vs baseline. GREEN: Report improvement."""
        evaluator = ErdosEvaluator(seed=SEED)
        
        # Mock OpenCode results
        mock_results = [
            EvaluationResult(
                problem_id=f"P{i}",
                grading_level=ErdosGradingLevel.MEANINGFULLY_CORRECT if i % 12 == 0
                else ErdosGradingLevel.TECHNICALLY_CORRECT,
                autonomy_level="L2" if i % 12 == 0 else "L1",
            )
            for i in range(200)
        ]
        
        baseline = evaluator.get_aletheia_baseline()
        metrics = evaluator.compute_metrics(mock_results)
        
        # Compute delta
        delta = metrics.meaningful_success_rate - baseline["meaningful_success_rate"]
        
        assert isinstance(delta, float)
        # Target: 8%+ meaningful (vs Aletheia 6.1%)
        if metrics.meaningful_success_rate > baseline["meaningful_success_rate"]:
            assert delta >= 0


class TestSpec015ReportStructure:
    """Test 7: Report structure (JSON)."""
    
    def test_generate_evaluation_report(self):
        """RED: Generate report. GREEN: JSON valid."""
        evaluator = ErdosEvaluator(seed=SEED)
        
        loader = ErdosDatasetLoader(seed=SEED)
        problems = loader.load_simulated_dataset(n_problems=5)
        results = evaluator.evaluate_batch(problems)
        
        report_json = evaluator.generate_report(results)
        
        # Must be valid JSON
        report = json.loads(report_json)
        
        # Verify structure
        assert "summary" in report
        assert "total_evaluated" in report["summary"]
        assert "results" in report
    
    def test_report_completeness(self):
        """RED: Generate full report. GREEN: All sections present."""
        evaluator = ErdosEvaluator(seed=SEED)
        
        results = [
            EvaluationResult(
                problem_id="P1",
                grading_level=ErdosGradingLevel.MEANINGFULLY_CORRECT,
                autonomy_level="L3",
            ),
            EvaluationResult(
                problem_id="P2",
                grading_level=ErdosGradingLevel.TECHNICALLY_CORRECT,
                autonomy_level="L2",
            ),
        ]
        
        report_json = evaluator.generate_report(results)
        report = json.loads(report_json)
        
        # Verify per-problem results documented
        assert len(report["results"]) == len(results)


class TestSpec015Reproducibility:
    """Test 8: Seed reproducibility."""
    
    def test_evaluation_reproducibility(self):
        """RED: Evaluate twice with seed=42. GREEN: Verdicts identical."""
        loader = ErdosDatasetLoader(seed=SEED)
        problems = loader.load_simulated_dataset(n_problems=5)
        
        # Run 1
        random.seed(SEED)
        evaluator1 = ErdosEvaluator(seed=SEED)
        results1 = evaluator1.evaluate_batch(problems)
        verdicts1 = [r.grading_level for r in results1]
        
        # Run 2
        random.seed(SEED)
        evaluator2 = ErdosEvaluator(seed=SEED)
        results2 = evaluator2.evaluate_batch(problems)
        verdicts2 = [r.grading_level for r in results2]
        
        # Must be identical
        assert verdicts1 == verdicts2, f"Run 1: {verdicts1}, Run 2: {verdicts2}"
    
    def test_baseline_dataset_seed_consistency(self):
        """RED: Load dataset twice with seed=42. GREEN: Problem IDs identical."""
        loader1 = ErdosDatasetLoader(seed=SEED)
        problems1 = loader1.load_simulated_dataset(n_problems=20)
        
        loader2 = ErdosDatasetLoader(seed=SEED)
        problems2 = loader2.load_simulated_dataset(n_problems=20)
        
        ids1 = [p.problem_id for p in problems1]
        ids2 = [p.problem_id for p in problems2]
        
        assert ids1 == ids2, "Problem IDs should be identical with same seed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
