"""NEXUS Strategy Orchestrator — Multi-agent pipeline lifecycle engine."""
from __future__ import annotations
import copy
from typing import Any

PHASES = {
    0: "Discovery",
    1: "Strategy",
    2: "Foundation",
    3: "Build",
    4: "Hardening",
    5: "Launch",
    6: "Operate",
}

FULL_AGENTS = {
    0: ["Trend Researcher", "Feedback Synthesizer", "UX Researcher", "Analytics Reporter", "Legal Compliance Checker", "Tool Evaluator"],
    1: ["Studio Producer", "Senior Project Manager", "Sprint Prioritizer", "UX Architect", "Brand Guardian", "Backend Architect", "AI Engineer", "Finance Tracker"],
    2: ["DevOps Automator", "Frontend Developer", "Backend Architect", "UX Architect", "Infrastructure Maintainer", "Studio Operations"],
    3: ["Frontend Developer", "Backend Architect", "AI Engineer", "Mobile App Builder", "Evidence Collector", "API Tester", "Performance Benchmarker"],
    4: ["Reality Checker", "Evidence Collector", "Performance Benchmarker", "API Tester", "Test Results Analyzer", "Legal Compliance Checker", "Infrastructure Maintainer"],
    5: ["Growth Hacker", "Content Creator", "Social Media Strategist", "DevOps Automator", "Infrastructure Maintainer", "Support Responder", "Analytics Reporter"],
    6: ["Infrastructure Maintainer", "Support Responder", "Analytics Reporter", "Feedback Synthesizer", "Finance Tracker", "Trend Researcher", "Sprint Prioritizer"],
}

SPRINT_AGENTS = {
    0: ["Trend Researcher", "Feedback Synthesizer", "UX Researcher"],
    1: ["Senior Project Manager", "Sprint Prioritizer", "UX Architect", "Backend Architect"],
    2: ["DevOps Automator", "Frontend Developer", "Backend Architect"],
    3: ["Frontend Developer", "Backend Architect", "Evidence Collector", "API Tester"],
    4: ["Reality Checker", "Evidence Collector", "Performance Benchmarker"],
    5: ["Content Creator", "Social Media Strategist", "DevOps Automator"],
    6: ["Infrastructure Maintainer", "Support Responder", "Analytics Reporter"],
}

MICRO_AGENTS = {
    0: ["Trend Researcher", "Analytics Reporter"],
    1: ["Senior Project Manager", "Sprint Prioritizer"],
    2: ["Frontend Developer", "Backend Architect"],
    3: ["Frontend Developer", "Evidence Collector"],
    4: ["Reality Checker", "Evidence Collector"],
    5: ["Content Creator", "Social Media Strategist"],
    6: ["Infrastructure Maintainer", "Support Responder"],
}

AGENT_SETS = {"NEXUS-Full": FULL_AGENTS, "NEXUS-Sprint": SPRINT_AGENTS, "NEXUS-Micro": MICRO_AGENTS}

GATE_CRITERIA: dict[int, list[dict[str, Any]]] = {
    0: [{"name": "market_validated", "threshold": True, "evidence": "Trend Researcher report with sources"}],
    1: [{"name": "architecture_complete", "threshold": True, "evidence": "Backend Architect + UX Architect specs"}],
    2: [{"name": "ci_cd_operational", "threshold": True, "evidence": "Pipeline execution logs"}],
    3: [{"name": "all_tasks_pass_qa", "threshold": True, "evidence": "Evidence Collector screenshots per task"}],
    4: [{"name": "user_journeys_complete", "threshold": True, "evidence": "End-to-end screenshots"}],
    5: [{"name": "deployment_successful", "threshold": True, "evidence": "DevOps deployment logs"}],
    6: [{"name": "systems_stable", "threshold": True, "evidence": "Infrastructure monitoring"}],
}

class PipelineState:
    def __init__(self, mode: str = "NEXUS-Sprint"):
        self.mode = mode
        self.current_phase = 0
        self.gate_results: dict[int, bool] = {}
        self.tasks: dict[str, dict[str, Any]] = {}

    def set_gate(self, phase: int, passed: bool) -> None:
        self.gate_results[phase] = passed

    def add_task(self, task_id: str) -> None:
        self.tasks[task_id] = {"attempts": 0, "status": "PENDING", "history": []}


def advance_phase(state: PipelineState) -> dict[str, Any]:
    gate_passed = state.gate_results.get(state.current_phase, False)
    if gate_passed:
        old = state.current_phase
        state.current_phase = min(old + 1, 6)
        return {"from_phase": old, "to_phase": state.current_phase, "status": "ADVANCED"}
    return {"from_phase": state.current_phase, "to_phase": state.current_phase, "status": "BLOCKED", "reason": f"Phase {state.current_phase} gate not passed"}


def get_phase_agents(state: PipelineState) -> list[str]:
    agents = AGENT_SETS.get(state.mode, SPRINT_AGENTS)
    return list(agents.get(state.current_phase, []))


def evaluate_gate(phase: int, results: dict[str, bool]) -> dict[str, Any]:
    criteria = GATE_CRITERIA.get(phase, [])
    all_pass = all(results.get(c["name"], False) for c in criteria)
    failing = [c for c in criteria if not results.get(c["name"], False)]
    return {
        "phase": phase,
        "verdict": "PASS" if all_pass else "FAIL",
        "criteria_checked": len(criteria),
        "passed": sum(1 for c in criteria if results.get(c["name"], False)),
        "failed_details": failing,
        "evidence": [c["evidence"] for c in criteria] if all_pass else [],
    }


def record_qa_result(state: PipelineState, task_id: str, verdict: str, issues: list[dict] | None = None) -> dict[str, Any]:
    if task_id not in state.tasks:
        state.add_task(task_id)
    task = state.tasks[task_id]
    task["attempts"] += 1
    task["history"].append({"attempt": task["attempts"], "verdict": verdict, "issues": issues or []})
    if verdict == "PASS":
        task["status"] = "COMPLETED"
    elif task["attempts"] >= 3:
        task["status"] = "ESCALATED"
    else:
        task["status"] = "RETRY"
    return dict(task)


def get_pipeline_summary(state: PipelineState) -> dict[str, Any]:
    agents = get_phase_agents(state)
    return {
        "mode": state.mode,
        "current_phase": state.current_phase,
        "phase_name": PHASES.get(state.current_phase, "Unknown"),
        "active_agents": agents,
        "agent_count": len(agents),
        "tasks_total": len(state.tasks),
        "tasks_completed": sum(1 for t in state.tasks.values() if t["status"] == "COMPLETED"),
        "tasks_escalated": sum(1 for t in state.tasks.values() if t["status"] == "ESCALATED"),
    }
