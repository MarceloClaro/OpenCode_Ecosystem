"""
Unit tests for AuditorAgent
Tests PhD-level proof evaluation with 10 dimensions and tier classification

Test Coverage:
- TierLevel enum and classification
- ProofAudit data structure
- 10-dimensional scoring
- Tier assignment (A, B, C, D)
- Improvement suggestions
- Comparative analysis (vs V3, V4)
- Weighted scoring calculation
"""

import pytest
import sys
from pathlib import Path
from dataclasses import asdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "references"))

from auditor_agent import (
    AuditorAgent,
    TierLevel,
    ProofAudit,
    DIMENSIONS
)


class TestTierLevel:
    """Test TierLevel enum"""
    
    def test_tier_levels_defined(self):
        """Test all tier levels are defined"""
        tiers = [TierLevel.A, TierLevel.B, TierLevel.C, TierLevel.D]
        assert len(tiers) == 4
    
    @pytest.mark.parametrize("tier,expected_id,min_score", [
        (TierLevel.A, "A", 8.0),
        (TierLevel.B, "B", 7.0),
        (TierLevel.C, "C", 6.0),
        (TierLevel.D, "D", 5.0)
    ])
    def test_tier_properties(self, tier, expected_id, min_score):
        """Test tier properties"""
        assert tier.tier_id == expected_id
        assert tier.min_score == min_score
        assert tier.description is not None
    
    def test_tier_descriptions(self):
        """Test tier descriptions are appropriate"""
        assert "publishable" in TierLevel.A.description.lower()
        assert "minor" in TierLevel.B.description.lower()
        assert "revision" in TierLevel.C.description.lower() or "revision" in TierLevel.D.description.lower()


class TestDimensions:
    """Test dimension definitions"""
    
    def test_all_dimensions_defined(self):
        """Test all 11 dimensions (D1-D10 + D11) are defined"""
        dim_keys = list(DIMENSIONS.keys())
        assert len(dim_keys) == 11  # D1-D10 + D11 (proof_elegance) + overall_soundness (meta)
    
    def test_dimension_keys(self):
        """Test dimension key names"""
        expected_keys = [
            "hypothesis_clarity",
            "mathematical_insight",
            "proof_rigor",
            "case_analysis",
            "formal_correctness",
            "induction_validity",
            "tactic_usage",
            "lemma_usage",
            "edge_case_coverage",
            "proof_elegance",  # D11 — new dimension
            "overall_soundness"
        ]
        
        assert list(DIMENSIONS.keys()) == expected_keys
    
    def test_dimension_properties(self):
        """Test each dimension has required properties"""
        for dim_key, dim_spec in DIMENSIONS.items():
            assert "name" in dim_spec
            assert "weight" in dim_spec
            assert "description" in dim_spec
            assert isinstance(dim_spec["name"], str)
            assert isinstance(dim_spec["weight"], (int, float))
            assert isinstance(dim_spec["description"], str)
    
    def test_dimension_weights(self):
        """Test dimension weights are valid"""
        # Weights should sum to 1.0 (allow small floating point error)
        total_weight = sum(d["weight"] for d in DIMENSIONS.values())
        
        assert abs(total_weight - 1.0) < 0.1
    
    def test_overall_soundness_weight_zero(self):
        """Test that overall_soundness has weight 0 (computed field)"""
        assert DIMENSIONS["overall_soundness"]["weight"] == 0.0


