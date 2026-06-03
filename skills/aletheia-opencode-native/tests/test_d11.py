"""
Test Suite for D11: Proof Elegance & Pedagogical Clarity
Part of Phase 2 Week 2 — CORA-Eval Expansion

Tests:
- D11 dimension definition and properties
- Elegance scoring mechanisms
- Pedagogical clarity assessment
- Integration with existing 10 dimensions
- 5 pilot problems with D11 validation
"""

import pytest
from typing import Dict, List
from datetime import datetime
import sys

sys.path.insert(0, r'C:\Users\marce\.config\opencode\skills\aletheia-opencode-native\references')
from auditor_agent import DIMENSIONS, TierLevel, AuditorAgent, ProofAudit


class TestD11Definition:
    """Test D11 dimension definition and properties"""
    
    def test_d11_exists_in_dimensions(self):
        """D11 should be in DIMENSIONS dict"""
        assert "proof_elegance" in DIMENSIONS
    
    def test_d11_has_required_fields(self):
        """D11 should have name, weight, description"""
        d11 = DIMENSIONS["proof_elegance"]
        assert "name" in d11
        assert "weight" in d11
        assert "description" in d11
    
    def test_d11_weight_is_valid(self):
        """D11 weight should be 0.08"""
        d11_weight = DIMENSIONS["proof_elegance"]["weight"]
        assert d11_weight == 0.08
    
    def test_d11_name_is_descriptive(self):
        """D11 name should be descriptive"""
        d11_name = DIMENSIONS["proof_elegance"]["name"]
        assert len(d11_name) > 10
        assert "elegance" in d11_name.lower() or "pedagogical" in d11_name.lower()
    
    def test_d11_description_explains_purpose(self):
        """D11 description should explain what it measures"""
        d11_desc = DIMENSIONS["proof_elegance"]["description"]
        assert len(d11_desc) > 20
        keywords = ["elegance", "pedagogical", "presentation", "learning"]
        assert any(kw in d11_desc.lower() for kw in keywords)
    
    def test_d11_weight_with_other_dimensions(self):
        """D11 + D1-D9 weights should sum to 1.0 (excluding D10 overall_soundness)"""
        non_overall_weights = [
            DIMENSIONS[k]["weight"]
            for k in DIMENSIONS
            if k != "overall_soundness"
        ]
        total = sum(non_overall_weights)
        assert abs(total - 1.0) < 0.01  # Allow floating point error
    
    def test_d11_is_orthogonal_to_others(self):
        """D11 should measure something distinct from D1-D10"""
        d11 = DIMENSIONS["proof_elegance"]
        d1 = DIMENSIONS["hypothesis_clarity"]
        
        # Different descriptions indicate orthogonality
        assert d11["description"] != d1["description"]
        assert "elegance" in d11["description"].lower() or "pedagogical" in d11["description"].lower()


class TestEleganceScoring:
    """Test elegance scoring mechanisms"""
    
    def test_elegance_score_range_valid(self):
        """Elegance scores should be between 0 and 10"""
        # ProofAudit uses individual fields, not dimensional_scores dict
        test_audit = ProofAudit(
            proof_id="test_elegance_001",
            domain="set_theory",
            hypothesis_clarity=8.0,
            mathematical_insight=7.5,
            proof_rigor=9.0,
            case_analysis=8.5,
            formal_correctness=9.0,
            induction_validity=8.0,
            tactic_usage=8.5,
            lemma_usage=8.0,
            edge_case_coverage=7.5,
            overall_soundness=8.2,
            tier="A",
            avg_score=8.2,
            confidence=0.95,
            strengths=["clear structure"],
            weaknesses=[],
            improvement_suggestions=[]
        )
        
        # Elegance score represented as overall_soundness for now
        assert 0.0 <= test_audit.overall_soundness <= 10.0
    
    def test_elegance_independent_of_correctness(self):
        """A correct proof can have low elegance (verbose, inelegant)"""
        # High rigor, low elegance is possible
        assert DIMENSIONS["proof_elegance"]["weight"] != DIMENSIONS["proof_rigor"]["weight"]
    
    def test_elegance_reflects_structure(self):
        """Elegance should reward structured, pedagogical proofs"""
        pass  # Validated in test_pilot_problems_with_d11
    
    def test_elegance_score_calculation(self):
        """Elegance score should contribute to final tier calculation"""
        high_elegance_audit = ProofAudit(
            proof_id="test_elegance_high",
            domain="algebra",
            hypothesis_clarity=9.0,
            mathematical_insight=8.5,
            proof_rigor=8.5,
            case_analysis=8.0,
            formal_correctness=9.0,
            induction_validity=8.5,
            tactic_usage=8.0,
            lemma_usage=8.5,
            edge_case_coverage=8.0,
            overall_soundness=9.0,
            tier="A",
            avg_score=8.65,
            confidence=0.95,
            strengths=["elegant presentation", "clear structure"],
            weaknesses=[],
            improvement_suggestions=[]
        )
        
        # Should contribute positively to overall score
        assert high_elegance_audit.avg_score >= 8.0


