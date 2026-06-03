"""
Unit tests for ArchitectAgent
Tests domain inference, phase selection, and proof skeleton generation

Test Coverage:
- Domain classification (set_theory, algebra, logic, analysis, number_theory)
- Phase selection based on domain
- Reasoning type selection
- Proof skeleton template generation
- Error handling for unknown domains
"""

import pytest
import sys
from pathlib import Path
from dataclasses import asdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "references"))

from architect_agent import (
    ArchitectAgent, 
    Problem, 
    ReasoningPlan,
    DOMAIN_STRATEGIES,
    PHASE_DEFINITIONS,
    PROOF_TEMPLATES
)


class TestArchitectAgentInitialization:
    """Test ArchitectAgent initialization"""
    
    def test_init_default(self):
        """Test default initialization"""
        architect = ArchitectAgent()
        assert architect.reasoning_orchestrator is None
        assert architect.decision_node is None
        assert architect.generated_proofs == []
    
    def test_init_with_mocks(self):
        """Test initialization with mocked dependencies"""
        mock_orchestrator = {"name": "mock_orchestrator"}
        mock_decision_node = {"name": "mock_decision_node"}
        
        architect = ArchitectAgent(
            reasoning_orchestrator=mock_orchestrator,
            decision_node=mock_decision_node
        )
        
        assert architect.reasoning_orchestrator == mock_orchestrator
        assert architect.decision_node == mock_decision_node


class TestDomainClassification:
    """Test domain classification and strategy selection"""
    
    def test_known_domains(self):
        """Test classification of all known domains"""
        architect = ArchitectAgent()
        
        test_domains = {
            "set_theory": "set_theory",
            "algebra": "algebra",
            "logic": "logic",
            "analysis": "analysis",
            "number_theory": "number_theory"
        }
        
        for input_domain, expected_domain in test_domains.items():
            problem = Problem(
                id="test_001",
                domain=input_domain,
                statement="Test theorem",
                difficulty="intermediate"
            )
            
            plan, metadata = architect.analyze(problem)
            
            assert metadata["domain"] == expected_domain
            assert plan.domain_strategy == expected_domain
    
    def test_domain_case_insensitivity(self):
        """Test that domain classification is case-insensitive"""
        architect = ArchitectAgent()
        
        test_cases = ["ALGEBRA", "Algebra", "AlGebrA"]
        
        for domain_input in test_cases:
            problem = Problem(
                id="test_002",
                domain=domain_input,
                statement="Test theorem",
                difficulty="intermediate"
            )
            
            plan, metadata = architect.analyze(problem)
            assert metadata["domain"] == "algebra"
    
    def test_unknown_domain_default(self):
        """Test that unknown domains default to algebra"""
        architect = ArchitectAgent()
        
        problem = Problem(
            id="test_003",
            domain="unknown_domain_xyz",
            statement="Test theorem",
            difficulty="intermediate"
        )
        
        plan, metadata = architect.analyze(problem)
        
        # Should default to algebra
        assert metadata["domain"] == "algebra"
        assert plan.domain_strategy == "algebra"


class TestPhaseSelection:
    """Test phase selection based on domain"""
    
    @pytest.mark.parametrize("domain,expected_phases", [
        ("set_theory", [1, 2, 3, 5, 6, 7]),
        ("algebra", [1, 2, 3, 4, 6, 7]),
        ("logic", [1, 3, 5, 6, 7]),
        ("analysis", [1, 2, 3, 4, 5, 6, 7]),
        ("number_theory", [1, 2, 3, 5, 6, 7])
    ])
    def test_phase_selection_by_domain(self, domain, expected_phases):
        """Test that correct phases are selected for each domain"""
        architect = ArchitectAgent()
        
        problem = Problem(
            id=f"phase_test_{domain}",
            domain=domain,
            statement="Test theorem",
            difficulty="intermediate"
        )
        
        plan, metadata = architect.analyze(problem)
        
        assert plan.phases_selected == expected_phases
        assert metadata["phases_count"] == len(expected_phases)
    
    def test_phase_definitions_valid(self):
        """Test that all phase definitions are valid"""
        for phase_num in range(1, 8):
            assert phase_num in PHASE_DEFINITIONS
            
            phase_def = PHASE_DEFINITIONS[phase_num]
            assert "name" in phase_def
            assert "reasoning_types" in phase_def
            assert "purpose" in phase_def
            assert "output" in phase_def
            assert len(phase_def["reasoning_types"]) > 0


