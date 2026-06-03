"""
Test Suite for Aletheia V7 Verifier
Cora-Debate V7: D11 Proof Elegance & Pedagogical Clarity Assessment

Tests: 15 test cases covering structure analysis, pedagogical assessment,
       and D11 scoring for 5 pilot domains
"""

import pytest
import sys
from pathlib import Path

# Add references directory to path
refs_dir = Path(__file__).parent.parent / "references"
sys.path.insert(0, str(refs_dir))

from verifier_v7 import (
    VerifierV7,
    ProofStructure,
    PedagogicalAssessment,
    D11Assessment,
    EleganceLevel
)


class TestV7ProofStructureParsing:
    """Tests for proof structure extraction"""
    
    def test_parse_empty_proof(self):
        """Test parsing empty proof"""
        v7 = VerifierV7()
        structure = v7.parse_proof_structure("")
        
        assert structure.total_lines == 0
        assert structure.lemma_count == 0
        assert structure.case_count == 0
        assert structure.tactic_count == 0
    
    def test_parse_simple_proof(self):
        """Test parsing simple one-liner proof"""
        v7 = VerifierV7()
        proof_text = "theorem union_idempotent: A ∪ A = A := by simp"
        structure = v7.parse_proof_structure(proof_text)
        
        assert structure.total_lines > 0
        assert "union_idempotent" in structure.lemma_names
        assert "simp" in structure.tactic_types
    
    def test_parse_multi_lemma_proof(self):
        """Test parsing proof with multiple lemmas"""
        v7 = VerifierV7()
        proof_text = """
        lemma helper_1: P → Q := by simp
        lemma helper_2: Q → R := by exact sorry
        theorem main: P → R := by
          intro p
          apply helper_2
          exact helper_1 p
        """
        structure = v7.parse_proof_structure(proof_text)
        
        assert structure.lemma_count >= 3
        assert "helper_1" in structure.lemma_names
        assert "helper_2" in structure.lemma_names
        assert "main" in structure.lemma_names
    
    def test_parse_case_analysis(self):
        """Test parsing proof with case analysis"""
        v7 = VerifierV7()
        proof_text = """
        theorem cases_example: P ∨ Q → R := by
          intro h
          cases h with
          | inl hp => -- Case 1: P holds
            exact from_p hp
          | inr hq => -- Case 2: Q holds
            exact from_q hq
        """
        structure = v7.parse_proof_structure(proof_text)
        
        assert structure.case_count >= 2
        assert len(structure.case_labels) >= 2
    
    def test_complexity_score(self):
        """Test complexity metric calculation"""
        simple_structure = ProofStructure(
            total_lines=5,
            lemma_count=0,
            case_count=0,
            tactic_count=1,
            nesting_depth=1,
            avg_lemma_lines=5.0
        )
        
        complex_structure = ProofStructure(
            total_lines=50,
            lemma_count=10,
            case_count=5,
            tactic_count=30,
            nesting_depth=8,
            avg_lemma_lines=2.0
        )
        
        simple_complexity = simple_structure.complexity_score()
        complex_complexity = complex_structure.complexity_score()
        
        # Simple proof should have lower complexity
        assert simple_complexity < complex_complexity
        assert 0 <= simple_complexity <= 1
        assert 0 <= complex_complexity <= 1


class TestV7PedagogicalAssessment:
    """Tests for pedagogical value assessment"""
    
    def test_assess_empty_proof(self):
        """Test assessment of empty proof"""
        v7 = VerifierV7()
        ped = v7.assess_pedagogical_value("", "set_theory")
        
        assert ped.pedagogical_score() == 0.0
        assert len(ped.teaching_value_indicators) == 0
    
    def test_assess_canonical_logic(self):
        """Test assessment of canonical logic proof (high pedagogical value)"""
        v7 = VerifierV7()
        proof_text = """
        -- Goal: Prove Modus Ponens
        theorem modus_ponens: P → (P → Q) → Q :=
          fun hp hpq => hpq hp
        
        -- Key insight: 
        -- From a proposition and its implication, we derive the conclusion
        """
        
        ped = v7.assess_pedagogical_value(proof_text, "logic")
        
        # Check that at least some pedagogical indicators are present
        assert ped.has_key_insight    # "key insight" mentioned
        assert len(ped.teaching_value_indicators) > 0
        score = ped.pedagogical_score()
        assert score > 0.2  # Should have some pedagogical value
    
    def test_assess_analytic_proof(self):
        """Test assessment of analysis proof (complex, low pedagogy expected)"""
        v7 = VerifierV7()
        proof_text = """
        theorem limit_epsilon_delta: ∀ ε > 0, ∃ δ > 0, 
          ∀ x, |x - a| < δ → |f x - L| < ε := by
          intro ε hε
          use δ
          constructor
          · exact sorry
          · intro x hx
            exact sorry
        """
        
        ped = v7.assess_pedagogical_value(proof_text, "analysis")
        
        # Analysis proofs are inherently complex, pedagogy may be limited
        assert isinstance(ped, PedagogicalAssessment)
    
    def test_teaching_value_indicators(self):
        """Test collection of teaching value indicators"""
        v7 = VerifierV7()
        proof_text = """
        -- Goal: Prove A ∪ A = A
        -- Key insight: An element is in A ∪ A iff it's in A
        lemma left_inclusion: A ∪ A ⊆ A := sorry
        lemma right_inclusion: A ⊆ A ∪ A := sorry
        theorem result: A ∪ A = A := by
          ext x
          constructor <;> intro h <;> [exact sorry, exact sorry]
        
        -- Example: {1, 2, 3} ∪ {1, 2, 3} = {1, 2, 3}
        """
        
        ped = v7.assess_pedagogical_value(proof_text, "set_theory")
        
        assert "explicit_goal" in ped.teaching_value_indicators
        assert "key_insight" in ped.teaching_value_indicators
        assert len(ped.teaching_value_indicators) >= 3


