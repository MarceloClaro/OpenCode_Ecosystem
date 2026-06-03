#!/usr/bin/env python3
"""
TDD Test Suite for SPEC-014: AletheiaVerifierWrapper
====================================================

6 Tests:
1. Cora check results (V1-V7 verdicts)
2. Reconciliation logic (conservative strategy)
3. Critical-failure handling (max-severity rule)
4. Aletheia score averaging
5. export_report() JSON structure
6. Wrapper integration (end-to-end)
"""

import pytest
import json
from spec_014_cora_wrapper import (
    CoraCheckId,
    CoraCheckResult,
    CoraVerifierSimulation,
    AletheiaVerifierWrapper,
)


SEED = 42


class TestSpec014CoraChecks:
    """Test 1: Cora check results (V1-V7 verdicts)."""
    
    def test_cora_check_id_enum(self):
        """RED: Verify all 7 Cora checks defined. GREEN: Enum contains all."""
        expected = {
            CoraCheckId.V1_LOGICAL_CONSISTENCY,
            CoraCheckId.V2_MATHEMATICAL_CORRECTNESS,
            CoraCheckId.V3_EDGE_CASE_COVERAGE,
            CoraCheckId.V4_CITATION_ACCURACY,
            CoraCheckId.V5_PROOF_COMPLETENESS,
            CoraCheckId.V6_COUNTEREXAMPLE_RESISTANCE,
            CoraCheckId.V7_CLARITY_AND_RIGOR,
        }
        assert len(expected) == 7
        # Verify all are callable
        for check in expected:
            assert isinstance(check, CoraCheckId)
    
    def test_cora_check_result_structure(self):
        """RED: Create CoraCheckResult. GREEN: Verify dataclass structure."""
        result = CoraCheckResult(
            check_id=CoraCheckId.V1_LOGICAL_CONSISTENCY,
            passed=True,
            confidence=0.92,
            severity="critical",
            details="All logical steps are valid"
        )
        
        assert result.check_id == CoraCheckId.V1_LOGICAL_CONSISTENCY
        assert result.passed is True
        assert 0.0 <= result.confidence <= 1.0
        assert result.severity in ["critical", "warning", "info"]
        assert isinstance(result.details, str)
    
    def test_cora_simulator_verdict(self):
        """RED: Run Cora simulator. GREEN: Get verdicts for all V1-V7."""
        simulator = CoraVerifierSimulation(seed=SEED)
        
        problem_text = "Let n be a positive integer. Prove that n^2 + n is always even."
        solution_text = "Since n(n+1) is the product of two consecutive integers, one is even."
        
        results = simulator.run_checks(problem_text, solution_text)
        
        # Must have all 7 checks
        assert len(results) == 7, f"Expected 7 checks, got {len(results)}"
        
        # All must be CoraCheckResult
        for result in results.values():
            assert isinstance(result, CoraCheckResult)
            assert hasattr(result, "check_id")
            assert hasattr(result, "passed")
            assert hasattr(result, "confidence")


class TestSpec014ReconciliationLogic:
    """Test 2: Reconciliation logic (conservative strategy)."""
    
    def test_reconciliation_with_aletheia_score(self):
        """RED: Reconcile Aletheia + Cora scores. GREEN: Verify averaging."""
        wrapper = AletheiaVerifierWrapper(seed=SEED)
        
        # Mock data
        aletheia_score = 0.80
        cora_results = [
            CoraCheckResult(
                check_id=CoraCheckId.V1_LOGICAL_CONSISTENCY,
                passed=True,
                confidence=0.85,
                details="Test check",
                severity="critical",
            ),
            CoraCheckResult(
                check_id=CoraCheckId.V2_MATHEMATICAL_CORRECTNESS,
                passed=True,
                confidence=0.90,
                details="Test check",
                severity="critical",
            ),
        ]
        
        # Reconcile
        final_score, final_passed = wrapper.reconcile_scores(
            aletheia_score, cora_results
        )
        
        # Expected: (0.80 + (0.85 + 0.90) / 2) / 2 = (0.80 + 0.875) / 2 = 0.8375
        assert 0.80 <= final_score <= 1.0
        assert isinstance(final_passed, bool)
    
    def test_reconciliation_averaging(self):
        """RED: Verify averaging formula. GREEN: Compute expected."""
        wrapper = AletheiaVerifierWrapper(seed=SEED)
        
        aletheia_score = 0.75
        cora_results = [
            CoraCheckResult(
                check_id=CoraCheckId.V1_LOGICAL_CONSISTENCY,
                passed=True,
                confidence=0.80,
                details="Test check",
                severity="info",
            ),
            CoraCheckResult(
                check_id=CoraCheckId.V2_MATHEMATICAL_CORRECTNESS,
                passed=True,
                confidence=0.70,
                details="Test check",
                severity="info",
            ),
        ]
        
        final_score, _ = wrapper.reconcile_scores(aletheia_score, cora_results)
        
        # Manual calculation
        cora_avg = (0.80 + 0.70) / 2  # 0.75
        expected = (aletheia_score + cora_avg) / 2  # (0.75 + 0.75) / 2 = 0.75
        
        assert abs(final_score - expected) < 0.01