class TestReasoningTypeSelection:
    """Test reasoning type selection"""
    
    def test_reasoning_types_selected(self):
        """Test that reasoning types are selected for each phase"""
        architect = ArchitectAgent()
        
        problem = Problem(
            id="reasoning_test_001",
            domain="algebra",
            statement="Test theorem",
            difficulty="intermediate"
        )
        
        plan, metadata = architect.analyze(problem)
        
        # Should have reasoning types (at least 1 per phase)
        assert len(plan.reasoning_types) > 0
        assert len(plan.reasoning_types) >= len(plan.phases_selected)
    
    def test_reasoning_types_from_phase_definitions(self):
        """Test that reasoning types come from phase definitions"""
        architect = ArchitectAgent()
        
        problem = Problem(
            id="reasoning_test_002",
            domain="logic",
            statement="Test theorem",
            difficulty="intermediate"
        )
        
        plan, metadata = architect.analyze(problem)
        
        # Verify reasoning types come from selected phases
        expected_reasoning_types = []
        for phase_num in plan.phases_selected:
            expected_reasoning_types.extend(
                PHASE_DEFINITIONS[phase_num]["reasoning_types"][:3]
            )
        
        assert plan.reasoning_types == expected_reasoning_types


class TestProofSkeleton:
    """Test proof skeleton generation"""
    
    def test_skeleton_generation_basic(self):
        """Test basic proof skeleton generation"""
        architect = ArchitectAgent()
        
        problem = Problem(
            id="A0004",
            domain="algebra",
            statement="For all a, a + 0 = a",
            difficulty="easy"
        )
        
        plan, _ = architect.analyze(problem)
        skeleton = architect.generate_skeleton(problem, plan)
        
        assert skeleton is not None
        assert "lean_code" in skeleton
        assert "theorem_" in skeleton["lean_code"]
        assert "sorry" in skeleton["lean_code"]
    
    def test_skeleton_contains_phase_comments(self):
        """Test that skeleton contains phase comments"""
        architect = ArchitectAgent()
        
        problem = Problem(
            id="A0005",
            domain="algebra",
            statement="Test",
            difficulty="intermediate"
        )
        
        plan, _ = architect.analyze(problem)
        skeleton = architect.generate_skeleton(problem, plan)
        
        lean_code = skeleton["lean_code"]
        
        # Should contain phase comments
        assert "Phase" in lean_code
        assert "sorry" in lean_code
    
    def test_skeleton_different_domains(self):
        """Test skeleton generation for different domains"""
        architect = ArchitectAgent()
        
        test_problems = [
            Problem("D1", "set_theory", "Set test", "easy"),
            Problem("D2", "algebra", "Algebra test", "easy"),
            Problem("D3", "logic", "Logic test", "easy"),
        ]
        
        for problem in test_problems:
            plan, _ = architect.analyze(problem)
            skeleton = architect.generate_skeleton(problem, plan)
            
            assert "lean_code" in skeleton
            assert "theorem_" in skeleton["lean_code"]
    
    def test_skeleton_theorem_naming(self):
        """Test correct theorem naming in skeleton"""
        architect = ArchitectAgent()
        
        problem = Problem(
            id="test:problem:001",
            domain="algebra",
            statement="Test",
            difficulty="easy"
        )
        
        plan, _ = architect.analyze(problem)
        skeleton = architect.generate_skeleton(problem, plan)
        
        # Theorem name should have colons replaced with underscores
        assert "theorem_test_problem_001" in skeleton["lean_code"]


