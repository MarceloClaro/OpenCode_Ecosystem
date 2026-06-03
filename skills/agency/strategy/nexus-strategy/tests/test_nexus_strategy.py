"""Tests for NEXUS Strategy Orchestrator engine."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from nexus_strategy_engine import PipelineState, advance_phase, get_phase_agents, evaluate_gate, record_qa_result, get_pipeline_summary


class TestPhaseTransition:
    def test_advance_with_gate_passed(self):
        state = PipelineState(mode="NEXUS-Full")
        state.set_gate(0, True)
        result = advance_phase(state)
        assert result["status"] == "ADVANCED"
        assert result["from_phase"] == 0
        assert result["to_phase"] == 1

    def test_advance_with_gate_failed(self):
        state = PipelineState()
        state.set_gate(0, False)
        result = advance_phase(state)
        assert result["status"] == "BLOCKED"
        assert result["to_phase"] == 0


class TestAgentActivation:
    def test_full_mode_phase1_agents(self):
        state = PipelineState(mode="NEXUS-Full")
        state.current_phase = 1
        agents = get_phase_agents(state)
        assert "Studio Producer" in agents
        assert "Senior Project Manager" in agents
        assert "Sprint Prioritizer" in agents

    def test_micro_mode_phase3_max_agents(self):
        state = PipelineState(mode="NEXUS-Micro")
        state.current_phase = 3
        agents = get_phase_agents(state)
        assert len(agents) <= 10


class TestQualityGate:
    def test_all_pass(self):
        results = {"market_validated": True}
        verdict = evaluate_gate(0, results)
        assert verdict["verdict"] == "PASS"

    def test_one_fail(self):
        results = {"market_validated": False}
        verdict = evaluate_gate(0, results)
        assert verdict["verdict"] == "FAIL"
        assert len(verdict["failed_details"]) >= 1


class TestDevQARetry:
    def test_retry_tracking(self):
        state = PipelineState()
        r1 = record_qa_result(state, "T-001", "FAIL", [{"criterion": "visual", "issue": "misaligned"}])
        assert r1["attempts"] == 1
        assert r1["status"] == "RETRY"

    def test_escalation_after_3_fails(self):
        state = PipelineState()
        for _ in range(3):
            record_qa_result(state, "T-002", "FAIL")
        task = state.tasks["T-002"]
        assert task["attempts"] == 3
        assert task["status"] == "ESCALATED"

    def test_pass_clears_task(self):
        state = PipelineState()
        record_qa_result(state, "T-003", "PASS")
        assert state.tasks["T-003"]["status"] == "COMPLETED"


class TestPipelineSummary:
    def test_summary_basics(self):
        state = PipelineState(mode="NEXUS-Full")
        state.current_phase = 3
        summary = get_pipeline_summary(state)
        assert summary["mode"] == "NEXUS-Full"
        assert summary["current_phase"] == 3
        assert summary["phase_name"] == "Build"
        assert len(summary["active_agents"]) > 0