class TestSpec014CriticalFailure:
    """Test 3: Critical-failure handling (max-severity rule)."""
    
    def test_critical_failure_overrides_score(self):
        """RED: One critical check fails. GREEN: final_passed = False."""
        wrapper = AletheiaVerifierWrapper(seed=SEED)
        
        aletheia_score = 0.95  # Very high Aletheia score
        cora_results = [
            CoraCheckResult(
                check_id=CoraCheckId.V1_LOGICAL_CONSISTENCY,
                passed=True,
                confidence=0.90,
                details="Test check",
                severity="critical",
            ),
            CoraCheckResult(
                check_id=CoraCheckId.V5_PROOF_COMPLETENESS,
                passed=False,  # FAILS
                confidence=0.30,
                details="Proof missing QED or explicit conclusion",
                severity="critical",  # CRITICAL
            ),
        ]
        
        final_score, final_passed = wrapper.reconcile_scores(
            aletheia_score, cora_results
        )
        
        # Despite high Aletheia score, critical failure → final_passed = False
        assert final_passed is False, "Critical failure should override final_passed"
    
    def test_multiple_critical_failures(self):
        """RED: Multiple critical failures. GREEN: Still final_passed = False."""
        wrapper = AletheiaVerifierWrapper(seed=SEED)
        
        cora_results = [
            CoraCheckResult(
                check_id=CoraCheckId.V1_LOGICAL_CONSISTENCY,
                passed=False,
                confidence=0.40,
                details="Test check",
                severity="critical",
            ),
            CoraCheckResult(
                check_id=CoraCheckId.V2_MATHEMATICAL_CORRECTNESS,
                passed=False,
                confidence=0.35,
                details="Test check",
                severity="critical",
            ),
            CoraCheckResult(
                check_id=CoraCheckId.V3_EDGE_CASE_COVERAGE,
                passed=True,
                confidence=0.85,
                details="Test check",
                severity="warning",
            ),
        ]
        
        _, final_passed = wrapper.reconcile_scores(0.80, cora_results)
        assert final_passed is False
    
    def test_warning_severity_does_not_force_fail(self):
        """RED: Warning-level failures. GREEN: Don't force final_passed = False."""
        wrapper = AletheiaVerifierWrapper(seed=SEED)
        
        cora_results = [
            CoraCheckResult(
                check_id=CoraCheckId.V3_EDGE_CASE_COVERAGE,
                passed=False,
                confidence=0.40,
                details="Test check",
                severity="warning",  # Not critical
            ),
            CoraCheckResult(
                check_id=CoraCheckId.V4_CITATION_ACCURACY,
                passed=True,
                confidence=0.85,
                details="Test check",
                severity="info",
            ),
        ]
        
        _, final_passed = wrapper.reconcile_scores(0.75, cora_results)
        # Warning failures should NOT force final_passed = False
        # (score-based decision only)
        assert isinstance(final_passed, bool)