class TestReasoningPlan:
    """Test ReasoningPlan data structure"""
    
    def test_reasoning_plan_creation(self):
        """Test ReasoningPlan creation and properties"""
        plan = ReasoningPlan(
            phases_selected=[1, 2, 3],
            reasoning_types=["R01_Notation", "R02_Abstraction", "R03_Decomposition"],
            domain_strategy="algebra",
            estimated_sorry_count=1
        )
        
        assert plan.phases_selected == [1, 2, 3]
        assert len(plan.reasoning_types) == 3
        assert plan.domain_strategy == "algebra"
        assert plan.estimated_sorry_count == 1
    
    def test_reasoning_plan_to_dict(self):
        """Test ReasoningPlan serialization"""
        plan = ReasoningPlan(
            phases_selected=[1, 2, 3],
            reasoning_types=["R01_Notation", "R02_Abstraction"],
            domain_strategy="algebra",
            estimated_sorry_count=2
        )
        
        plan_dict = asdict(plan)
        
        assert isinstance(plan_dict, dict)
        assert plan_dict["phases_selected"] == [1, 2, 3]
        assert plan_dict["domain_strategy"] == "algebra"


class TestProblemDataClass:
    """Test Problem data structure"""
    
    def test_problem_creation_basic(self):
        """Test basic Problem creation"""
        problem = Problem(
            id="test_001",
            domain="algebra",
            statement="a + b = b + a",
            difficulty="easy"
        )
        
        assert problem.id == "test_001"
        assert problem.domain == "algebra"
        assert problem.statement == "a + b = b + a"
        assert problem.difficulty == "easy"
    
    def test_problem_with_variables(self):
        """Test Problem with variables"""
        problem = Problem(
            id="test_002",
            domain="algebra",
            statement="a + 0 = a",
            difficulty="easy",
            variables=["a"]
        )
        
        assert problem.variables == ["a"]
    
    def test_problem_to_dict(self):
        """Test Problem serialization"""
        problem = Problem(
            id="test_003",
            domain="algebra",
            statement="Test",
            difficulty="intermediate"
        )
        
        problem_dict = asdict(problem)
        
        assert problem_dict["id"] == "test_003"
        assert problem_dict["domain"] == "algebra"


class TestDecisionNodeIntegration:
    """Test DecisionNode integration (when decision_node is provided)"""
    
    def test_decision_recording_structure(self):
        """Test that decisions would be recorded correctly"""
        # Mock decision node
        recorded_decisions = []
        
        class MockDecisionNode:
            def record_decision(self, id, decision, rationale):
                recorded_decisions.append({
                    "id": id,
                    "decision": decision,
                    "rationale": rationale
                })
        
        mock_dn = MockDecisionNode()
        architect = ArchitectAgent(decision_node=mock_dn)
        
        problem = Problem(
            id="test_004",
            domain="algebra",
            statement="Test",
            difficulty="intermediate"
        )
        
        architect.analyze(problem)
        
        # Should have recorded a decision
        assert len(recorded_decisions) == 1
        assert "proof-strategy-test_004" in recorded_decisions[0]["id"]


class TestErrorHandling:
    """Test error handling"""
    
    def test_analyze_with_none_domain(self):
        """Test handling of None domain"""
        architect = ArchitectAgent()
        
        # This might raise an error or handle gracefully
        # Depending on implementation
        try:
            problem = Problem(
                id="test_error_001",
                domain=None,
                statement="Test",
                difficulty="easy"
            )
            plan, metadata = architect.analyze(problem)
            # If it doesn't raise, should default to algebra
            assert metadata["domain"] == "algebra"
        except (TypeError, AttributeError):
            # Acceptable to raise error
            pass
    
    def test_analyze_with_empty_statement(self):
        """Test handling of empty statement"""
        architect = ArchitectAgent()
        
        problem = Problem(
            id="test_error_002",
            domain="algebra",
            statement="",
            difficulty="easy"
        )
        
        # Should still work
        plan, metadata = architect.analyze(problem)
        assert metadata["domain"] == "algebra"