class TestV7EleganceScoring:
    """Tests for elegance score computation"""
    
    def test_elegant_simple_proof(self):
        """Test elegance scoring for simple, elegant proof"""
        v7 = VerifierV7()
        
        # Simple, direct proof
        simple_structure = ProofStructure(
            total_lines=3,
            lemma_count=0,
            case_count=0,
            tactic_count=1,
            nesting_depth=1,
            avg_lemma_lines=3.0,
            tactic_types=["simp"]
        )
        
        score = v7.compute_elegance_score(simple_structure, "set_theory")
        # Simple proof should score well (7+)
        assert score >= 7.0  # Should be elegant for set theory
    
    def test_inelegant_verbose_proof(self):
        """Test elegance scoring for verbose, fragmented proof"""
        v7 = VerifierV7()
        
        # Complex, fragmented proof
        complex_structure = ProofStructure(
            total_lines=100,
            lemma_count=15,
            case_count=8,
            tactic_count=50,
            nesting_depth=10,
            avg_lemma_lines=2.0,  # Very fragmented
            tactic_types=["intro", "cases", "apply", "rw", "simp"]
        )
        
        score = v7.compute_elegance_score(complex_structure, "analysis")
        assert score <= 6.0  # Should be less elegant for analysis
    
    def test_domain_specific_elegance(self):
        """Test domain-specific elegance adjustments"""
        v7 = VerifierV7()
        
        moderate_structure = ProofStructure(
            total_lines=20,
            lemma_count=2,
            case_count=0,
            tactic_count=5,
            nesting_depth=2,
            avg_lemma_lines=10.0,
            tactic_types=["intro", "apply"]
        )
        
        # Same structure, different domains
        set_theory_score = v7.compute_elegance_score(moderate_structure, "set_theory")
        analysis_score = v7.compute_elegance_score(moderate_structure, "analysis")
        
        # Set theory should reward simplicity more
        assert set_theory_score > analysis_score


class TestV7PedagogicalScoring:
    """Tests for pedagogical clarity score computation"""
    
    def test_high_pedagogical_score(self):
        """Test high pedagogical score with all indicators"""
        v7 = VerifierV7()
        
        ped = PedagogicalAssessment(
            has_explicit_goal=True,
            has_key_insight=True,
            uses_standard_techniques=True,
            connects_to_theory=True,
            provides_examples=True,
            has_clear_progression=True,
            teaching_value_indicators=[
                "explicit_goal", "key_insight", "standard_techniques",
                "theory_connection", "examples", "clear_progression"
            ]
        )
        
        score = v7.compute_pedagogical_score(ped)
        assert score >= 9.0  # Should be very high
    
    def test_low_pedagogical_score(self):
        """Test low pedagogical score with minimal indicators"""
        v7 = VerifierV7()
        
        ped = PedagogicalAssessment(
            has_explicit_goal=False,
            has_key_insight=False,
            uses_standard_techniques=False,
            connects_to_theory=False,
            provides_examples=False,
            has_clear_progression=False,
            teaching_value_indicators=[]
        )
        
        score = v7.compute_pedagogical_score(ped)
        assert score <= 3.0  # Should be very low


