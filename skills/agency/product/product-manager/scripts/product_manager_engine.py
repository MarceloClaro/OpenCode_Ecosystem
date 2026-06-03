"""Product Manager — Product lifecycle decision engine."""
from __future__ import annotations
from typing import Any


def assess_opportunity(
    reach: float, impact: float, confidence: float, effort: float
) -> dict[str, Any]:
    if effort <= 0:
        raise ValueError("Effort must be greater than zero")
    rice = (reach * impact * confidence) / effort
    rice = round(rice, 2)
    if rice >= 100:
        recommendation = "BUILD"
    elif rice >= 30:
        recommendation = "EXPLORE"
    elif rice >= 10:
        recommendation = "DEFER"
    else:
        recommendation = "KILL"
    return {"rice_score": rice, "recommendation": recommendation, "factors": {"reach": reach, "impact": impact, "confidence": confidence, "effort": effort}}


def validate_roadmap_item(item: dict[str, Any]) -> tuple[bool, str]:
    required = ["name", "owner", "success_metric", "time_horizon"]
    missing = [f for f in required if not item.get(f)]
    if missing:
        return False, f"Missing required fields: {', '.join(missing)}"
    if item.get("time_horizon", "") not in ("Now", "Next", "Later"):
        return False, "time_horizon must be one of: Now, Next, Later"
    return True, ""


def calculate_sprint_health(
    committed: list[float], delivered: list[float], task_labels: list[str] | None = None
) -> dict[str, Any]:
    labels = task_labels or [f"Task-{i}" for i in range(len(committed))]
    velocity = sum(committed)
    completed = sum(delivered)
    completion_pct = round((completed / velocity * 100), 1) if velocity > 0 else 0.0
    carried_over = []
    blockers = []
    for i, (c, d) in enumerate(zip(committed, delivered)):
        if d < c:
            carried_over.append({"label": labels[i], "points_remaining": c - d})
            blockers.append({"task": labels[i], "reason": "Not completed", "points_blocked": c - d})
    return {
        "velocity": velocity,
        "completed": completed,
        "completion_pct": completion_pct,
        "carried_over": carried_over,
        "blockers": blockers,
        "status": "ON_TRACK" if completion_pct >= 70 else ("AT_RISK" if completion_pct >= 40 else "OFF_TRACK"),
    }


def evaluate_scope_change(
    request: dict[str, Any], sprint_goal: str
) -> dict[str, Any]:
    source = request.get("source", "Unknown")
    priority = request.get("priority", "Medium")
    aligns = request.get("aligns_with_goal", False)
    effort = request.get("effort_estimate", 5)
    if priority == "Critical" or aligns:
        decision = "ACCEPT"
        rationale = f"Aligned with sprint goal '{sprint_goal}'" if aligns else "Critical priority"
    elif priority == "High" and effort <= 3:
        decision = "ACCEPT"
        rationale = f"High priority, low effort ({effort} pts)"
    elif priority == "Low":
        decision = "REJECT"
        rationale = "Low priority — defer to backlog"
    else:
        decision = "DEFER"
        rationale = f"Does not align with sprint goal '{sprint_goal}'. Evaluate next sprint."
    return {
        "decision": decision,
        "rationale": rationale,
        "request_source": source,
        "request_priority": priority,
        "impact_assessment": {"timeline_impact": f"+{effort} pts" if decision == "ACCEPT" else "None", "scope_delta": effort if decision == "ACCEPT" else 0},
    }
