"""Tests for Feedback Synthesizer engine."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
import pytest
from feedback_synthesizer_engine import analyze_sentiment, categorize_feedback, calculate_rice_score, generate_summary, filter_by_theme


class TestSentimentAnalysis:
    def test_positive_sentiment(self):
        result = analyze_sentiment("This feature is amazing, love it!")
        assert result["score"] > 0.5
        assert result["label"] == "positive"
        assert result["confidence"] >= 0.7

    def test_negative_sentiment(self):
        result = analyze_sentiment("This is terrible, worst update ever")
        assert result["score"] < -0.5
        assert result["label"] == "negative"
        assert result["confidence"] >= 0.7

    def test_neutral_sentiment(self):
        result = analyze_sentiment("The update was released yesterday")
        assert result["label"] == "neutral"


class TestCategorization:
    def test_performance_theme(self):
        items = [{"id": "1", "text": "The app is so slow and laggy"}]
        result = categorize_feedback(items)
        assert "performance" in result["theme_distribution"]

    def test_ux_theme(self):
        items = [{"id": "2", "text": "The navigation is confusing and hard to find settings"}]
        result = categorize_feedback(items)
        assert "ux" in result["theme_distribution"]

    def test_fallback_to_general(self):
        items = [{"id": "3", "text": "xyz abc 123"}]
        result = categorize_feedback(items)
        assert "general" in result["theme_distribution"]


class TestRICEScore:
    def test_basic_calculation(self):
        score = calculate_rice_score(1000, 2, 0.8, 4)
        assert score == 400.0

    def test_zero_effort_raises(self):
        with pytest.raises(ValueError):
            calculate_rice_score(100, 1, 0.5, 0)

    def test_invalid_impact_raises(self):
        with pytest.raises(ValueError):
            calculate_rice_score(100, 5, 0.5, 2)


class TestSummary:
    def test_mixed_feedback(self):
        items = [
            {"id": "1", "text": "Love this feature!"},
            {"id": "2", "text": "Terrible performance."},
            {"id": "3", "text": "The app is okay."},
        ]
        summary = generate_summary(items)
        assert summary["total_count"] == 3
        assert sum(summary["sentiment_distribution"].values()) == 3
        assert len(summary["top_themes"]) <= 5

    def test_all_positive(self):
        items = [{"id": "1", "text": "amazing great love excellent fantastic wonderful perfect"}]
        summary = generate_summary(items)
        assert summary["sentiment_distribution"]["positive"] == 1
        assert summary["summary_verdict"] == "positive"


class TestThemeFilter:
    def test_filter_by_performance(self):
        items = [
            {"id": "1", "text": "The app is slow"},
            {"id": "2", "text": "Love the design"},
            {"id": "3", "text": "Loading times are terrible"},
        ]
        filtered = filter_by_theme(items, "performance")
        assert len(filtered) == 2

    def test_filter_unknown_theme(self):
        assert filter_by_theme([], "nonexistent") == []
