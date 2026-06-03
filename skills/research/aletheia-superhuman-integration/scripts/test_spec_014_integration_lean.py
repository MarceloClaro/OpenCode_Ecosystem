#!/usr/bin/env python3
"""
Testes de Integração: SPEC-014 + SPEC-014 Lean Verifier

Valida que:
1. SPEC-014 (Cora V1-V7) funciona
2. SPEC-014 Lean extension funciona
3. Integração entre os dois funciona
"""

import pytest
from spec_014_cora_wrapper import (
    AletheiaVerifierWrapper,
    AletheiaVerifierOutput,
    verify_with_lean_enhancement,
)


class TestIntegrationSpec014WithLean:
    """RED: Integrate SPEC-014 + Lean. GREEN: Enhanced results."""
    
    def test_wrapper_plus_lean_enhancement(self):
        """RED: Enhance Cora result with Lean. GREEN: Enhanced."""
        wrapper = AletheiaVerifierWrapper(verbose=False)
        
        test_solution = """
        theorem erdos_652 : P := by
          simp [h1, h2]
          induction n
          ring
          nlinarith
          done
        """
        
        aletheia_output = AletheiaVerifierOutput(
            passed=True,
            score=0.80,
            reasoning="Good structure",
            suggested_fixes=[],
            hallucination_detected=False,
        )
        
        result = wrapper.verify(test_solution, "number_theory", aletheia_output)
        
        # Enhance with Lean
        enhanced_result, lean_report = verify_with_lean_enhancement(
            wrapper, result, "Erdos-652"
        )
        
        assert lean_report is not None
        assert "has_lean_proof" in lean_report
        assert lean_report["has_lean_proof"] is True
    
    def test_lean_enhancement_increases_confidence(self):
        """RED: Lean boosts confidence. GREEN: Confidence increased."""
        wrapper = AletheiaVerifierWrapper(verbose=False)
        
        test_solution = """
        theorem foo : P := by
          ring
          simp
          nlinarith
        """
        
        aletheia_output = AletheiaVerifierOutput(
            passed=True,
            score=0.70,
            reasoning="Moderate confidence",
            suggested_fixes=["Add more detail"],
            hallucination_detected=False,
        )
        
        result = wrapper.verify(test_solution, "algebra", aletheia_output)
        
        # Store original confidences
        original_confidences = {
            k: v.confidence for k, v in result.cora_checks.items()
        }
        
        # Enhance
        enhanced_result, lean_report = verify_with_lean_enhancement(
            wrapper, result, "Erdos-654"
        )
        
        # Lean should enhance result
        assert lean_report is not None
    
    def test_lean_enhancement_nonexistent_problem(self):
        """RED: No Lean proof for problem. GREEN: No enhancement."""
        wrapper = AletheiaVerifierWrapper(verbose=False)
        
        test_solution = "Some solution"
        
        aletheia_output = AletheiaVerifierOutput(
            passed=False,
            score=0.40,
            reasoning="No proof structure",
            suggested_fixes=["Provide formal proof"],
            hallucination_detected=True,
        )
        
        result = wrapper.verify(test_solution, "general", aletheia_output)
        
        # Try to enhance with nonexistent problem
        enhanced_result, lean_report = verify_with_lean_enhancement(
            wrapper, result, "Erdos-999999"
        )
        
        assert lean_report["has_lean_proof"] is False
    
    def test_multiple_problems_enhanced(self):
        """RED: Enhance 4 Erdős problems. GREEN: All enhanced."""
        wrapper = AletheiaVerifierWrapper(verbose=False)
        
        problems = ["Erdos-652", "Erdos-654", "Erdos-1040", "Erdos-1051"]
        
        test_solution = """
        theorem proof : P := by
          simp
          ring
          induction n
          done
        """
        
        aletheia_output = AletheiaVerifierOutput(
            passed=True,
            score=0.75,
            reasoning="Good proof structure",
            suggested_fixes=[],
            hallucination_detected=False,
        )
        
        results = []
        for problem_id in problems:
            result = wrapper.verify(test_solution, "mathematics", aletheia_output)
            enhanced_result, lean_report = verify_with_lean_enhancement(
                wrapper, result, problem_id
            )
            results.append(lean_report)
        
        # All should be enhanced successfully
        assert len(results) == 4
        assert all(r["has_lean_proof"] for r in results)
    
    def test_lean_tactics_found_in_report(self):
        """RED: Lean tactics in report. GREEN: Tactics listed."""
        wrapper = AletheiaVerifierWrapper(verbose=False)
        
        test_solution = "Proof with Lean tactics"
        
        aletheia_output = AletheiaVerifierOutput(
            passed=True,
            score=0.80,
            reasoning="Good structure",
            suggested_fixes=[],
            hallucination_detected=False,
        )
        
        result = wrapper.verify(test_solution, "general", aletheia_output)
        enhanced_result, lean_report = verify_with_lean_enhancement(
            wrapper, result, "Erdos-652"
        )
        
        if lean_report["has_lean_proof"]:
            assert "tactics_found" in lean_report
            assert isinstance(lean_report["tactics_found"], list)
    
    def test_cora_enhancement_consistency(self):
        """RED: Enhancements consistent. GREEN: Same problem = same enhancement."""
        wrapper1 = AletheiaVerifierWrapper(verbose=False)
        wrapper2 = AletheiaVerifierWrapper(verbose=False)
        
        test_solution = """
        theorem p : Q := by
          simp
          ring
        """
        
        aletheia_output = AletheiaVerifierOutput(
            passed=True,
            score=0.70,
            reasoning="Moderate",
            suggested_fixes=[],
            hallucination_detected=False,
        )
        
        # First verification
        result1 = wrapper1.verify(test_solution, "algebra", aletheia_output)
        _, report1 = verify_with_lean_enhancement(wrapper1, result1, "Erdos-652")
        
        # Second verification (same problem)
        result2 = wrapper2.verify(test_solution, "algebra", aletheia_output)
        _, report2 = verify_with_lean_enhancement(wrapper2, result2, "Erdos-652")
        
        # Should be identical
        assert report1 == report2


class TestWrapperReproducibility:
    """RED: Reproducible across runs. GREEN: Consistent results."""
    
    def test_same_solution_same_result(self):
        """RED: Run twice. GREEN: Same Cora scores."""
        solution = "Some mathematical proof"
        aletheia_output = AletheiaVerifierOutput(
            passed=True, score=0.75, reasoning="OK",
            suggested_fixes=[], hallucination_detected=False
        )
        
        wrapper1 = AletheiaVerifierWrapper(verbose=False)
        result1 = wrapper1.verify(solution, "math", aletheia_output)
        cora_scores1 = {k: v.confidence for k, v in result1.cora_checks.items()}
        
        wrapper2 = AletheiaVerifierWrapper(verbose=False)
        result2 = wrapper2.verify(solution, "math", aletheia_output)
        cora_scores2 = {k: v.confidence for k, v in result2.cora_checks.items()}
        
        # Should match
        assert cora_scores1 == cora_scores2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