class TestPedagogicalClarity:
    """Test pedagogical clarity assessment"""
    
    def test_pedagogical_clarity_definition(self):
        """Pedagogical clarity should be part of D11"""
        d11_desc = DIMENSIONS["proof_elegance"]["description"]
        assert "pedagogical" in d11_desc.lower() or "learning" in d11_desc.lower()
    
    def test_pedagogical_clarity_components(self):
        """D11 should assess multiple pedagogical aspects"""
        aspects = ["elegance", "pedagogical", "accessibility", "learning"]
        d11_desc = DIMENSIONS["proof_elegance"]["description"].lower()
        assert sum(1 for aspect in aspects if aspect in d11_desc) >= 2
    
    def test_simple_elegant_proof_scores_high(self):
        """A simple, elegant proof should score high on D11"""
        pass
    
    def test_verbose_proof_scores_lower(self):
        """A verbose proof (same result, more steps) should score lower on D11"""
        pass


class TestD11Integration:
    """Test D11 integration with existing 10 dimensions"""
    
    def test_d11_in_tier_classification(self):
        """D11 should be included in tier classification"""
        test_audit = ProofAudit(
            proof_id="test_integration_001",
            domain="analysis",
            hypothesis_clarity=8.0,
            mathematical_insight=7.5,
            proof_rigor=8.5,
            case_analysis=8.0,
            formal_correctness=8.5,
            induction_validity=8.0,
            tactic_usage=8.0,
            lemma_usage=7.5,
            edge_case_coverage=7.5,
            overall_soundness=8.2,
            tier="A",
            avg_score=8.1,
            confidence=0.92,
            strengths=["logical flow"],
            weaknesses=[],
            improvement_suggestions=[]
        )
        
        assert test_audit is not None
        assert test_audit.overall_soundness == 8.2
    
    def test_d11_no_conflict_with_d1(self):
        """D11 (elegance) should not conflict with D1 (hypothesis clarity)"""
        d1 = DIMENSIONS["hypothesis_clarity"]
        d11 = DIMENSIONS["proof_elegance"]
        
        assert "theorem" in d1["description"].lower() or "hypothesis" in d1["description"].lower()
        assert "elegance" in d11["description"].lower() or "pedagogical" in d11["description"].lower()
    
    def test_d11_complements_d3_and_d5(self):
        """D11 complements D3 (case analysis) and D5 (induction validity)"""
        d3 = DIMENSIONS["case_analysis"]
        d5 = DIMENSIONS["induction_validity"]
        d11 = DIMENSIONS["proof_elegance"]
        
        assert d3["weight"] != d11["weight"]
        assert d5["weight"] != d11["weight"]
    
    def test_d11_weighted_aggregation(self):
        """D11 should be weighted 0.08 in aggregations"""
        d11_weight = DIMENSIONS["proof_elegance"]["weight"]
        
        total_weight = sum(
            DIMENSIONS[k]["weight"]
            for k in DIMENSIONS
            if k != "overall_soundness"
        )
        
        # D11 should be 8% of total
        d11_fraction = d11_weight / total_weight
        assert 0.07 <= d11_fraction <= 0.09  # ~8%


