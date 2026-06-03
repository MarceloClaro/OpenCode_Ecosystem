"""Handoff Templates — Context-preserving handoff document generation."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


PRIORITY_ORDER = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}


def generate_handoff(
    from_agent: str,
    to_agent: str,
    phase: int,
    task_ref: str,
    priority: str = "Medium",
    project: str = "",
    current_state: str = "",
    files: list[str] | None = None,
    acceptance_criteria: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "metadata": {
            "from": from_agent,
            "to": to_agent,
            "phase": phase,
            "task_reference": task_ref,
            "priority": priority,
            "timestamp": _ts(),
        },
        "context": {
            "project": project,
            "current_state": current_state,
            "relevant_files": files or [],
            "dependencies": [],
            "constraints": [],
        },
        "deliverable": {
            "what_is_needed": f"Handoff from {from_agent} to {to_agent}",
            "acceptance_criteria": acceptance_criteria or [],
            "reference_materials": [],
        },
        "quality": {
            "must_pass": [],
            "evidence_required": "Screenshots and test output",
            "handoff_to_next": "",
        },
    }


def generate_qa_verdict(
    task_id: str,
    developer: str,
    verdict: str,
    attempt: int = 1,
    acceptance_criteria: list[str] | None = None,
    issues: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    doc: dict[str, Any] = {
        "task": {"task_id": task_id, "developer": developer, "qa_agent": "Evidence Collector", "attempt": attempt, "timestamp": _ts()},
        "verdict": verdict.upper(),
    }
    if verdict.upper() == "PASS":
        doc["evidence"] = {"screenshots": {"desktop": "", "tablet": "", "mobile": ""}, "functional_verification": []}
        doc["acceptance_criteria"] = {c: "passed" for c in (acceptance_criteria or [])}
        doc["notes"] = "All criteria met."
        doc["next_action"] = "Agents Orchestrator: Mark task complete, advance to next task"
    else:
        doc["issues"] = issues or []
        doc["acceptance_criteria_status"] = {}
        for c in (acceptance_criteria or []):
            failed = any(i.get("criterion", "") == c for i in (issues or []))
            doc["acceptance_criteria_status"][c] = "FAILED" if failed else "passed"
        doc["retry_instructions"] = [
            "Fix ONLY the issues listed above",
            "Do NOT introduce new features or changes",
            "Re-submit for QA when all issues are addressed",
            f"This is attempt {attempt} of 3 maximum",
        ]
    return doc


def generate_escalation(
    task_id: str,
    developer: str,
    attempts_history: list[dict[str, Any]],
    root_cause: str = "",
    systemic_issue: str = "",
) -> dict[str, Any]:
    return {
        "task": {"task_id": task_id, "developer": developer, "attempts_exhausted": 3, "escalation_to": "Agents Orchestrator", "timestamp": _ts()},
        "failure_history": [{"attempt": h.get("attempt", i + 1), "issues": h.get("issues", ["Unresolved"]), "result": "FAIL"} for i, h in enumerate(attempts_history)],
        "root_cause_analysis": {"why_failing": root_cause or "Task complexity exceeded scope", "systemic_issue": systemic_issue or "Requires architectural review"},
        "resolution_options": [
            {"option": "Reassign", "recommended_agent": "Senior Developer"},
            {"option": "Decompose", "proposed_breakdown": "Split into subtasks"},
            {"option": "Revise approach", "change_needed": "Architecture/design change"},
            {"option": "Accept", "limitations": "Current state with documented limitations"},
            {"option": "Defer", "target": "Future sprint"},
        ],
        "impact_assessment": {"blocking": [f"Tasks dependent on {task_id}"], "timeline_impact": "1-3 day delay", "quality_impact": "Known limitations accepted"},
    }


def generate_phase_gate_handoff(
    from_phase: int,
    to_phase: int,
    gate_keeper: str,
    gate_result: str,
    criteria_results: dict[str, bool],
) -> dict[str, Any]:
    entries = []
    for name, passed in criteria_results.items():
        entries.append({"criterion": name, "result": "PASS" if passed else "FAIL"})
    return {
        "transition": {"from_phase": from_phase, "to_phase": to_phase, "gate_keeper": gate_keeper, "gate_result": gate_result, "timestamp": _ts()},
        "gate_criteria_results": entries,
        "documents_carried_forward": [],
        "risks_carried_forward": [],
    }
