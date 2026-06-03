"""Tests for simulation-runner skill."""
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import pytest


class TestSimEngine:
    """CT-1: Core engine data structures."""

    def test_agent_state_enum(self):
        from sim_engine import AgentState
        assert AgentState.IDLE.value == "idle"
        assert AgentState.THINKING.value == "thinking"

    def test_action_type_enum(self):
        from sim_engine import ActionType
        assert ActionType.POST.value == "post"
        assert ActionType.DO_NOTHING.value == "nothing"

    def test_sentiment_enum(self):
        from sim_engine import Sentiment
        assert Sentiment.NEUTRAL.value == 0
        assert Sentiment.VERY_POSITIVE.value == 2

    def test_agent_memory_creation(self):
        from sim_engine import AgentMemory
        mem = AgentMemory()
        assert mem.emotional_state == 0.0
        assert mem.energy == 1.0
        assert mem.recent_posts == []


class TestBrazilTimezone:
    """CT-2: BRAZIL_TZ is correct."""

    def test_brazil_tz_offset(self):
        from sim_engine import BRAZIL_TZ
        from datetime import timedelta
        assert BRAZIL_TZ.utcoffset(None) == timedelta(hours=-3)


class TestModuleIntegrity:
    """CT-3: All module files exist."""

    def test_core_files_exist(self):
        core_files = [
            "sim_engine.py", "profile_manager.py",
            "llm_discourse.py", "multiagent_warroom.py",
        ]
        for f in core_files:
            assert (SKILL_DIR / "scripts" / f).exists(), f"Missing: {f}"

    def test_scripts_dir_has_modules(self):
        assert (SKILL_DIR / "scripts").is_dir()
        scripts = list((SKILL_DIR / "scripts").glob("*.py"))
        assert len(scripts) >= 3
        for s in scripts:
            assert s.stat().st_size > 0, f"Empty script: {s.name}"