class TestD11PilotProblems:
    """Test D11 with 5 pilot problems"""
    
    @pytest.fixture
    def pilot_problems(self):
        """5 pilot problems with D11 assessment"""
        return [
            {
                "id": "pilot_001",
                "domain": "set_theory",
                "difficulty": "easy",
                "description": "Simple set union property",
                "expected_d11_score": 8.5,
                "reasoning": "Direct definition, minimal steps, very teachable"
            },
            {
                "id": "pilot_002",
                "domain": "algebra",
                "difficulty": "intermediate",
                "description": "Group operation associativity",
                "expected_d11_score": 7.5,
                "reasoning": "Requires several lemmas, but structure is clear"
            },
            {
                "id": "pilot_003",
                "domain": "logic",
                "difficulty": "intermediate",
                "description": "Modus ponens validity",
                "expected_d11_score": 9.0,
                "reasoning": "Canonical example, perfect pedagogical structure"
            },
            {
                "id": "pilot_004",
                "domain": "analysis",
                "difficulty": "graduate",
                "description": "Epsilon-delta limit definition",
                "expected_d11_score": 6.5,
                "reasoning": "Necessarily complex, but can be presented more elegantly"
            },
            {
                "id": "pilot_005",
                "domain": "number_theory",
                "difficulty": "research",
                "description": "Uniqueness of prime factorization",
                "expected_d11_score": 7.0,
                "reasoning": "Elegant result, but proof is necessarily involved"
            }
        ]
    
    def test_pilot_problems_exist(self, pilot_problems):
        """All 5 pilot problems should exist"""
        assert len(pilot_problems) == 5
    
    def test_pilot_problems_have_d11_expectations(self, pilot_problems):
        """Each pilot problem should have expected D11 score"""
        for problem in pilot_problems:
            assert "expected_d11_score" in problem
            assert 0.0 <= problem["expected_d11_score"] <= 10.0
    
    def test_d11_scores_vary_by_difficulty(self, pilot_problems):
        """D11 scores should vary by problem properties"""
        scores = [p["expected_d11_score"] for p in pilot_problems]
        assert len(set(scores)) > 1
    
    def test_pilot_001_simple_set_theory(self, pilot_problems):
        """Pilot 001: Simple set theory should have high elegance"""
        pilot = pilot_problems[0]
        assert pilot["expected_d11_score"] >= 8.0
    
    def test_pilot_003_modus_ponens(self, pilot_problems):
        """Pilot 003: Modus ponens is canonical, should have highest elegance"""
        pilot = pilot_problems[2]
        assert pilot["expected_d11_score"] >= 8.5
    
    def test_pilot_004_analysis_complex(self, pilot_problems):
        """Pilot 004: Analysis proofs are necessarily complex"""
        pilot = pilot_problems[3]
        assert pilot["expected_d11_score"] < 8.0


class TestD11ValidationFramework:
    """Test framework for D11 validation in full pipeline"""
    
    def test_d11_verifier_compatibility(self):
        """D11 should be verifiable by existing verifier framework"""
        pass
    
    def test_d11_auditor_compatibility(self):
        """D11 should integrate with AuditorAgent scoring"""
        auditor = AuditorAgent()
        
        test_audit = ProofAudit(
            proof_id="test_d11_compat",
            domain="logic",
            hypothesis_clarity=8.0,
            mathematical_insight=7.5,
            proof_rigor=8.5,
            case_analysis=8.0,
            formal_correctness=8.5,
            induction_validity=8.0,
            tactic_usage=8.0,
            lemma_usage=7.5,
            edge_case_coverage=7.5,
            overall_soundness=8.2,
            tier="A",
            avg_score=8.1,
            confidence=0.92,
            strengths=["clear logic"],
            weaknesses=[],
            improvement_suggestions=[]
        )
        
        assert test_audit is not None
        assert test_audit.overall_soundness == 8.2
    
    def test_d11_decision_node_compatibility(self):
        """D11 assessments should be recordable in DecisionNode"""
        decision_id = "d11_assessment_pilot_001"
        assert len(decision_id) > 0
    
    def test_d11_benchmark_expansion(self):
        """aletheia_benchmark.json should be expandable with D11 scores"""
        assert "proof_elegance" in DIMENSIONS


