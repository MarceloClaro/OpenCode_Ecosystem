"""Tests for graph-memory-updater skill."""
import sys
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import pytest


class TestGraphMemoryUpdater:
    """CT-1: Updater lifecycle."""

    @pytest.fixture
    def storage(self):
        from memory_updater import MockGraphStorage
        return MockGraphStorage()

    @pytest.fixture
    def updater(self, storage):
        from memory_updater import GraphMemoryUpdater
        return GraphMemoryUpdater("test_graph", storage)

    def test_updater_start_stop(self, updater):
        updater.start()
        assert updater._running
        updater.stop()
        assert not updater._running

    def test_agent_activity_creation(self):
        from memory_updater import AgentActivity
        activity = AgentActivity(
            platform="twitter", agent_id=1, agent_name="Test",
            action_type="CREATE_POST",
            action_args={"content": "Hello world"},
            round_num=1, timestamp="2025-01-01T00:00:00",
        )
        text = activity.to_episode_text()
        assert "Test" in text
        assert "Hello world" in text

    def test_do_nothing_is_skipped(self, updater):
        from memory_updater import AgentActivity
        activity = AgentActivity(
            platform="twitter", agent_id=0, agent_name="Silent",
            action_type="DO_NOTHING", action_args={},
            round_num=1, timestamp="2025-01-01T00:00:00",
        )
        updater.add_activity(activity)
        stats = updater.get_stats()
        assert stats["skipped"] == 1
        assert stats["total"] == 0

    def test_stats_report(self, updater):
        stats = updater.get_stats()
        assert stats["graph_id"] == "test_graph"
        assert "total" in stats
        assert "sent" in stats


import os