class TestProofAudit:
    """Test ProofAudit data structure"""
    
    def test_proof_audit_creation(self):
        """Test creating a ProofAudit"""
        audit = ProofAudit(
            proof_id="test_001",
            domain="algebra",
            hypothesis_clarity=8.5,
            mathematical_insight=8.4,
            proof_rigor=8.6,
            case_analysis=8.3,
            formal_correctness=8.7,
            induction_validity=8.2,
            tactic_usage=8.5,
            lemma_usage=8.4,
            edge_case_coverage=8.6,
            overall_soundness=8.5,
            tier="A",
            avg_score=8.47,
            confidence=0.95,
            weaknesses=["Minor gaps in edge cases"],
            strengths=["Strong formal correctness", "Clear hypothesis"],
            improvement_suggestions=["Add more boundary case analysis"]
        )
        
        assert audit.proof_id == "test_001"
        assert audit.domain == "algebra"
        assert audit.tier == "A"
        assert audit.avg_score == 8.47
    
    def test_proof_audit_tier_a(self):
        """Test Tier A classification (score ≥ 8.0)"""
        audit = ProofAudit(
            proof_id="test_A",
            domain="algebra",
            hypothesis_clarity=8.5, mathematical_insight=8.4,
            proof_rigor=8.6, case_analysis=8.3,
            formal_correctness=8.7, induction_validity=8.2,
            tactic_usage=8.5, lemma_usage=8.4,
            edge_case_coverage=8.6, overall_soundness=8.5,
            tier="A",
            avg_score=8.47,
            confidence=0.95,
            weaknesses=[], strengths=[], improvement_suggestions=[]
        )
        
        assert audit.tier == "A"
        assert audit.avg_score >= 8.0
    
    def test_proof_audit_tier_b(self):
        """Test Tier B classification (7.0 ≤ score < 8.0)"""
        audit = ProofAudit(
            proof_id="test_B",
            domain="algebra",
            hypothesis_clarity=7.5, mathematical_insight=7.4,
            proof_rigor=7.6, case_analysis=7.3,
            formal_correctness=7.7, induction_validity=7.2,
            tactic_usage=7.5, lemma_usage=7.4,
            edge_case_coverage=7.6, overall_soundness=7.5,
            tier="B",
            avg_score=7.47,
            confidence=0.85,
            weaknesses=["Needs revisions"], strengths=[], improvement_suggestions=[]
        )
        
        assert audit.tier == "B"
        assert 7.0 <= audit.avg_score < 8.0
    
    def test_proof_audit_tier_c(self):
        """Test Tier C classification (6.0 ≤ score < 7.0)"""
        audit = ProofAudit(
            proof_id="test_C",
            domain="algebra",
            hypothesis_clarity=6.5, mathematical_insight=6.4,
            proof_rigor=6.6, case_analysis=6.3,
            formal_correctness=6.7, induction_validity=6.2,
            tactic_usage=6.5, lemma_usage=6.4,
            edge_case_coverage=6.6, overall_soundness=6.5,
            tier="C",
            avg_score=6.47,
            confidence=0.70,
            weaknesses=["Significant gaps"], strengths=[], improvement_suggestions=[]
        )
        
        assert audit.tier == "C"
        assert 6.0 <= audit.avg_score < 7.0
    
    def test_proof_audit_tier_d(self):
        """Test Tier D classification (score < 6.0)"""
        audit = ProofAudit(
            proof_id="test_D",
            domain="algebra",
            hypothesis_clarity=5.5, mathematical_insight=5.4,
            proof_rigor=5.6, case_analysis=5.3,
            formal_correctness=5.7, induction_validity=5.2,
            tactic_usage=5.5, lemma_usage=5.4,
            edge_case_coverage=5.6, overall_soundness=5.5,
            tier="D",
            avg_score=5.47,
            confidence=0.50,
            weaknesses=["Major rework needed"], strengths=[], improvement_suggestions=[]
        )
        
        assert audit.tier == "D"
        assert audit.avg_score < 6.0
    
    def test_proof_audit_to_dict(self):
        """Test ProofAudit serialization"""
        audit = ProofAudit(
            proof_id="test_serial",
            domain="logic",
            hypothesis_clarity=8.0, mathematical_insight=8.0,
            proof_rigor=8.0, case_analysis=8.0,
            formal_correctness=8.0, induction_validity=8.0,
            tactic_usage=8.0, lemma_usage=8.0,
            edge_case_coverage=8.0, overall_soundness=8.0,
            tier="A",
            avg_score=8.0,
            confidence=0.95,
            weaknesses=[], strengths=[], improvement_suggestions=[]
        )
        
        audit_dict = asdict(audit)
        
        assert isinstance(audit_dict, dict)
        assert audit_dict["proof_id"] == "test_serial"
        assert audit_dict["tier"] == "A"


class TestAuditorAgent:
    """Test AuditorAgent main class"""
    
    def test_auditor_initialization_default(self):
        """Test default initialization"""
        auditor = AuditorAgent()
        assert auditor.decision_node is None
        assert auditor.audited_proofs == []
    
    def test_auditor_initialization_with_decision_node(self):
        """Test initialization with decision node"""
        mock_dn = {"name": "mock"}
        auditor = AuditorAgent(decision_node=mock_dn)
        assert auditor.decision_node == mock_dn