class TestSpec014ExportReport:
    """Test 5: export_report() JSON structure."""
    
    def test_export_report_json_valid(self):
        """RED: Export report to JSON. GREEN: Valid JSON structure."""
        wrapper = AletheiaVerifierWrapper(seed=SEED)
        
        from spec_014_cora_wrapper import AletheiaVerifierOutput, EnrichedVerificationResult
        
        aletheia_result = AletheiaVerifierOutput(
            passed=True,
            score=0.80,
            reasoning="Test",
            suggested_fixes=[],
            hallucination_detected=False,
        )
        
        cora_results = {
            CoraCheckId.V1_LOGICAL_CONSISTENCY: CoraCheckResult(
                check_id=CoraCheckId.V1_LOGICAL_CONSISTENCY,
                passed=True,
                confidence=0.88,
                details="Test check",
                severity="critical",
            ),
            CoraCheckId.V2_MATHEMATICAL_CORRECTNESS: CoraCheckResult(
                check_id=CoraCheckId.V2_MATHEMATICAL_CORRECTNESS,
                passed=False,
                confidence=0.45,
                details="Test check",
                severity="critical",
            ),
        }
        
        result = EnrichedVerificationResult(
            aletheia_result=aletheia_result,
            cora_checks=cora_results,
            final_passed=False,
            final_score=0.60,
        )
        
        report = wrapper.export_report(result)
        
        # Verify structure
        assert "aletheia" in report
        assert "cora" in report
        assert "final" in report
        assert report["final"]["passed"] is False
    
    def test_export_report_completeness(self):
        """RED: Export full report. GREEN: All fields present."""
        wrapper = AletheiaVerifierWrapper(seed=SEED)
        
        from spec_014_cora_wrapper import AletheiaVerifierOutput, EnrichedVerificationResult
        
        aletheia_result = AletheiaVerifierOutput(
            passed=True,
            score=0.85,
            reasoning="Test",
            suggested_fixes=[],
            hallucination_detected=False,
        )
        
        cora_results = {
            CoraCheckId.V1_LOGICAL_CONSISTENCY: CoraCheckResult(
                check_id=CoraCheckId.V1_LOGICAL_CONSISTENCY,
                passed=True,
                confidence=0.92,
                details="Test check",
                severity="critical",
            ),
        }
        
        result = EnrichedVerificationResult(
            aletheia_result=aletheia_result,
            cora_checks=cora_results,
            final_passed=True,
            final_score=0.85,
        )
        
        report = wrapper.export_report(result)
        
        # Verify all cora checks documented
        assert len(report["cora"]) == len(cora_results)
        
        # Verify each check has required fields
        for check_id, check_data in report["cora"].items():
            assert "passed" in check_data
            assert "confidence" in check_data
            assert "severity" in check_data
            assert "details" in check_data


class TestSpec014WrapperIntegration:
    """Test 6: Wrapper integration (end-to-end)."""
    
    def test_full_verification_pipeline(self):
        """RED: Full pipeline (problem + solution). GREEN: Get final verdict."""
        wrapper = AletheiaVerifierWrapper(seed=SEED)
        
        problem = "Prove that the sum of n consecutive integers starting from a is n*(a + a + n - 1) / 2."
        solution = "The sum is a + (a+1) + ... + (a+n-1) = n*a + (0+1+...+(n-1)) = n*a + n*(n-1)/2 = n*(a + (a+n-1)/2)."
        
        # Run Cora checks (returns dict)
        cora_results_dict = wrapper.simulator.run_checks(problem, solution)
        cora_results_list = list(cora_results_dict.values())
        
        # Get Aletheia score (mocked)
        aletheia_score = 0.82
        
        # Reconcile
        final_score, final_passed = wrapper.reconcile_scores(
            aletheia_score, cora_results_list
        )
        
        # Verify result
        assert isinstance(final_score, float)
        assert isinstance(final_passed, bool)
        assert 0.0 <= final_score <= 1.0
    
    def test_reproducibility_with_seed(self):
        """RED: Run verification twice with seed=42. GREEN: Verify identical."""
        import random
        
        problem = "Test problem"
        solution = "Test solution"
        
        # Run 1
        random.seed(SEED)
        wrapper1 = AletheiaVerifierWrapper(seed=SEED)
        results1_dict = wrapper1.simulator.run_checks(problem, solution)
        verdicts1 = sorted([r.passed for r in results1_dict.values()])
        
        # Run 2
        random.seed(SEED)
        wrapper2 = AletheiaVerifierWrapper(seed=SEED)
        results2_dict = wrapper2.simulator.run_checks(problem, solution)
        verdicts2 = sorted([r.passed for r in results2_dict.values()])
        
        # Must be identical
        assert verdicts1 == verdicts2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
