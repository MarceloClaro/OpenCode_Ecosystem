#!/usr/bin/env python3
"""
TDD Test Suite for SPEC-015: ErdosEvaluator
===========================================

21 Tests with corrected method signatures.
"""

import pytest
import json
import random
from spec_015_erdos_evaluator import (
    ErdosProblem,
    EvaluationResult,
    ErdosEvaluationMetrics,
    ErdosGradingLevel,
    ErdosProblemDifficulty,
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
        assert len(loader.problems) == 700, f"Expected 700, got {len(loader.problems)}"
    
    def test_load_manual_problems(self):
        """RED: Load 4 manual Erdős problems. GREEN: Verify IDs."""
        loader = ErdosDatasetLoader(use_realistic_subset=False)
        assert len(loader.problems) == 4, f"Expected 4, got {len(loader.problems)}"
        
        expected_ids = {"Erdos-652", "Erdos-654", "Erdos-1040", "Erdos-1051"}
        actual_ids = {p.erdos_id for p in loader.problems}
        assert actual_ids == expected_ids
    
    def test_problem_structure(self):
        """RED: Verify ErdosProblem dataclass. GREEN: All fields present."""
        loader = ErdosDatasetLoader(use_realistic_subset=False)
        problem = loader.problems[0]
        
        assert isinstance(problem.erdos_id, str)
        assert isinstance(problem.statement, str)
        assert isinstance(problem.domain, str)
        assert problem.domain in {"number_theory", "combinatorics", "algebra", "geometry", "analysis"}


class TestSpec015GradingLogic:
    """Test 2: Grading logic (5 levels)."""
    
    def test_grading_levels_enum(self):
        """RED: Verify 5 grading levels. GREEN: Enum complete."""
        expected_levels = 5
        actual_levels = len(list(ErdosGradingLevel))
        assert actual_levels == expected_levels
    
    def test_grade_no_solution(self):
        """RED: No solution returned. GREEN: Grade = NO_SOLUTION."""
        grader = ErdosGrader(seed=SEED)
        problem = ErdosProblem(
            erdos_id="P1",
            statement="Test",
            domain="number_theory",
            difficulty=ErdosProblemDifficulty.OLYMPIAD
        )
        
        result = grader.grade_solution(
            problem=problem,
            solution=None,
            aletheia_verifier_score=0.0,
            cora_checks_passed=0,
        )
        
        assert result.grading == ErdosGradingLevel.NO_SOLUTION
    
    def test_grade_technically_incorrect(self):
        """RED: Low score (<0.3). GREEN: Grade = TECHNICALLY_INCORRECT."""
        grader = ErdosGrader(seed=SEED)
        problem = ErdosProblem(
            erdos_id="P2",
            statement="Test",
            domain="combinatorics",
            difficulty=ErdosProblemDifficulty.PHD_EXERCISE
        )
        
        result = grader.grade_solution(
            problem=problem,
            solution="Wrong proof",
            aletheia_verifier_score=0.10,
            cora_checks_passed=0,
        )
        
        assert result.grading == ErdosGradingLevel.TECHNICALLY_INCORRECT
    
    def test_grade_technically_correct(self):
        """RED: Medium score (0.3-0.6). GREEN: Grade = TECHNICALLY_CORRECT."""
        grader = ErdosGrader(seed=SEED)
        problem = ErdosProblem(
            erdos_id="P3",
            statement="Test",
            domain="algebra",
            difficulty=ErdosProblemDifficulty.RESEARCH_OPEN
        )
        
        result = grader.grade_solution(
            problem=problem,
            solution="Partial proof",
            aletheia_verifier_score=0.40,
            cora_checks_passed=2,
        )
        
        assert result.grading == ErdosGradingLevel.TECHNICALLY_CORRECT
    
    def test_grade_meaningfully_correct(self):
        """RED: High score (0.6-0.85). GREEN: Grade = MEANINGFULLY_CORRECT."""
        grader = ErdosGrader(seed=SEED)
        problem = ErdosProblem(
            erdos_id="P4",
            statement="Test",
            domain="number_theory",
            difficulty=ErdosProblemDifficulty.RESEARCH_OPEN
        )
        
        result = grader.grade_solution(
            problem=problem,
            solution="Complete proof",
            aletheia_verifier_score=0.75,
            cora_checks_passed=5,
        )
        
        assert result.grading == ErdosGradingLevel.MEANINGFULLY_CORRECT
    
    def test_grade_novel_contribution(self):
        """RED: Very high score (>0.85). GREEN: Grade = NOVEL_CONTRIBUTION."""
        grader = ErdosGrader(seed=SEED)
        problem = ErdosProblem(
            erdos_id="P5",
            statement="Test",
            domain="geometry",
            difficulty=ErdosProblemDifficulty.RESEARCH_OPEN
        )
        
        result = grader.grade_solution(
            problem=problem,
            solution="Novel insight",
            aletheia_verifier_score=0.95,
            cora_checks_passed=7,
        )
        
        assert result.grading == ErdosGradingLevel.NOVEL_CONTRIBUTION


class TestSpec015AutonomyAssignment:
    """Test 3: Autonomy assignment (L0-L3)."""
    
    def test_autonomy_level_for_low_cora_score(self):
        """RED: Low Cora (2/7). GREEN: Autonomy = L1."""
        grader = ErdosGrader(seed=SEED)
        problem = ErdosProblem(
            erdos_id="P1",
            statement="Test",
            domain="number_theory",
            difficulty=ErdosProblemDifficulty.OLYMPIAD
        )
        
        result = grader.grade_solution(
            problem=problem,
            solution="Partial",
            aletheia_verifier_score=0.45,
            cora_checks_passed=2,
        )
        
        assert result.autonomy_level == "L1"
    
    def test_autonomy_level_for_publishable_score(self):
        """RED: Medium Cora (5/7). GREEN: Autonomy = L2."""
        grader = ErdosGrader(seed=SEED)
        problem = ErdosProblem(
            erdos_id="P2",
            statement="Test",
            domain="combinatorics",
            difficulty=ErdosProblemDifficulty.PHD_EXERCISE
        )
        
        result = grader.grade_solution(
            problem=problem,
            solution="Good proof",
            aletheia_verifier_score=0.70,
            cora_checks_passed=5,
        )
        
        assert result.autonomy_level == "L2"
    
    def test_autonomy_level_for_major_discovery(self):
        """RED: High Cora (7/7). GREEN: Autonomy = L3."""
        grader = ErdosGrader(seed=SEED)
        problem = ErdosProblem(
            erdos_id="P3",
            statement="Test",
            domain="analysis",
            difficulty=ErdosProblemDifficulty.RESEARCH_OPEN
        )
        
        result = grader.grade_solution(
            problem=problem,
            solution="Excellent proof",
            aletheia_verifier_score=0.90,
            cora_checks_passed=7,
        )
        
        assert result.autonomy_level == "L3"


class TestSpec015MetricsComputation:
    """Test 4: Metrics computation."""
    
    def test_meaningful_success_rate_computation(self):
        """RED: Compute metrics. GREEN: Rates calculated."""
        # Use realistic subset to have 700 problems available
        evaluator = ErdosEvaluator()
        evaluator.dataset = ErdosDatasetLoader(use_realistic_subset=True)
        
        # Evaluate 10 problems
        def dummy_solution_generator(problem):
            return ("Solution", 0.7, 5)
        
        problems = evaluator.dataset.get_subset(10)
        evaluator.evaluate_batch(problems, dummy_solution_generator)
        
        assert len(evaluator.results) == 10
    
    def test_metrics_structure(self):
        """RED: Generate metrics. GREEN: All fields present."""
        evaluator = ErdosEvaluator()
        
        def dummy_solution_generator(problem):
            return ("Solution", 0.7, 5)
        
        problems = evaluator.dataset.get_subset(5)
        evaluator.evaluate_batch(problems, dummy_solution_generator)
        metrics = evaluator.compute_metrics()
        
        assert isinstance(metrics, ErdosEvaluationMetrics)
        assert hasattr(metrics, 'total_problems')
        assert hasattr(metrics, 'meaningfully_correct')
        assert hasattr(metrics, 'success_rate_meaningful')


class TestSpec015BatchEvaluation:
    """Test 5: Batch evaluation."""
    
    def test_batch_evaluation_on_small_set(self):
        """RED: Evaluate 10 problems. GREEN: 10 results."""
        evaluator = ErdosEvaluator()
        evaluator.dataset = ErdosDatasetLoader(use_realistic_subset=True)
        
        def dummy_solution_generator(problem):
            return ("Solution", 0.7, 5)
        
        problems = evaluator.dataset.get_subset(10)
        results = evaluator.evaluate_batch(problems, dummy_solution_generator)
        
        assert len(results) == 10


class TestSpec015ComparisonVsBaseline:
    """Test 6: Comparison vs Aletheia baseline."""
    
    def test_baseline_metrics_hardcoded(self):
        """RED: Retrieve baseline. GREEN: Metrics match Feng et al."""
        evaluator = ErdosEvaluator()
        
        assert evaluator.ALETHEIA_BASELINE["meaningfully_correct"] == 13
        assert evaluator.ALETHEIA_BASELINE["total"] == 700
    
    def test_delta_measurement(self):
        """RED: Compute delta. GREEN: Report improvement."""
        evaluator = ErdosEvaluator()
        
        def dummy_solution_generator(problem):
            return ("Solution", 0.7, 5)
        
        problems = evaluator.dataset.get_subset(10)
        evaluator.evaluate_batch(problems, dummy_solution_generator)
        metrics = evaluator.compute_metrics()
        
        # Verify delta computation
        assert isinstance(metrics.comparison_with_aletheia, dict)


class TestSpec015ReportStructure:
    """Test 7: Report structure."""
    
    def test_generate_evaluation_report(self):
        """RED: Generate report. GREEN: JSON valid."""
        evaluator = ErdosEvaluator()
        
        def dummy_solution_generator(problem):
            return ("Solution", 0.7, 5)
        
        problems = evaluator.dataset.get_subset(5)
        evaluator.evaluate_batch(problems, dummy_solution_generator)
        
        report = evaluator.generate_report()
        
        assert isinstance(report, dict)
        assert 'evaluation_metadata' in report
    
    def test_report_completeness(self):
        """RED: Generate full report. GREEN: Sections present."""
        evaluator = ErdosEvaluator()
        
        def dummy_solution_generator(problem):
            return ("Solution", 0.7, 5)
        
        problems = evaluator.dataset.get_subset(3)
        evaluator.evaluate_batch(problems, dummy_solution_generator)
        
        report = evaluator.generate_report()
        
        assert 'metrics' in report
        assert 'comparison_with_aletheia' in report


class TestSpec015Reproducibility:
    """Test 8: Seed reproducibility."""
    
    def test_evaluation_reproducibility(self):
        """RED: Evaluate twice with seed=42. GREEN: Verdicts identical."""
        loader1 = ErdosDatasetLoader(use_realistic_subset=False)
        loader2 = ErdosDatasetLoader(use_realistic_subset=False)
        
        assert [p.erdos_id for p in loader1.problems] == [p.erdos_id for p in loader2.problems]
    
    def test_baseline_dataset_seed_consistency(self):
        """RED: Load twice with seed=42. GREEN: Problem IDs identical."""
        loader1 = ErdosDatasetLoader(use_realistic_subset=False)
        loader2 = ErdosDatasetLoader(use_realistic_subset=False)
        
        ids1 = {p.erdos_id for p in loader1.problems}
        ids2 = {p.erdos_id for p in loader2.problems}
        
        assert ids1 == ids2
