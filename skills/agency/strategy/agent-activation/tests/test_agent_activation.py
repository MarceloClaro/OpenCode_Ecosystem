"""Tests for Agent Activation Prompts engine."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from agent_activation_engine import resolve_prompt, get_orchestrator_prompt, interpolate, list_supported_agents, get_agent_division


class TestPromptResolution:
    def test_known_agent(self):
        prompt = resolve_prompt("Frontend Developer", "Build")
        assert "Frontend Developer" in prompt
        assert "[PROJECT NAME]" in prompt

    def test_unknown_agent_fallback(self):
        prompt = resolve_prompt("UnknownBot", "Discovery")
        assert "UnknownBot" in prompt
        assert "NEXUS pipeline" in prompt


class TestOrchestratorPrompt:
    def test_full_mode(self):
        prompt = get_orchestrator_prompt("NEXUS-Full")
        assert "7-phase" in prompt or "NEXUS-Full" in prompt

    def test_micro_mode(self):
        prompt = get_orchestrator_prompt("NEXUS-Micro")
        assert "Micro" in prompt


class TestInterpolation:
    def test_all_placeholders_replaced(self):
        template = "Project: [PROJECT NAME], Phase: [PHASE], Task: [TASK ID]"
        result = interpolate(template, {"PROJECT NAME": "Atlas", "PHASE": "Build", "TASK ID": "T-042"})
        assert "Atlas" in result
        assert "Build" in result
        assert "T-042" in result
        assert "[PROJECT NAME]" not in result

    def test_partial_values_leave_unused(self):
        template = "Project: [PROJECT NAME], Phase: [PHASE]"
        result = interpolate(template, {"PROJECT NAME": "Atlas"})
        assert "Atlas" in result
        assert "[PHASE]" in result


class TestAgentEnumeration:
    def test_returns_divisions(self):
        agents = list_supported_agents()
        assert "Engineering" in agents
        assert "Product" in agents
        assert "Frontend Developer" in agents["Engineering"]
        assert "Backend Architect" in agents["Engineering"]
        assert "Sprint Prioritizer" in agents["Product"]
        assert "Trend Researcher" in agents["Product"]

    def test_get_division(self):
        assert get_agent_division("Frontend Developer") == "Engineering"
        assert get_agent_division("Sprint Prioritizer") == "Product"
        assert get_agent_division("NonexistentAgent") is None