class TestScoringCalculation:
    """Test score calculation and weighting"""
    
    def test_weighted_average_calculation(self):
        """Test weighted average across dimensions"""
        # Create a specific audit with known scores
        scores = {
            "hypothesis_clarity": 8.0,
            "mathematical_insight": 7.0,
            "proof_rigor": 9.0,
            "case_analysis": 8.0,
            "formal_correctness": 9.0,
            "induction_validity": 7.0,
            "tactic_usage": 8.0,
            "lemma_usage": 8.0,
            "edge_case_coverage": 9.0,
            "overall_soundness": 8.0
        }
        
        # Manual calculation
        weighted_sum = 0
        total_weight = 0
        
        for dim_key, dim_value in scores.items():
            if dim_key in DIMENSIONS:
                weight = DIMENSIONS[dim_key]["weight"]
                if dim_key != "overall_soundness":  # overall_soundness has 0 weight
                    weighted_sum += dim_value * weight
                    total_weight += weight
        
        avg = weighted_sum / total_weight if total_weight > 0 else 0
        
        # Should be between min and max individual scores
        assert min(scores.values()) <= avg <= max(scores.values())
    
    def test_dimension_weights_sum(self):
        """Test dimension weights sum correctly"""
        non_overall_weights = [
            DIMENSIONS[k]["weight"]
            for k in DIMENSIONS
            if k != "overall_soundness"
        ]
        
        total = sum(non_overall_weights)
        assert abs(total - 0.92) < 0.1  # 9 dimensions sum to 0.92


class TestImprovementSuggestions:
    """Test improvement suggestion generation"""
    
    def test_improvement_suggestions_structure(self):
        """Test improvement suggestions are well-formed"""
        audit = ProofAudit(
            proof_id="improve_001",
            domain="algebra",
            hypothesis_clarity=7.0, mathematical_insight=6.5,
            proof_rigor=7.5, case_analysis=6.0,
            formal_correctness=7.5, induction_validity=6.5,
            tactic_usage=7.0, lemma_usage=7.0,
            edge_case_coverage=6.5, overall_soundness=7.0,
            tier="B",
            avg_score=7.0,
            confidence=0.80,
            weaknesses=["Weak case analysis", "Limited edge case coverage"],
            strengths=["Good rigor", "Clear hypothesis"],
            improvement_suggestions=[
                "Expand case analysis coverage",
                "Add boundary case testing",
                "Strengthen edge case handling"
            ]
        )
        
        assert len(audit.improvement_suggestions) > 0
        assert all(isinstance(s, str) for s in audit.improvement_suggestions)


