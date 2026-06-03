"""Behavioral Nudge Engine — Adaptive software interaction cadence generator."""
from __future__ import annotations
from typing import Any

NUDGE_SEQUENCE: dict[int, str] = {
    1: "SMS",
    2: "SMS",
    3: "EMAIL",
    4: "EMAIL",
    5: "EMAIL",
    6: "in_app",
    7: "in_app",
    10: "EMAIL",
    14: "in_app",
    30: "EMAIL",
}


def generate_sprint_nudge(pending_tasks: list[dict[str, Any]], user_profile: dict[str, Any]) -> dict[str, Any]:
    tendencies = user_profile.get("tendencies", [])
    status = user_profile.get("status", "Normal")
    preferred_channel = user_profile.get("preferred_channel", "EMAIL")
    is_overwhelmed = "ADHD" in tendencies or status == "Overwhelmed" or len(pending_tasks) > 15

    if is_overwhelmed:
        return {
            "channel": preferred_channel if preferred_channel in ("SMS", "in_app") else "SMS",
            "message": "Hey! You've got a few quick follow-ups pending. Let's see how many we can knock out in the next 5 mins. I'll tee up the first draft. Ready?",
            "action_button": "Start 5 Min Sprint",
            "type": "micro_sprint",
        }

    top_task = pending_tasks[0] if pending_tasks else {"title": "No pending tasks", "priority": "None"}
    return {
        "channel": "EMAIL",
        "message": f"You have {len(pending_tasks)} pending items. Here is the highest priority: {top_task.get('title', 'N/A')}.",
        "action_button": "View Tasks",
        "type": "standard_summary",
    }


def get_nudge_channel(day: int, preferred_channel: str = "EMAIL", use_fallback: bool = False) -> str:
    if not use_fallback:
        return preferred_channel
    return NUDGE_SEQUENCE.get(day, preferred_channel)


def generate_celebration(completed_tasks: int, total_minutes: int, user_name: str = "") -> str:
    greeting = f"{user_name}, " if user_name else ""
    if completed_tasks >= 20:
        return f"Amazing work{greeting}! You crushed {completed_tasks} tasks in {total_minutes} minutes. That's incredible momentum. Want to do another 5 minutes, or call it for now?"
    elif completed_tasks >= 10:
        return f"Nice work{greeting}! You completed {completed_tasks} tasks in {total_minutes} minutes. That's solid progress. Want to keep going for 5 more minutes, or take a break?"
    elif completed_tasks >= 5:
        return f"Great job{greeting}! {completed_tasks} tasks done in {total_minutes} minutes. Want to do another 5 minutes, or call it for the day?"
    return f"Good start{greeting}! {completed_tasks} tasks completed. Ready for another quick sprint?"


def assess_cognitive_load(pending_count: int) -> dict[str, Any]:
    if pending_count == 0:
        return {"level": "none", "strategy": "celebration", "action": "You're all caught up!"}
    if pending_count <= 3:
        return {"level": "low", "strategy": "single_task", "action": "Show the most critical item"}
    if pending_count <= 10:
        return {"level": "moderate", "strategy": "priority_triage", "action": "Show top 3, hide rest"}
    if pending_count <= 25:
        return {"level": "high", "strategy": "micro_sprint", "action": "Time-box to 5 minutes"}
    return {"level": "critical", "strategy": "single_action", "action": "Show ONE action only. No counts."}
