"""Tests for Handoff Templates engine."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from handoff_templates_engine import generate_handoff, generate_qa_verdict, generate_escalation, generate_phase_gate_handoff


class TestStandardHandoff:
    def test_basic_handoff(self):
        doc = generate_handoff(
            from_agent="Backend Architect",
            to_agent="Frontend Developer",
            phase=2,
            task_ref="T-042",
            priority="High",
            acceptance_criteria=["API returns valid JSON", "Response time < 200ms"],
        )
        assert doc["metadata"]["from"] == "Backend Architect"
        assert doc["metadata"]["to"] == "Frontend Developer"
        assert doc["metadata"]["phase"] == 2
        assert doc["metadata"]["task_reference"] == "T-042"
        assert doc["metadata"]["priority"] == "High"
        assert len(doc["deliverable"]["acceptance_criteria"]) == 2


class TestQAVerdictPass:
    def test_pass_verdict(self):
        doc = generate_qa_verdict(
            task_id="T-001",
            developer="Frontend Developer",
            verdict="PASS",
            attempt=2,
            acceptance_criteria=["UI renders", "Form submits"],
        )
        assert doc["verdict"] == "PASS"
        assert doc["acceptance_criteria"]["UI renders"] == "passed"
        assert doc["acceptance_criteria"]["Form submits"] == "passed"
        assert "next_action" in doc


class TestQAVerdictFail:
    def test_fail_verdict_with_issues(self):
        issues = [
            {"criterion": "UI renders", "category": "Visual", "severity": "High", "expected": "Blue button", "actual": "Red button", "fix": "Change color to #0055FF"},
        ]
        doc = generate_qa_verdict(
            task_id="T-002",
            developer="Backend Architect",
            verdict="FAIL",
            attempt=1,
            acceptance_criteria=["UI renders", "Form submits"],
            issues=issues,
        )
        assert doc["verdict"] == "FAIL"
        assert len(doc["issues"]) == 1
        assert doc["issues"][0]["category"] == "Visual"
        assert "Do NOT introduce new features" in doc["retry_instructions"][1]

    def test_fail_partial_acceptance(self):
        issues = [{"criterion": "UI renders", "category": "Visual", "severity": "High", "expected": "X", "actual": "Y", "fix": "Z"}]
        doc = generate_qa_verdict("T-003", "Dev", "FAIL", acceptance_criteria=["UI renders", "Form submits"], issues=issues)
        assert doc["acceptance_criteria_status"]["UI renders"] == "FAILED"
        assert doc["acceptance_criteria_status"]["Form submits"] == "passed"


class TestEscalation:
    def test_escalation_report(self):
        history = [
            {"attempt": 1, "issues": ["Color mismatch"]},
            {"attempt": 2, "issues": ["Spacing wrong"]},
            {"attempt": 3, "issues": ["Still broken"]},
        ]
        doc = generate_escalation("T-099", "Frontend Developer", history, "Design tokens not applied", "Missing design system integration")
        assert doc["task"]["attempts_exhausted"] == 3
        assert len(doc["failure_history"]) == 3
        assert doc["root_cause_analysis"]["why_failing"] != ""
        assert len(doc["resolution_options"]) >= 3
        assert len(doc["impact_assessment"]["blocking"]) >= 1


class TestPhaseGateHandoff:
    def test_gate_transition(self):
        doc = generate_phase_gate_handoff(2, 3, "DevOps Automator", "PASSED", {"ci_cd_operational": True, "skeleton_running": True})
        assert doc["transition"]["from_phase"] == 2
        assert doc["transition"]["to_phase"] == 3
        assert doc["transition"]["gate_result"] == "PASSED"
        assert len(doc["gate_criteria_results"]) == 2