class TestIntegration:
    """Integration tests for full analyze + generate_skeleton flow"""
    
    def test_full_workflow_algebra(self):
        """Test complete workflow for algebra problem"""
        architect = ArchitectAgent()
        
        problem = Problem(
            id="B0014",
            domain="algebra",
            statement="For a group (G, ·), prove a·e = a",
            difficulty="intermediate"
        )
        
        # Step 1: Analyze
        plan, metadata = architect.analyze(problem)
        
        assert metadata["domain"] == "algebra"
        assert len(plan.phases_selected) > 0
        
        # Step 2: Generate skeleton
        skeleton = architect.generate_skeleton(problem, plan)
        
        assert "lean_code" in skeleton
        assert skeleton["lean_code"] is not None
    
    def test_full_workflow_logic(self):
        """Test complete workflow for logic problem"""
        architect = ArchitectAgent()
        
        problem = Problem(
            id="E0019",
            domain="logic",
            statement="Prove ¬(P ∧ ¬P)",
            difficulty="intermediate"
        )
        
        plan, metadata = architect.analyze(problem)
        assert metadata["domain"] == "logic"
        
        skeleton = architect.generate_skeleton(problem, plan)
        assert "lean_code" in skeleton
    
    def test_full_workflow_batch(self):
        """Test batch processing multiple problems"""
        architect = ArchitectAgent()
        
        problems = [
            Problem("batch_001", "algebra", "Test 1", "easy"),
            Problem("batch_002", "logic", "Test 2", "intermediate"),
            Problem("batch_003", "set_theory", "Test 3", "hard"),
        ]
        
        results = []
        for problem in problems:
            plan, metadata = architect.analyze(problem)
            skeleton = architect.generate_skeleton(problem, plan)
            results.append((plan, skeleton))
        
        assert len(results) == 3
        assert all(r[1] is not None for r in results)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_long_problem_statement(self):
        """Test handling of very long problem statement"""
        architect = ArchitectAgent()
        
        long_statement = "Test " * 1000  # Very long statement
        
        problem = Problem(
            id="edge_001",
            domain="algebra",
            statement=long_statement,
            difficulty="easy"
        )
        
        plan, metadata = architect.analyze(problem)
        assert metadata["domain"] == "algebra"
    
    def test_special_characters_in_problem_id(self):
        """Test handling of special characters in problem ID"""
        architect = ArchitectAgent()
        
        special_ids = ["test:1:2:3", "test-1-2-3", "test_1_2_3"]
        
        for problem_id in special_ids:
            problem = Problem(
                id=problem_id,
                domain="algebra",
                statement="Test",
                difficulty="easy"
            )
            
            plan, _ = architect.analyze(problem)
            skeleton = architect.generate_skeleton(problem, plan)
            
            assert "lean_code" in skeleton
    
    def test_all_difficulties(self):
        """Test all difficulty levels"""
        architect = ArchitectAgent()
        
        difficulties = ["easy", "intermediate", "hard", "research"]
        
        for difficulty in difficulties:
            problem = Problem(
                id=f"difficulty_{difficulty}",
                domain="algebra",
                statement="Test",
                difficulty=difficulty
            )
            
            plan, metadata = architect.analyze(problem)
            assert metadata["difficulty"] == difficulty


# ═════════════════════════════════════════════════════════════════
# Test Execution & Coverage Report
# ═════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    """
    Run tests with:
        pytest test_architect.py -v --cov=architect_agent --cov-report=html
    
    Expected coverage:
        - ArchitectAgent class: 100%
        - Problem dataclass: 100%
        - ReasoningPlan dataclass: 100%
        - Domain classification: 100%
        - Phase selection: 100%
        - Skeleton generation: 95%+
    """
    pytest.main([__file__, "-v", "--tb=short"])
