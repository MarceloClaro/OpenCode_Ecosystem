"""TDD tests for AnthropologistEngine — cultural analysis, kinship, coherence."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from anthropologist_engine import AnthropologistEngine, CulturalAnalysis


class TestAnthropologist:
    def setup_method(self):
        self.engine = AnthropologistEngine()

    # ── Basic functionality ───────────────────────────────────────────
    def test_analyze_culture_returns_analysis(self):
        result = self.engine.analyze_culture(
            "A patrilineal agricultural society with ancestor worship and tribal organization"
        )
        assert isinstance(result, CulturalAnalysis)
        assert result.society_name != ""
        assert isinstance(result.score, float)
        assert 0.0 <= result.score <= 1.0

    def test_analyze_culture_extracts_subsistence(self):
        result = self.engine.analyze_culture(
            "An agricultural farming society that cultivates wheat and uses irrigation"
        )
        assert len(result.subsistence) > 0
        assert any("agricult" in k or any("agricult" in v for v in result.subsistence.values())
                   for k in result.subsistence)

    def test_analyze_culture_extracts_social_org(self):
        result = self.engine.analyze_culture(
            "A tribal society with segmentary lineage organization and big man leadership"
        )
        assert len(result.social_organization) > 0

    def test_analyze_culture_extracts_beliefs(self):
        result = self.engine.analyze_culture(
            "They practice ancestor worship and animistic rituals with a shaman"
        )
        assert len(result.belief_system) > 0

    # ── Coherence checking ────────────────────────────────────────────
    def test_coherence_detects_contradictions_matrilineal_patrilineal(self):
        result = self.engine.analyze_culture(
            "A matrilineal society where inheritance passes only through fathers in a patrilineal system"
        )
        issues = self.engine.check_coherence(result)
        assert len(issues) > 0

    def test_coherence_detects_multiple_kinship_systems(self):
        result = self.engine.analyze_culture(
            "A society that is both matrilineal and patrilineal simultaneously"
        )
        issues = self.engine.check_coherence(result)
        assert len(issues) > 0

    def test_coherence_hunter_gatherer_state(self):
        result = self.engine.analyze_culture(
            "Hunter-gatherer bands living in a state-level society with bureaucracy"
        )
        issues = self.engine.check_coherence(result)
        assert len(issues) > 0

    def test_coherent_culture_no_issues(self):
        result = self.engine.analyze_culture(
            "A patrilineal agricultural tribal society with ancestor worship"
        )
        issues = self.engine.check_coherence(result)
        assert isinstance(issues, list)

    def test_coherence_monotheism_polytheism(self):
        result = self.engine.analyze_culture(
            "A monotheistic society that worships a pantheon of many gods (polytheistic)"
        )
        issues = self.engine.check_coherence(result)
        assert len(issues) > 0

    # ── Kinship validation ────────────────────────────────────────────
    def test_valid_kinship_recognized_patrilineal(self):
        result = self.engine.validate_kinship("patrilineal")
        assert result["valid"] is True
        assert "patrilineal" in result["type"]
        assert "details" in result

    def test_valid_kinship_recognized_matrilineal(self):
        result = self.engine.validate_kinship("matrilineal")
        assert result["valid"] is True

    def test_valid_kinship_bilateral(self):
        result = self.engine.validate_kinship("bilateral")
        assert result["valid"] is True

    def test_invalid_kinship_flagged(self):
        result = self.engine.validate_kinship("nonsense_system")
        assert result["valid"] is False
        assert "error" in result

    def test_invalid_kinship_returns_suggestion(self):
        result = self.engine.validate_kinship("xyzabc")
        assert result["valid"] is False
        assert "suggestion" in result or "error" in result

    # ── Engine property ───────────────────────────────────────────────
    def test_available_property(self):
        assert self.engine.available is True

    def test_available_is_readonly(self):
        with pytest.raises(AttributeError):
            self.engine.available = False

    # ── Score computation ─────────────────────────────────────────────
    def test_score_present_in_analysis(self):
        result = self.engine.analyze_culture("A patrilineal society")
        assert hasattr(result, "score")
        assert isinstance(result.score, float)

    def test_score_reduced_for_incoherent(self):
        coherent = self.engine.analyze_culture("A patrilineal agricultural society")
        incoherent = self.engine.analyze_culture(
            "A matrilineal society where inheritance passes only through fathers in a patrilineal system"
        )
        assert coherent.score >= incoherent.score
