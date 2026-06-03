"""Agent Activation Prompts — Template resolution and placeholder interpolation."""
from __future__ import annotations
import re
from typing import Any

AGENTS_BY_DIVISION: dict[str, list[str]] = {
    "Engineering": ["Frontend Developer", "Backend Architect", "AI Engineer", "DevOps Automator", "Rapid Prototyper", "Senior Developer", "Mobile App Builder"],
    "Design": ["UI Designer", "UX Researcher", "UX Architect", "Brand Guardian", "Visual Storyteller", "Whimsy Injector", "Image Prompt Engineer"],
    "Marketing": ["Growth Hacker", "Content Creator", "Twitter Engager", "TikTok Strategist", "Instagram Curator", "Reddit Community Builder", "App Store Optimizer", "Social Media Strategist"],
    "Product": ["Sprint Prioritizer", "Trend Researcher", "Feedback Synthesizer"],
    "Project Management": ["Studio Producer", "Project Shepherd", "Studio Operations", "Experiment Tracker", "Senior Project Manager"],
    "Testing": ["Evidence Collector", "Reality Checker", "Test Results Analyzer", "Performance Benchmarker", "API Tester", "Tool Evaluator", "Workflow Optimizer"],
    "Support": ["Support Responder", "Analytics Reporter", "Finance Tracker", "Infrastructure Maintainer", "Legal Compliance Checker", "Executive Summary Generator"],
    "Spatial Computing": ["XR Interface Architect", "macOS Spatial/Metal Engineer", "XR Immersive Developer", "XR Cockpit Interaction Specialist", "visionOS Spatial Engineer", "Terminal Integration Specialist"],
    "Specialized": ["Agents Orchestrator", "LSP/Index Engineer", "Sales Data Extraction Agent", "Data Consolidation Agent", "Report Distribution Agent"],
}

PROMPT_DB: dict[str, str] = {
    "Frontend Developer": "You are Frontend Developer working within the NEXUS pipeline for [PROJECT NAME]. Phase: [PHASE]. Task: [TASK ID] — [TASK DESCRIPTION]. Acceptance criteria: [SPECIFIC CRITERIA FROM TASK LIST].",
    "Backend Architect": "You are Backend Architect working within the NEXUS pipeline for [PROJECT NAME]. Phase: [PHASE]. Task: [TASK ID] — [TASK DESCRIPTION]. Acceptance criteria: [SPECIFIC CRITERIA FROM TASK LIST].",
    "Sprint Prioritizer": "You are Sprint Prioritizer planning the next sprint for [PROJECT NAME]. Input: current backlog, team velocity, strategic priorities.",
    "Evidence Collector": "You are Evidence Collector performing QA within the NEXUS Dev-QA loop. Task: [TASK ID] — [TASK DESCRIPTION]. Developer: [WHICH AGENT IMPLEMENTED THIS]. Attempt: [N] of 3 maximum.",
}

ORCHESTRATOR_PROMPTS: dict[str, str] = {
    "NEXUS-Full": "You are the Agents Orchestrator executing the NEXUS 7-phase pipeline for [PROJECT NAME]. Mode: NEXUS-Full.",
    "NEXUS-Sprint": "You are the Agents Orchestrator executing the NEXUS sprint pipeline for [PROJECT NAME]. Mode: NEXUS-Sprint. Recommended 15-25 agents.",
    "NEXUS-Micro": "You are the Agents Orchestrator executing the NEXUS micro pipeline for [PROJECT NAME]. Mode: NEXUS-Micro. Use 5-10 agents max.",
}

GENERIC_PROMPT = "You are [AGENT NAME] working within the NEXUS pipeline. Phase: [PHASE]. Complete the assigned task following NEXUS quality standards."


def resolve_prompt(role: str, phase: str = "Build") -> str:
    if role in PROMPT_DB:
        return PROMPT_DB[role]
    return GENERIC_PROMPT.replace("[AGENT NAME]", role).replace("[PHASE]", phase)


def get_orchestrator_prompt(mode: str) -> str:
    for key in ORCHESTRATOR_PROMPTS:
        if mode in key or key in mode:
            return ORCHESTRATOR_PROMPTS[key]
    return ORCHESTRATOR_PROMPTS.get(mode, ORCHESTRATOR_PROMPTS["NEXUS-Sprint"])


def interpolate(template: str, values: dict[str, str]) -> str:
    result = template
    for key, val in values.items():
        result = result.replace(f"[{key}]", str(val))
        result = result.replace(f"[{key.upper()}]", str(val))
    return result


def list_supported_agents() -> dict[str, list[str]]:
    return dict(AGENTS_BY_DIVISION)


def get_agent_division(agent_name: str) -> str | None:
    for division, agents in AGENTS_BY_DIVISION.items():
        if agent_name in agents:
            return division
    return None
