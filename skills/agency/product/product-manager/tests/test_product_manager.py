"""Tests for Product Manager engine."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from product_manager_engine import assess_opportunity, validate_roadmap_item, calculate_sprint_health, evaluate_scope_change


class TestOpportunityAssessment:
    def test_high_score_recommends_build(self):
        result = assess_opportunity(5000, 2.0, 0.75, 6.0)
        assert result["rice_score"] == 1250.0
        assert result["recommendation"] == "BUILD"

    def test_very_low_score_recommends_kill(self):
        result = assess_opportunity(100, 0.5, 0.3, 10)
        assert result["recommendation"] == "KILL"

    def test_medium_score_recommends_explore(self):
        result = assess_opportunity(500, 1.5, 0.6, 8)
        assert result["recommendation"] == "EXPLORE"

    def test_low_score_recommends_defer(self):
        result = assess_opportunity(200, 1.0, 0.5, 10)
        assert result["recommendation"] == "DEFER"


class TestRoadmapValidation:
    def test_valid_item(self):
        item = {"name": "Onboarding v2", "owner": "Alex", "success_metric": "activation +15%", "time_horizon": "Now"}
        valid, msg = validate_roadmap_item(item)
        assert valid is True
        assert msg == ""

    def test_missing_owner(self):
        item = {"name": "Feature X", "owner": "", "success_metric": "N/A", "time_horizon": "Next"}
        valid, msg = validate_roadmap_item(item)
        assert valid is False
        assert "owner" in msg

    def test_invalid_horizon(self):
        item = {"name": "A", "owner": "B", "success_metric": "C", "time_horizon": "Soon"}
        valid, msg = validate_roadmap_item(item)
        assert valid is False
        assert "time_horizon" in msg


class TestSprintHealth:
    def test_partial_completion(self):
        result = calculate_sprint_health([5, 8, 3], [5, 3, 0], ["Login", "Dashboard", "API"])
        assert result["velocity"] == 16
        assert result["completed"] == 8
        assert result["completion_pct"] == 50.0
        assert len(result["carried_over"]) == 2

    def test_full_completion(self):
        result = calculate_sprint_health([5, 5, 5], [5, 5, 5])
        assert result["completion_pct"] == 100.0
        assert result["status"] == "ON_TRACK"
        assert len(result["blockers"]) == 0


class TestScopeChange:
    def test_accept_critical(self):
        result = evaluate_scope_change({"source": "Sales", "priority": "Critical", "effort_estimate": 8}, "Improve onboarding")
        assert result["decision"] == "ACCEPT"

    def test_reject_low_priority(self):
        result = evaluate_scope_change({"source": "Eng", "priority": "Low", "aligns_with_goal": False}, "Improve onboarding")
        assert result["decision"] == "REJECT"

    def test_defer_non_aligned(self):
        result = evaluate_scope_change({"source": "Marketing", "priority": "Medium", "aligns_with_goal": False, "effort_estimate": 5}, "Improve onboarding")
        assert result["decision"] == "DEFER"