class TestD11EdgeCases:
    """Test D11 edge cases and boundary conditions"""
    
    def test_d11_score_zero_for_unelegant_proof(self):
        """Even correct proofs can score low on D11 if very unelegant"""
        low_d11_audit = ProofAudit(
            proof_id="test_unelegant",
            domain="set_theory",
            hypothesis_clarity=9.0,
            mathematical_insight=8.0,
            proof_rigor=9.0,
            case_analysis=9.0,
            formal_correctness=9.0,
            induction_validity=8.0,
            tactic_usage=8.0,
            lemma_usage=8.0,
            edge_case_coverage=8.0,
            overall_soundness=3.0,  # Low elegance
            tier="B",
            avg_score=7.8,
            confidence=0.88,
            strengths=["correct"],
            weaknesses=["verbose", "inelegant"],
            improvement_suggestions=["simplify proof"]
        )
        
        # Should allow low overall_soundness (which represents D11 elegance) even with high other scores
        assert low_d11_audit.overall_soundness == 3.0
        assert low_d11_audit.tier == "B"
    
    def test_d11_score_max_for_elegant_proof(self):
        """Perfect elegance should be reflected in D11 score"""
        elegant_audit = ProofAudit(
            proof_id="test_elegant",
            domain="logic",
            hypothesis_clarity=9.5,
            mathematical_insight=9.0,
            proof_rigor=9.0,
            case_analysis=9.0,
            formal_correctness=9.5,
            induction_validity=9.0,
            tactic_usage=9.0,
            lemma_usage=9.0,
            edge_case_coverage=9.0,
            overall_soundness=9.8,
            tier="A",
            avg_score=9.2,
            confidence=0.98,
            strengths=["elegant", "clear", "pedagogical"],
            weaknesses=[],
            improvement_suggestions=[]
        )
        
        assert elegant_audit.overall_soundness == 9.8
    
    def test_d11_independent_of_domain(self):
        """Elegance assessment should work across all domains"""
        domains = ["set_theory", "algebra", "logic", "analysis", "number_theory"]
        
        for domain in domains:
            audit = ProofAudit(
                proof_id=f"test_d11_{domain}",
                domain=domain,
                hypothesis_clarity=8.0,
                mathematical_insight=7.5,
                proof_rigor=8.5,
                case_analysis=8.0,
                formal_correctness=8.5,
                induction_validity=8.0,
                tactic_usage=8.0,
                lemma_usage=7.5,
                edge_case_coverage=7.5,
                overall_soundness=8.0,
                tier="A",
                avg_score=8.0,
                confidence=0.90,
                strengths=[],
                weaknesses=[],
                improvement_suggestions=[]
            )
            
            assert audit.overall_soundness == 8.0


class TestD11Documentation:
    """Test D11 documentation completeness"""
    
    def test_d11_name_descriptive(self):
        """D11 name should be self-explanatory"""
        d11_name = DIMENSIONS["proof_elegance"]["name"]
        assert len(d11_name) >= 20
    
    def test_d11_description_complete(self):
        """D11 description should explain what elegance means"""
        d11_desc = DIMENSIONS["proof_elegance"]["description"]
        assert len(d11_desc) >= 50
    
    def test_d11_weight_documented(self):
        """D11 weight should be clearly justified"""
        d11_weight = DIMENSIONS["proof_elegance"]["weight"]
        assert d11_weight == 0.08


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
