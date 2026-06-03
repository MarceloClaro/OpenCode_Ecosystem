"""TDD tests for PsychologistEngine — Big Five profiling, attachment, defense mechanisms, dynamics."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from psychologist_engine import PsychologistEngine


class TestPsychologist:
    def setup_method(self):
        self.engine = PsychologistEngine()

    # ── Big Five profile ──────────────────────────────────────────────
    def test_big_five_profile_returns_all_five(self):
        result = self.engine.profile_character(
            "A curious, organized, outgoing, compassionate, and anxious person"
        )
        assert "traits" in result
        for trait in ["openness", "conscientiousness", "extraversion", "agreeableness", "neuroticism"]:
            assert trait in result["traits"], f"Missing trait: {trait}"
            assert "direction" in result["traits"][trait]
            assert "percentile" in result["traits"][trait]

    def test_big_five_high_openness_detected(self):
        result = self.engine.profile_character(
            "A highly curious, creative, imaginative, adventurous, and unconventional thinker"
        )
        assert result["traits"]["openness"]["direction"] == "high"
        assert result["traits"]["openness"]["percentile"] > 50

    def test_big_five_low_extraversion_detected(self):
        result = self.engine.profile_character(
            "An introverted, quiet, reserved, solitary person who prefers small groups"
        )
        assert result["traits"]["extraversion"]["direction"] == "low"

    def test_big_five_percentile_range(self):
        result = self.engine.profile_character("A curious and creative person")
        for data in result["traits"].values():
            assert 5 <= data["percentile"] <= 95

    def test_big_five_includes_summary(self):
        result = self.engine.profile_character("An organized and diligent person")
        assert "summary" in result
        assert len(result["summary"]) > 0

    def test_big_five_includes_framework_name(self):
        result = self.engine.profile_character("A person")
        assert "framework" in result
        assert "Big Five" in result["framework"] or "OCEAN" in result["framework"]

    # ── Attachment style ──────────────────────────────────────────────
    def test_attachment_style_detected_anxious(self):
        result = self.engine.assess_attachment_style(
            "She fears abandonment and constantly seeks reassurance, "
            "experiencing emotional highs and lows with clinging behavior"
        )
        assert result == "anxious"

    def test_attachment_style_detected_secure(self):
        result = self.engine.assess_attachment_style(
            "He is comfortable with intimacy, trusts others, and communicates "
            "his needs directly, staying resilient in conflict"
        )
        assert result == "secure"

    def test_attachment_style_detected_avoidant(self):
        result = self.engine.assess_attachment_style(
            "Discomfort with closeness, values independence above all, "
            "dismissive of emotions, withdraws under stress"
        )
        assert result == "avoidant"

    def test_attachment_style_defaults_to_secure(self):
        result = self.engine.assess_attachment_style("A normal person")
        assert result == "secure"

    # ── Defense mechanisms ────────────────────────────────────────────
    def test_defense_mechanism_identified_denial(self):
        result = self.engine.identify_defense_mechanisms(
            "He refuses to acknowledge what happened and insists everything is fine"
        )
        mechanisms = [d["mechanism"] for d in result]
        assert "denial" in mechanisms

    def test_defense_mechanism_identified_rationalization(self):
        result = self.engine.identify_defense_mechanisms(
            "She says it's actually a good thing because this happened for a reason"
        )
        mechanisms = [d["mechanism"] for d in result]
        assert "rationalization" in mechanisms

    def test_defense_mechanism_identified_sublimation(self):
        result = self.engine.identify_defense_mechanisms(
            "He channeled his anger into work and transformed it into activism"
        )
        mechanisms = [d["mechanism"] for d in result]
        assert "sublimation" in mechanisms

    def test_defense_mechanism_confidence_range(self):
        result = self.engine.identify_defense_mechanisms("refuses to acknowledge the problem")
        if result:
            for d in result:
                assert 0.0 < d["confidence"] <= 1.0

    def test_defense_mechanism_returns_evidence(self):
        result = self.engine.identify_defense_mechanisms(
            "He insists everything is fine and refuses to acknowledge anything"
        )
        if result:
            assert "evidence" in result[0]

    # ── Not reduced to diagnosis ──────────────────────────────────────
    def test_not_reduced_to_diagnosis(self):
        result = self.engine.profile_character(
            "A person who is sometimes anxious and sometimes calm"
        )
        assert "disclaimer" in result
        assert "DIAGNOSIS" in result["disclaimer"].upper() or "diagnos" in result["disclaimer"].lower()

    # ── Relationship dynamics ─────────────────────────────────────────
    def test_relationship_dynamics_returns_attachment(self):
        result = self.engine.analyze_dynamics(
            "outgoing and trusting person", "quiet and suspicious person"
        )
        assert "character_a_attachment" in result
        assert "character_b_attachment" in result

    def test_relationship_compatibility_range(self):
        result = self.engine.analyze_dynamics(
            "trusting, comfortable with intimacy", "also trusting and intimate"
        )
        assert 0.0 <= result["attachment_compatibility"] <= 1.0

    def test_relationship_conflicts_detected(self):
        result = self.engine.analyze_dynamics(
            "anxious and clingy, fears abandonment",
            "dismissive of emotions, withdraws under stress"
        )
        assert "potential_conflicts" in result
        assert "potential_strengths" in result
        assert len(result["potential_conflicts"]) > 0 or result["attachment_compatibility"] < 0.5

    def test_relationship_disclaimer_present(self):
        result = self.engine.analyze_dynamics("Person A", "Person B")
        assert "disclaimer" in result

    # ── Engine property ───────────────────────────────────────────────
    def test_available_property(self):
        assert self.engine.available is True

    def test_available_is_readonly(self):
        with pytest.raises(AttributeError):
            self.engine.available = False
