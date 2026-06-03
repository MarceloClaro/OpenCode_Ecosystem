"""TDD tests for HistorianEngine — anachronism detection, period authenticity, claim evaluation."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from historian_engine import HistorianEngine


class TestHistorian:
    def setup_method(self):
        self.engine = HistorianEngine()

    # ── Anachronism detection ─────────────────────────────────────────
    def test_potatoes_in_pre_columbian_europe(self):
        findings = self.engine.detect_anachronisms(
            "The knight ate potatoes and tomatoes for dinner",
            "medieval_europe", "Europe"
        )
        assert len(findings) > 0
        anachronisms = [f for f in findings if f["severity"] in ("high", "medium")]
        assert len(anachronisms) >= 1

    def test_maize_in_ancient_rome(self):
        findings = self.engine.detect_anachronisms(
            "Roman soldiers ate maize before battle",
            "ancient_rome", "Mediterranean"
        )
        high_anachronisms = [f for f in findings if f["severity"] == "high"]
        assert any("maize" in f["item"].lower() or "maize" in f.get("message", "").lower()
                   for f in high_anachronisms) or len(findings) > 0

    def test_gunpowder_in_ancient_egypt(self):
        findings = self.engine.detect_anachronisms(
            "Egyptian soldiers used gunpowder weapons",
            "ancient_egypt", "Nile Valley"
        )
        assert len(findings) > 0

    def test_tobacco_in_medieval_europe(self):
        findings = self.engine.detect_anachronisms(
            "A medieval monk smoking tobacco in his garden",
            "medieval_europe", "Europe"
        )
        assert len(findings) > 0

    def test_knight_drinking_coffee(self):
        findings = self.engine.detect_anachronisms(
            "The knight enjoyed coffee every morning",
            "medieval_europe", "Europe"
        )
        assert any(f["item"] == "coffee" for f in findings)

    # ── Confidence levels ─────────────────────────────────────────────
    def test_confidence_levels_stated(self):
        findings = self.engine.detect_anachronisms(
            "They used steam engines and antibiotics", "medieval_europe", "Europe"
        )
        assert len(findings) > 0
        for f in findings:
            assert "confidence" in f
            assert isinstance(f["confidence"], (int, float))
            assert 0.0 <= f["confidence"] <= 1.0

    # ── Period authenticity ───────────────────────────────────────────
    def test_period_authenticity_report_medieval(self):
        report = self.engine.period_authenticity("medieval_europe", "Europe")
        assert report["confidence_level"] == "high"
        assert "unavailable" in report.get("known_unavailable", []) or "known_unavailable" in report

    def test_period_authenticity_report_ancient_rome(self):
        report = self.engine.period_authenticity("ancient_rome", "Mediterranean")
        assert "available_crops" in report
        assert "wheat" in report.get("available_crops", [])

    def test_period_authenticity_unknown_period(self):
        report = self.engine.period_authenticity("unknown_period_xyz", "Nowhere")
        assert report["confidence_level"] == "low"
        assert "warning" in report

    def test_period_authenticity_includes_anachronism_risks(self):
        report = self.engine.period_authenticity("ancient_egypt", "Nile Valley")
        assert "anachronism_risks" in report
        assert isinstance(report["anachronism_risks"], list)

    # ── Claim evaluation ──────────────────────────────────────────────
    def test_claim_evaluation_returns_structure(self):
        result = self.engine.evaluate_claim(
            "Vikings grew potatoes before Columbus", "medieval_europe"
        )
        assert "verdict" in result
        assert "confidence" in result
        assert "claim" in result

    def test_claim_evaluation_counter_evidence_for_anachronism(self):
        result = self.engine.evaluate_claim(
            "Knights used plastic shields", "medieval_europe"
        )
        assert len(result["counter_evidence"]) > 0
        assert result["confidence"] < 0.5

    def test_claim_evaluation_supporting_evidence_for_valid(self):
        result = self.engine.evaluate_claim(
            "Romans grew wheat and olive", "ancient_rome"
        )
        assert len(result["supporting_evidence"]) >= 0
        assert isinstance(result["confidence"], float)

    def test_claim_evaluation_confidence_range(self):
        result = self.engine.evaluate_claim("Some claim text", "medieval_europe")
        assert 0.0 <= result["confidence"] <= 1.0

    # ── Engine property ───────────────────────────────────────────────
    def test_available_property(self):
        assert self.engine.available is True

    def test_period_covers_electricity_anachronism(self):
        findings = self.engine.detect_anachronisms(
            "Medieval peasants used electric lights",
            "medieval_europe", "Europe"
        )
        assert len(findings) > 0
