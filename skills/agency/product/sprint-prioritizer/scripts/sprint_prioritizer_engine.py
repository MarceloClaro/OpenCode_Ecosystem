"""Sprint Prioritizer — Agile sprint planning and prioritization engine."""
from __future__ import annotations
from typing import Any


def calculate_rice(reach: float, impact: float, confidence: float, effort: float) -> float:
    if reach < 0:
        raise ValueError("Reach must be non-negative")
    if effort <= 0:
        raise ValueError("Effort must be greater than zero")
    if impact < 0.25 or impact > 3:
        raise ValueError("Impact must be between 0.25 and 3")
    if not (0 <= confidence <= 1):
        raise ValueError("Confidence must be between 0 and 1")
    return round((reach * impact * confidence) / effort, 2)


def classify_moscow(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not items:
        return []
    sorted_items = sorted(items, key=lambda x: x.get("rice_score", 0), reverse=True)
    n = len(sorted_items)
    boundaries = {
        "Must Have": max(1, round(n * 0.2)),
        "Should Have": max(1, round(n * 0.3)),
        "Could Have": max(1, round(n * 0.3)),
    }
    idx = 0
    for item in sorted_items:
        if idx < boundaries["Must Have"]:
            item["moscow"] = "Must Have"
        elif idx < boundaries["Must Have"] + boundaries["Should Have"]:
            item["moscow"] = "Should Have"
        elif idx < boundaries["Must Have"] + boundaries["Should Have"] + boundaries["Could Have"]:
            item["moscow"] = "Could Have"
        else:
            item["moscow"] = "Won't Have"
        idx += 1
    return sorted_items


def plan_sprint_capacity(velocity: float, team_size: int, buffer_pct: float = 15.0) -> dict[str, Any]:
    if velocity <= 0:
        raise ValueError("Velocity must be positive")
    if buffer_pct < 0 or buffer_pct > 50:
        raise ValueError("Buffer percentage must be between 0 and 50")
    effective_capacity = round(velocity * (1 - buffer_pct / 100), 1)
    return {
        "velocity": velocity,
        "team_size": team_size,
        "buffer_pct": buffer_pct,
        "effective_capacity": effective_capacity,
        "recommended_commitment": effective_capacity,
        "max_commitment": velocity * 1.1,
    }


def resolve_dependencies(tasks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    task_map: dict[str, dict[str, Any]] = {}
    for t in tasks:
        tid = t["id"]
        task_map[tid] = dict(t)
        if "deps" not in task_map[tid]:
            task_map[tid]["deps"] = []

    in_degree: dict[str, int] = {tid: len(task_map[tid].get("deps", [])) for tid in task_map}
    queue = [tid for tid, deg in in_degree.items() if deg == 0]
    result: list[dict[str, Any]] = []
    visited: set[str] = set()

    while queue:
        queue.sort()
        current = queue.pop(0)
        if current in visited:
            continue
        visited.add(current)
        result.append(task_map[current])
        for tid, task in task_map.items():
            if current in task.get("deps", []):
                in_degree[tid] -= 1
                if in_degree[tid] == 0 and tid not in visited:
                    queue.append(tid)

    if len(result) != len(tasks):
        cycle_tasks = [tid for tid in task_map if tid not in visited]
        raise ValueError(f"Circular dependency detected involving: {cycle_tasks}")

    return result


def value_vs_effort(items: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    quadrants: dict[str, list[dict[str, Any]]] = {"quick_wins": [], "major_projects": [], "fill_ins": [], "time_sinks": []}
    for item in items:
        value = item.get("value", 0.5)
        effort = item.get("effort", 5)
        high_value = value >= 0.6
        low_effort = effort <= 5
        if high_value and low_effort:
            quadrants["quick_wins"].append(item)
        elif high_value and not low_effort:
            quadrants["major_projects"].append(item)
        elif not high_value and low_effort:
            quadrants["fill_ins"].append(item)
        else:
            quadrants["time_sinks"].append(item)
    return quadrants
