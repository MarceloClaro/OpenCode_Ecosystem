"""
TDD: reasoning-orchestrator-v11 — Multi-agent reasoning pipeline
Tests OrchestratorState, ReasoningOrchestrator, and taxonomy integrity.
"""
import os
import sys
import pytest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AGENTS_DIR = os.path.join(SKILL_DIR, "agents")
sys.path.insert(0, SKILL_DIR)
sys.path.insert(0, AGENTS_DIR)


class TestReasoningStructure:
    """CT-1: Directory and file structure."""

    def test_skill_md_exists(self):
        path = os.path.join(SKILL_DIR, "SKILL.md")
        assert os.path.isfile(path), "SKILL.md must exist"

    def test_agents_directory_exists(self):
        assert os.path.isdir(AGENTS_DIR), "agents/ directory must exist"

    def test_core_modules_present(self):
        files = os.listdir(SKILL_DIR)
        assert "orchestrator.py" in files, "orchestrator.py must exist"
        assert "reason.py" in files, "reason.py must exist"

    def test_agent_files_exist(self):
        agent_files = os.listdir(AGENTS_DIR)
        required = ["framework.py", "critical_agents.py", "domain_agents.py"]
        for f in required:
            assert f in agent_files, f"Missing agent file: {f}"


class TestOrchestratorState:
    """CT-2: OrchestratorState initialization and defaults."""

    def test_state_importable(self):
        from orchestrator import OrchestratorState
        state = OrchestratorState(
            problem={"id": "test", "description": "test problem"},
            domain="mathematics"
        )
        assert state.problem["id"] == "test"
        assert state.domain == "mathematics"
        assert state.phase == 0
        assert state.pci == 0
        assert state.verdict == "PENDING"
        assert isinstance(state.errors, list)
        assert isinstance(state.warnings, list)
        assert isinstance(state.agent_results, dict)
        assert isinstance(state.lemma_graph, dict)


class TestReasoningOrchestrator:
    """CT-3: Orchestrator pipeline structure."""

    def test_orchestrator_importable(self):
        from orchestrator import ReasoningOrchestrator
        orch = ReasoningOrchestrator()
        assert orch is not None
        assert len(orch.pipeline) == 7, "Must have 7 pipeline phases"
        for phase in range(1, 8):
            assert phase in orch.pipeline, f"Missing phase {phase}"

    def test_solve_returns_structure(self):
        from orchestrator import ReasoningOrchestrator
        orch = ReasoningOrchestrator()
        problem = {
            "id": "test-001",
            "description": "Test problem",
            "n": 3,
            "domain": "mathematics",
            "claimed_answer": {1},
            "statements": ["Statement A", "Statement B"],
        }
        result = orch.solve(problem, domain="mathematics")
        assert "pci" in result, "Result must have PCI"
        assert "verdict" in result, "Result must have verdict"
        assert "agent_results" in result, "Result must have agent results"
        assert isinstance(result["pci"], int), "PCI must be integer"
        assert 0 <= result["pci"] <= 100, "PCI must be 0-100"

    def test_pipeline_phases_execute(self):
        from orchestrator import ReasoningOrchestrator
        orch = ReasoningOrchestrator()
        problem = {
            "id": "test-002",
            "description": "Simple arithmetic",
            "n": 2,
            "domain": "mathematics",
            "claimed_answer": {2},
            "statements": ["1+1=2", "2*2=4"],
        }
        result = orch.solve(problem)
        agents_run = len(result.get("agent_results", {}))
        assert agents_run > 0, f"Must execute at least 1 agent (got {agents_run})"


class TestTaxonomyIntegrity:
    """CT-4: Reasoning type taxonomy validation."""

    def test_framework_registry_populated(self):
        from framework import REASONING_REGISTRY
        assert len(REASONING_REGISTRY) >= 50, \
            f"Must have 50+ reasoning types (got {len(REASONING_REGISTRY)})"

    def test_registry_has_categories(self):
        from framework import REASONING_REGISTRY
        categories = set(info["category"] for info in REASONING_REGISTRY.values())
        assert len(categories) >= 5, f"Must have 5+ categories (got {len(categories)})"

    def test_registry_has_domains(self):
        from framework import REASONING_REGISTRY
        domains = set(info["domain"] for info in REASONING_REGISTRY.values())
        assert len(domains) >= 3, f"Must have 3+ domains (got {len(domains)})"

    def test_get_agents_for_domain(self):
        from framework import get_agents_for_domain
        agents = get_agents_for_domain("mathematics")
        assert len(agents) > 0, "Must have mathematics agents"

    def test_skill_md_documents_phases(self):
        path = os.path.join(SKILL_DIR, "SKILL.md")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        assert "FASE 1" in content, "Must document Phase 1"
        assert "FASE 7" in content, "Must document Phase 7"
        assert "PCI" in content, "Must document Proof Confidence Index"