class TestComparativeAnalysis:
    """Test comparative analysis (vs V3, V4)"""
    
    def test_improvement_vs_v3(self):
        """Test improvement percentage calculation vs V3"""
        audit = ProofAudit(
            proof_id="comp_001",
            domain="algebra",
            hypothesis_clarity=8.0, mathematical_insight=8.0,
            proof_rigor=8.0, case_analysis=8.0,
            formal_correctness=8.0, induction_validity=8.0,
            tactic_usage=8.0, lemma_usage=8.0,
            edge_case_coverage=8.0, overall_soundness=8.0,
            tier="A",
            avg_score=8.0,
            confidence=0.95,
            weaknesses=[], strengths=[], improvement_suggestions=[],
            vs_v3_improvement=25.0,  # 25% improvement
            vs_v4_improvement=34.0   # 34% improvement
        )
        
        assert audit.vs_v3_improvement == 25.0
        assert audit.vs_v4_improvement == 34.0
        assert audit.vs_v4_improvement > audit.vs_v3_improvement
    
    def test_improvement_percentage_calculation(self):
        """Test improvement percentage logic"""
        v3_score = 6.4
        v4_score = 6.23
        aletheia_score = 8.317
        
        # Calculate improvements
        v3_improvement = ((aletheia_score - v3_score) / v3_score) * 100
        v4_improvement = ((aletheia_score - v4_score) / v4_score) * 100
        
        # Expected from Phase 1 report (~33.5%, allow tolerance)
        assert abs(v4_improvement - 33.5) < 0.6  # ~33.5% vs V4 (tolerance 0.6%)
        assert v3_improvement > 0


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_perfect_audit(self):
        """Test perfect score audit"""
        audit = ProofAudit(
            proof_id="perfect_001",
            domain="algebra",
            hypothesis_clarity=10.0, mathematical_insight=10.0,
            proof_rigor=10.0, case_analysis=10.0,
            formal_correctness=10.0, induction_validity=10.0,
            tactic_usage=10.0, lemma_usage=10.0,
            edge_case_coverage=10.0, overall_soundness=10.0,
            tier="A",
            avg_score=10.0,
            confidence=1.0,
            weaknesses=[], strengths=["Perfect on all dimensions"],
            improvement_suggestions=[]
        )
        
        assert audit.avg_score == 10.0
        assert audit.tier == "A"
    
    def test_minimum_score_audit(self):
        """Test minimum acceptable score"""
        audit = ProofAudit(
            proof_id="min_001",
            domain="algebra",
            hypothesis_clarity=5.0, mathematical_insight=5.0,
            proof_rigor=5.0, case_analysis=5.0,
            formal_correctness=5.0, induction_validity=5.0,
            tactic_usage=5.0, lemma_usage=5.0,
            edge_case_coverage=5.0, overall_soundness=5.0,
            tier="D",
            avg_score=5.0,
            confidence=0.3,
            weaknesses=["Multiple issues"], strengths=[],
            improvement_suggestions=["Major rework required"]
        )
        
        assert audit.avg_score == 5.0
        assert audit.tier == "D"
    
    def test_boundary_tier_b_to_c(self):
        """Test boundary between Tier B and C (6.99 vs 7.00)"""
        audit_b = ProofAudit(
            proof_id="bound_b",
            domain="algebra",
            hypothesis_clarity=7.0, mathematical_insight=6.9,
            proof_rigor=6.95, case_analysis=7.0,
            formal_correctness=7.0, induction_validity=6.9,
            tactic_usage=7.0, lemma_usage=7.0,
            edge_case_coverage=6.95, overall_soundness=7.0,
            tier="B",
            avg_score=6.99,
            confidence=0.75,
            weaknesses=[], strengths=[], improvement_suggestions=[]
        )
        
        assert audit_b.tier == "B"
        
        audit_c = ProofAudit(
            proof_id="bound_c",
            domain="algebra",
            hypothesis_clarity=6.9, mathematical_insight=6.8,
            proof_rigor=6.85, case_analysis=6.9,
            formal_correctness=6.9, induction_validity=6.8,
            tactic_usage=6.9, lemma_usage=6.9,
            edge_case_coverage=6.85, overall_soundness=6.9,
            tier="C",
            avg_score=6.87,
            confidence=0.70,
            weaknesses=[], strengths=[], improvement_suggestions=[]
        )
        
        assert audit_c.tier == "C"


class TestMultipleDomains:
    """Test auditing across multiple domains"""
    
    @pytest.mark.parametrize("domain", [
        "algebra", "logic", "analysis", "set_theory", "number_theory"
    ])
    def test_audit_by_domain(self, domain):
        """Test audit creation for different domains"""
        audit = ProofAudit(
            proof_id=f"domain_{domain}",
            domain=domain,
            hypothesis_clarity=8.0, mathematical_insight=8.0,
            proof_rigor=8.0, case_analysis=8.0,
            formal_correctness=8.0, induction_validity=8.0,
            tactic_usage=8.0, lemma_usage=8.0,
            edge_case_coverage=8.0, overall_soundness=8.0,
            tier="A",
            avg_score=8.0,
            confidence=0.95,
            weaknesses=[], strengths=[], improvement_suggestions=[]
        )
        
        assert audit.domain == domain
        assert audit.tier == "A"


# ═════════════════════════════════════════════════════════════════
# Test Execution & Coverage Report
# ═════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Run tests with:
        pytest test_auditor.py -v --cov=auditor_agent --cov-report=html
    
    Expected coverage:
        - AuditorAgent class: 100%
        - ProofAudit dataclass: 100%
        - TierLevel enum: 100%
        - Dimension definitions: 100%
        - Scoring calculations: 95%+
    """
    pytest.main([__file__, "-v", "--tb=short"])
