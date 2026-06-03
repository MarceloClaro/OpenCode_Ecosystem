"""Tests for Sprint Prioritizer engine."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import pytest
from sprint_prioritizer_engine import calculate_rice, classify_moscow, plan_sprint_capacity, resolve_dependencies, value_vs_effort


class TestRICE:
    def test_basic_calculation(self):
        score = calculate_rice(2000, 3, 0.9, 5)
        assert score == 1080.0

    def test_negative_reach_raises(self):
        with pytest.raises(ValueError):
            calculate_rice(-10, 1, 0.5, 5)

    def test_zero_effort_raises(self):
        with pytest.raises(ValueError):
            calculate_rice(100, 2, 0.5, 0)


class TestMoSCoW:
    def test_classification(self):
        items = [
            {"id": "A", "rice_score": 500},
            {"id": "B", "rice_score": 150},
            {"id": "C", "rice_score": 30},
            {"id": "D", "rice_score": 8},
            {"id": "E", "rice_score": 300},
            {"id": "F", "rice_score": 80},
        ]
        result = classify_moscow(items)
        classifications = {r["id"]: r["moscow"] for r in result}
        assert classifications["A"] == "Must Have"
        assert classifications["B"] in ("Must Have", "Should Have")
        assert classifications["D"] == "Won't Have"

    def test_empty_list(self):
        assert classify_moscow([]) == []


class TestSprintCapacity:
    def test_with_buffer(self):
        result = plan_sprint_capacity(30, 5, 15)
        assert result["effective_capacity"] == 25.5
        assert result["recommended_commitment"] == 25.5

    def test_max_commitment(self):
        result = plan_sprint_capacity(30, 5, 15)
        assert result["max_commitment"] == 33.0


class TestDependencyResolution:
    def test_topological_sort(self):
        tasks = [
            {"id": "A", "deps": []},
            {"id": "B", "deps": ["A"]},
            {"id": "C", "deps": ["A"]},
            {"id": "D", "deps": ["B", "C"]},
        ]
        result = resolve_dependencies(tasks)
        ids = [t["id"] for t in result]
        assert ids.index("A") < ids.index("B")
        assert ids.index("A") < ids.index("C")
        assert ids.index("B") < ids.index("D")
        assert ids.index("C") < ids.index("D")

    def test_circular_dependency_raises(self):
        tasks = [
            {"id": "X", "deps": ["Y"]},
            {"id": "Y", "deps": ["X"]},
        ]
        with pytest.raises(ValueError, match="Circular"):
            resolve_dependencies(tasks)


class TestValueVsEffort:
    def test_quadrant_classification(self):
        items = [
            {"id": "qw", "value": 0.9, "effort": 3},
            {"id": "mp", "value": 0.8, "effort": 15},
            {"id": "fi", "value": 0.3, "effort": 2},
            {"id": "ts", "value": 0.2, "effort": 12},
        ]
        result = value_vs_effort(items)
        assert len(result["quick_wins"]) == 1
        assert result["quick_wins"][0]["id"] == "qw"
        assert len(result["major_projects"]) == 1
        assert len(result["fill_ins"]) == 1
        assert len(result["time_sinks"]) == 1
