"""Tests for Behavioral Nudge Engine."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from behavioral_nudge_engine import generate_sprint_nudge, get_nudge_channel, generate_celebration, assess_cognitive_load


class TestSprintNudgeADHD:
    def test_adhd_profile_hides_count(self):
        tasks = [{"title": f"Task {i}", "priority": "High"} for i in range(50)]
        user = {"tendencies": ["ADHD"], "status": "Normal", "preferred_channel": "SMS"}
        nudge = generate_sprint_nudge(tasks, user)
        assert nudge["channel"] == "SMS"
        assert "5 mins" in nudge["message"]
        assert "50" not in nudge["message"]
        assert nudge["type"] == "micro_sprint"

    def test_overwhelmed_status_triggers_micro_sprint(self):
        tasks = [{"title": "T1", "priority": "High"} for _ in range(20)]
        user = {"tendencies": [], "status": "Overwhelmed", "preferred_channel": "EMAIL"}
        nudge = generate_sprint_nudge(tasks, user)
        assert nudge["type"] == "micro_sprint"


class TestSprintNudgeStandard:
    def test_standard_profile_shows_count(self):
        tasks = [{"title": "Fix login bug", "priority": "High"}, {"title": "Update docs", "priority": "Low"}]
        user = {"tendencies": [], "status": "Normal", "preferred_channel": "EMAIL"}
        nudge = generate_sprint_nudge(tasks, user)
        assert nudge["channel"] == "EMAIL"
        assert "2" in nudge["message"]
        assert "Fix login bug" in nudge["message"]
        assert nudge["type"] == "standard_summary"


class TestNudgeChannel:
    def test_day1_no_fallback(self):
        assert get_nudge_channel(1, "SMS") == "SMS"

    def test_day5_fallback_email(self):
        assert get_nudge_channel(5, "in_app", use_fallback=True) == "EMAIL"


class TestCelebration:
    def test_high_completion(self):
        msg = generate_celebration(20, 45, "Alex")
        assert "Alex" in msg
        assert "20" in msg
        assert "Want to do another 5 minutes" in msg or "5 more minutes" in msg

    def test_medium_completion(self):
        msg = generate_celebration(12, 25)
        assert "12" in msg
        assert "keep going" in msg.lower() or "5 more" in msg.lower() or "another 5" in msg.lower()

    def test_low_completion_offers_off_ramp(self):
        msg = generate_celebration(3, 8)
        assert "3" in msg


class TestCognitiveLoad:
    def test_none(self):
        assert assess_cognitive_load(0)["level"] == "none"

    def test_critical(self):
        result = assess_cognitive_load(50)
        assert result["level"] == "critical"
        assert "ONE" in result["action"]