class TestV7D11Assessment:
    """Tests for complete D11 assessment"""
    
    def test_assess_set_union_proof(self):
        """Test D11 assessment of set union idempotent proof"""
        v7 = VerifierV7()
        
        proof = {
            "proof_id": "set_union_001",
            "text": """
            theorem union_idempotent (A : Set α) : A ∪ A = A := by
              ext x
              constructor
              · intro h
                cases h with
                | inl ha => exact ha
                | inr ha => exact ha
              · intro ha
                left
                exact ha
            """,
            "domain": "set_theory"
        }
        
        assessment = v7.assess(proof)
        
        assert assessment.proof_id == "set_union_001"
        assert assessment.domain == "set_theory"
        assert 0 <= assessment.elegance_score <= 10
        assert 0 <= assessment.pedagogical_clarity_score <= 10
        assert 0 <= assessment.overall_d11_score <= 10
        assert isinstance(assessment.assessment_level, EleganceLevel)
        assert len(assessment.reasoning) > 0
    
    def test_assess_modus_ponens(self):
        """Test D11 assessment of Modus Ponens (canonical logic proof)"""
        v7 = VerifierV7()
        
        proof = {
            "proof_id": "logic_modus_ponens",
            "text": """
            -- Goal: Demonstrate Modus Ponens
            -- Key insight: From P and (P → Q), derive Q
            theorem modus_ponens (P Q : Prop) : P → (P → Q) → Q :=
              fun hp hpq => hpq hp
            """,
            "domain": "logic"
        }
        
        assessment = v7.assess(proof)
        
        # Assessment should complete and have valid scores
        assert 0 <= assessment.overall_d11_score <= 10
        assert isinstance(assessment.assessment_level, EleganceLevel)
        # Logic proofs should be relatively short and elegant
        assert assessment.structure.nesting_depth <= 3
    
    def test_assess_epsilon_delta_limit(self):
        """Test D11 assessment of ε-δ limit proof (complex analysis)"""
        v7 = VerifierV7()
        
        proof = {
            "proof_id": "analysis_limit",
            "text": """
            theorem limit_definition (f : ℝ → ℝ) (a L : ℝ) :
              (∀ ε > 0, ∃ δ > 0, ∀ x, |x - a| < δ → |f x - L| < ε) :=
            sorry
            """,
            "domain": "analysis"
        }
        
        assessment = v7.assess(proof)
        
        # Analysis proofs are inherently complex
        # Lower D11 expected due to inherent technical density
        assert isinstance(assessment, D11Assessment)
        assert assessment.domain == "analysis"
    
    def test_assessment_timestamp(self):
        """Test that assessment includes timestamp"""
        v7 = VerifierV7()
        
        proof = {
            "proof_id": "test_ts",
            "text": "theorem test : 1 = 1 := rfl",
            "domain": "logic"
        }
        
        assessment = v7.assess(proof)
        assert assessment.timestamp is not None
        assert len(assessment.timestamp) > 0
    
    def test_assessed_proofs_tracking(self):
        """Test that verifier tracks assessed proofs"""
        v7 = VerifierV7()
        
        proof1 = {
            "proof_id": "p1",
            "text": "theorem test1 : True := trivial",
            "domain": "logic"
        }
        
        proof2 = {
            "proof_id": "p2",
            "text": "theorem test2 : ∀ x, x = x := fun x => rfl",
            "domain": "logic"
        }
        
        v7.assess(proof1)
        v7.assess(proof2)
        
        assert len(v7.assessed_proofs) == 2
        assert v7.assessed_proofs[0].proof_id == "p1"
        assert v7.assessed_proofs[1].proof_id == "p2"


class TestV7DomainSpecificAssessment:
    """Tests for domain-specific assessment variations"""
    
    def test_assess_algebra_proof(self):
        """Test D11 assessment for algebra (group properties)"""
        v7 = VerifierV7()
        
        proof = {
            "proof_id": "algebra_group",
            "text": """
            theorem group_identity_unique (G : Type) [Group G] :
              ∃! e : G, ∀ a : G, e * a = a :=
            sorry
            """,
            "domain": "algebra"
        }
        
        assessment = v7.assess(proof)
        assert assessment.domain == "algebra"
        assert isinstance(assessment, D11Assessment)
    
    def test_assess_number_theory_proof(self):
        """Test D11 assessment for number theory"""
        v7 = VerifierV7()
        
        proof = {
            "proof_id": "nt_prime",
            "text": """
            theorem infinitely_many_primes :
              ∀ n, ∃ p > n, Prime p :=
            sorry
            """,
            "domain": "number_theory"
        }
        
        assessment = v7.assess(proof)
        assert assessment.domain == "number_theory"
        assert 0 <= assessment.overall_d11_score <= 10


class TestV7VerifierIntegration:
    """Tests for integration with other components"""
    
    def test_d11_assessment_to_dict(self):
        """Test converting D11 assessment to dictionary"""
        v7 = VerifierV7()
        
        proof = {
            "proof_id": "test_dict",
            "text": "theorem simple : True := trivial",
            "domain": "logic"
        }
        
        assessment = v7.assess(proof)
        as_dict = assessment.to_dict()
        
        assert isinstance(as_dict, dict)
        assert "proof_id" in as_dict
        assert "elegance_score" in as_dict
        assert "pedagogical_clarity_score" in as_dict
        assert "overall_d11_score" in as_dict
        assert "assessment_level" in as_dict
    
    def test_multiple_assessments_independence(self):
        """Test that multiple assessments don't interfere"""
        v7 = VerifierV7()
        
        proofs = [
            {"proof_id": "simple", "text": "theorem t : True := trivial", "domain": "logic"},
            {"proof_id": "complex", "text": "theorem t : ∀ x y, x + y = y + x := sorry", "domain": "algebra"},
            {"proof_id": "union", "text": "theorem t (A : Set α) : A ∪ A = A := sorry", "domain": "set_theory"}
        ]
        
        assessments = [v7.assess(p) for p in proofs]
        
        assert len(assessments) == 3
        assert all(isinstance(a, D11Assessment) for a in assessments)
        assert assessments[0].proof_id == "simple"
        assert assessments[1].proof_id == "complex"
        assert assessments[2].proof_id == "union"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
