"""Tests for Trend Researcher engine."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from trend_researcher_engine import classify_lifecycle, calculate_market_size, calculate_signal_strength, build_positioning_matrix, adoption_forecast


class TestLifecycleClassification:
    def test_emergence(self):
        assert classify_lifecycle(0.5, 100, 3) == "EMERGENCE"

    def test_growth(self):
        assert classify_lifecycle(0.2, 2000, 10) == "GROWTH"

    def test_maturity(self):
        assert classify_lifecycle(0.05, 5000, 24) == "MATURITY"

    def test_decline(self):
        assert classify_lifecycle(-0.1, 10000, 60) == "DECLINE"


class TestMarketSizing:
    def test_basic_calculation(self):
        result = calculate_market_size(1000000, 0.15, 0.4, 0.1)
        assert result["TAM"] == 150000
        assert result["SAM"] == 60000
        assert result["SOM"] == 6000
        assert result["TAM"] >= result["SAM"] >= result["SOM"]


class TestSignalStrength:
    def test_weighted_scoring(self):
        signals = {"social_media": 80, "patent": 60, "investment": 90, "academic": 40, "expert": 50}
        score = calculate_signal_strength(signals)
        assert 0 <= score <= 100
        expected = 80*0.30 + 60*0.20 + 90*0.25 + 40*0.15 + 50*0.10
        assert score == round(expected, 2)

    def test_unknown_source_ignored(self):
        signals = {"social_media": 100, "unknown_source": 100}
        score = calculate_signal_strength(signals)
        assert score == 30.0  # only social_media weight 0.30 * 100


class TestPositioningMatrix:
    def test_matrix_build(self):
        competitors = [
            {"name": "Alpha", "features": {"speed": 9, "ux": 7, "price": 5}},
            {"name": "Beta", "features": {"speed": 6, "ux": 8, "price": 8}},
        ]
        features = ["speed", "ux", "price", "ai_assistant"]
        result = build_positioning_matrix(competitors, features)
        assert len(result["competitors"]) == 2
        assert result["competitors"][0]["name"] == "Alpha"
        assert result["competitors"][0]["differentiation_score"] == 75.0  # 3/4
        assert "ai_assistant" in result["white_space"]

    def test_white_space_detection(self):
        competitors = [{"name": "X", "features": {"a": 1}}]
        result = build_positioning_matrix(competitors, ["a", "b", "c"])
        assert set(result["white_space"]) == {"b", "c"}


class TestAdoptionForecast:
    def test_growth_projection(self):
        forecasts = adoption_forecast(1000, 0.1, 10000, 3)
        assert len(forecasts) == 3
        assert forecasts[0]["projected_users"] >= 1100
        assert forecasts[2]["penetration_pct"] > forecasts[0]["penetration_pct"]

    def test_caps_at_total_market(self):
        forecasts = adoption_forecast(9000, 0.5, 10000, 12)
        assert all(f["projected_users"] <= 10000 for f in forecasts)
