"""TDD tests for NarratologistEngine — structure, character, controlling idea, genre."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from narratologist_engine import NarratologistEngine


class TestNarratologist:
    def setup_method(self):
        self.engine = NarratologistEngine()

    # ── Controlling idea ──────────────────────────────────────────────
    def test_controlling_idea_found_explicit(self):
        result = self.engine.identify_controlling_idea(
            "The theme is: 'Love conquers all obstacles through sacrifice'"
        )
        assert result is not None
        assert len(result) > 0
        assert isinstance(result, str)

    def test_controlling_idea_found_descriptive(self):
        result = self.engine.identify_controlling_idea(
            "A story about redemption and forgiveness that explores the depths of human cruelty"
        )
        assert len(result) > 0

    def test_controlling_idea_not_empty_fallback(self):
        result = self.engine.identify_controlling_idea("A simple story")
        assert len(result) > 0
        assert isinstance(result, str)

    # ── Character assessment ──────────────────────────────────────────
    def test_character_has_want_need_lie(self):
        result = self.engine.assess_character(
            "A young hero who wants revenge to avenge his family, needs to learn forgiveness. "
            "He believes that vengeance will bring him peace."
        )
        assert "want" in result
        assert "need" in result
        assert "lie" in result
        assert len(result["want"]) > 0
        assert len(result["need"]) > 0

    def test_character_archetype_identified(self):
        result = self.engine.assess_character(
            "A wise old mentor who teaches the young hero and guides them through training"
        )
        assert result["archetype"] in ("hero", "mentor", "shadow", "trickster", "herald")

    def test_character_shadow_archetype(self):
        result = self.engine.assess_character(
            "A dark villain who seeks to destroy everything and corrupt the innocent"
        )
        assert result["archetype"] == "shadow"

    def test_framework_cited_in_character(self):
        result = self.engine.assess_character("A brave protagonist seeking glory")
        assert "framework_cited" in result
        assert len(result["framework_cited"]) > 0

    def test_arc_type_detected(self):
        result = self.engine.assess_character(
            "A character who grows and transforms through the journey, learning valuable lessons"
        )
        assert "arc_type" in result
        assert result["arc_type"] is not None

    # ── Structure analysis ────────────────────────────────────────────
    def test_structure_identified_hero_journey(self):
        result = self.engine.analyze_structure(
            "ordinary world, call to adventure, refusal, mentor, crossing threshold, "
            "tests and allies, approach inmost cave, ordeal, reward, road back, "
            "resurrection, return with elixir"
        )
        assert result["structure_type"] is not None
        assert len(result["structure_type"]) > 0

    def test_structure_identified_three_act(self):
        result = self.engine.analyze_structure(
            "A story with inciting incident, plot point 1, midpoint, plot point 2, climax"
        )
        assert "structure_type" in result
        assert "framework_cited" in result

    def test_structure_completeness_range(self):
        result = self.engine.analyze_structure("A basic story with a climax")
        assert 0.0 <= result["completeness"] <= 1.0

    def test_structure_detected_elements_present(self):
        result = self.engine.analyze_structure(
            "ordinary world and call to adventure with a climax"
        )
        assert "detected_elements" in result
        assert isinstance(result["detected_elements"], list)

    def test_framework_cited_in_structure(self):
        result = self.engine.analyze_structure("A hero in the ordinary world receives a call to adventure")
        assert len(result["framework_cited"]) > 0

    # ── Genre conventions ─────────────────────────────────────────────
    def test_genre_conventions_tragedy(self):
        result = self.engine.check_genre_conventions(
            "A flawed protagonist of noble birth experiences a reversal of fortune "
            "leading to recognition and catharsis", "tragedy"
        )
        assert result is not None
        assert "required_conventions_met" in result

    def test_genre_conventions_adherence_score(self):
        result = self.engine.check_genre_conventions(
            "A flawed protagonist with reversal of fortune achieving recognition", "tragedy"
        )
        assert "adherence_score" in result
        assert 0.0 <= result["adherence_score"] <= 1.0

    def test_genre_conventions_unknown_genre(self):
        result = self.engine.check_genre_conventions("A story", "nonexistent_genre_xyz")
        assert "error" in result or "known_genres" in result

    def test_genre_conventions_includes_conflict_type(self):
        result = self.engine.check_genre_conventions("A flawed protagonist", "tragedy")
        assert "conflict_type" in result

    # ── Engine property ───────────────────────────────────────────────
    def test_available_property(self):
        assert self.engine.available is True

    # ── Framework presence ────────────────────────────────────────────
    def test_framework_cited_overall(self):
        struct = self.engine.analyze_structure("call to adventure, crossroads, climax")
        assert "framework_cited" in struct
        assert any(name in struct["framework_cited"] for name in ["Campbell", "Vogler", "Field", "McKee", "Snyder", "Freytag", "Truby"])
