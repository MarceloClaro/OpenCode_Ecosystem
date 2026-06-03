"""Narratologist reasoning engine for OpenCode Ecosystem.
Narrative structure analysis, character assessment, controlling idea
identification, and genre convention checking.

Based on frameworks from:
- Robert McKee (Story: Substance, Structure, Style)
- John Truby (The Anatomy of Story)
- Christopher Vogler (The Writer's Journey / Hero's Journey)
- Syd Field (Screenplay paradigm)
- Vladimir Propp (Morphology of the Folktale)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ── Narrative frameworks ──────────────────────────────────────────────
_STRUCTURE_TYPES: dict[str, dict[str, Any]] = {
    "three_act": {
        "name": "Three-Act Structure",
        "acts": ["Setup", "Confrontation", "Resolution"],
        "key_points": ["inciting_incident", "plot_point_1", "midpoint", "plot_point_2", "climax"],
        "framework_source": "Syd Field / McKee",
    },
    "hero_journey": {
        "name": "Hero's Journey (Monomyth)",
        "acts": ["Departure", "Initiation", "Return"],
        "key_points": ["ordinary_world", "call_to_adventure", "refusal", "mentor", "crossing_threshold",
                       "tests_allies_enemies", "approach_inmost_cave", "ordeal", "reward",
                       "road_back", "resurrection", "return_with_elixir"],
        "framework_source": "Joseph Campbell / Christopher Vogler",
    },
    "five_act": {
        "name": "Five-Act Structure",
        "acts": ["Exposition", "Rising Action", "Climax", "Falling Action", "Denouement"],
        "key_points": ["exposition", "complication", "crisis", "catastrophe", "recognition"],
        "framework_source": "Freytag / Shakespearean",
    },
    "save_the_cat": {
        "name": "Save the Cat Beat Sheet",
        "acts": ["Thesis World", "Antithesis World", "Synthesis World"],
        "key_points": ["opening_image", "theme_stated", "setup", "catalyst", "debate",
                       "break_into_two", "b_story", "fun_and_games", "midpoint",
                       "bad_guys_close_in", "all_is_lost", "dark_night_of_soul",
                       "break_into_three", "finale", "final_image"],
        "framework_source": "Blake Snyder",
    },
}

_GENRE_CONVENTIONS: dict[str, dict[str, Any]] = {
    "hero_epic": {
        "required": ["protagonist_of_great_importance", "vast_setting", "supernatural_intervention",
                     "elevated_style", "objective_tone"],
        "optional": ["catalogues", "epic_similes", "invocation_of_muse", "in_medias_res"],
        "conflict_type": "external — fate, gods, massive forces",
    },
    "tragedy": {
        "required": ["flawed_protagonist", "hamartia", "reversal_of_fortune", "recognition", "catharsis"],
        "optional": ["unity_of_time_place_action", "chorus", "noble_birth_protagonist"],
        "conflict_type": "internal + external — character flaw meets circumstance",
    },
    "bildungsroman": {
        "required": ["youthful_protagonist", "psychological_growth", "conflict_with_society",
                     "epiphany_moment", "maturity_conclusion"],
        "optional": ["mentor_figure", "leaving_home", "love_interest", "education_theme"],
        "conflict_type": "internal — self vs. society's expectations",
    },
    "mystery": {
        "required": ["crime_or_puzzle", "investigator", "clues_and_red_herrings", "resolution_reveal"],
        "optional": ["sidekick", "suspect_pool", "twist_ending", "fair_play_principle"],
        "conflict_type": "intellectual — truth vs. deception",
    },
    "romance": {
        "required": ["two_protagonists", "obstacles_to_love", "emotional_vulnerability", "happy_ending_or_bittersweet"],
        "optional": ["meet_cute", "grand_gesture", "rival_love_interest", "separation_phase"],
        "conflict_type": "emotional — connection vs. barriers",
    },
    "science_fiction": {
        "required": ["speculative_element", "world_building", "logical_extrapolation", "human_condition_examination"],
        "optional": ["advanced_technology", "alien_life", "dystopia_or_utopia", "time_travel"],
        "conflict_type": "conceptual — humanity vs. technology/the unknown",
    },
}

_CHARACTER_ARCHETYPES: dict[str, dict[str, Any]] = {
    "hero": {"want": "external_goal", "need": "internal_lesson", "lie": "false_belief_about_self_or_world"},
    "mentor": {"want": "to_guide", "need": "to_let_go", "lie": "my_wisdom_must_be_followed"},
    "shadow": {"want": "same_as_hero_but_different_method", "need": "recognition", "lie": "power_will_fulfill_me"},
    "trickster": {"want": "chaos_or_amusement", "need": "belonging", "lie": "nothing_matters"},
    "herald": {"want": "to_deliver_message", "need": "to_be_heard", "lie": "change_is_optional"},
}


@dataclass
class StructureAnalysis:
    structure_type: str
    framework_cited: str
    detected_elements: list[str]
    missing_elements: list[str]
    completeness: float


@dataclass
class CharacterAssessment:
    want: str
    need: str
    lie: str
    archetype: str
    arc_type: str
    framework_cited: str = "Truby/McKee"


class NarratologistEngine:
    """Rule-based narratological analysis engine."""

    def __init__(self) -> None:
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def analyze_structure(self, story_description: str) -> dict[str, Any]:
        """Identify narrative structure elements from a story description."""
        text = story_description.lower()

        structure_scores: dict[str, int] = {}
        for struct_key, struct_data in _STRUCTURE_TYPES.items():
            score = 0
            for kp in struct_data["key_points"]:
                pattern = re.compile(rf'\b{re.escape(kp.replace("_", " "))}\b')
                if pattern.search(text):
                    score += 1
                pattern_underscore = re.compile(rf'\b{re.escape(kp)}\b')
                if pattern_underscore.search(text):
                    score += 1
            structure_scores[struct_key] = score

        best_match = max(structure_scores, key=structure_scores.__getitem__)
        best_data = _STRUCTURE_TYPES[best_match]

        detected: list[str] = []
        missing: list[str] = []
        for kp in best_data["key_points"]:
            if re.search(rf'\b{re.escape(kp.replace("_", " "))}\b', text) or re.search(rf'\b{re.escape(kp)}\b', text):
                detected.append(kp)
            else:
                missing.append(kp)

        completeness = len(detected) / len(best_data["key_points"]) if best_data["key_points"] else 0

        return {
            "structure_type": best_data["name"],
            "framework_cited": best_data["framework_source"],
            "detected_elements": detected,
            "missing_elements": missing,
            "completeness": round(completeness, 3),
            "alternative_matches": sorted(
                [(k, v) for k, v in structure_scores.items() if k != best_match and v > 0],
                key=lambda x: x[1], reverse=True,
            ),
        }

    def assess_character(self, character_desc: str) -> dict[str, Any]:
        """Assess a character description for want/need/lie and archetype."""
        text = character_desc.lower()

        want = self._extract_want(text)
        need = self._infer_need(text, want)
        lie = self._infer_lie(text, want, need)
        archetype = self._classify_archetype(text)
        arc_type = self._infer_arc(text, want, need)

        return {
            "want": want,
            "need": need,
            "lie": lie,
            "archetype": archetype,
            "arc_type": arc_type,
            "framework_cited": "Truby / McKee / Vogler",
        }

    def identify_controlling_idea(self, story: str) -> str:
        """Extract the controlling idea (theme) from a story description."""
        text = story.lower()

        theme_patterns: list[tuple[str, str]] = [
            (r'\b(?:because|when|if)\s+.*?\b(?:then|leads to|results in|ultimately)\b', "causal"),
            (r'(?:theme|message|moral|lesson)\s*(?:is|:)\s*"([^"]+)"', "explicit"),
            (r'(?:theme|message|moral|lesson)\s*(?:is|:)\s*\'([^\']+)\'', "explicit"),
            (r'(?:about|explores)\s+(\w[\w\s]{3,50}?)\s+(?:and|through|by|via)', "descriptive"),
        ]

        for pattern, ptype in theme_patterns:
            m = re.search(pattern, text)
            if m:
                groups = m.groups()
                return groups[0].strip().capitalize() if groups else m.group(0).strip()

        ideas = re.findall(r'(?:idea|theme|meaning)\s*(?:of|behind)\s+(\w[\w\s]{3,50})', text)
        if ideas:
            return f"Explores {ideas[0].strip()}"

        return "Controlling idea not explicitly stated; narrative implies exploration of human nature"

    def check_genre_conventions(self, story: str, genre: str) -> dict[str, Any]:
        """Check how well a story adheres to genre conventions."""
        text = story.lower()
        genre_key = genre.lower().replace(" ", "_").replace("-", "_")

        genre_data = _GENRE_CONVENTIONS.get(genre_key)
        if not genre_data:
            for name, data in _GENRE_CONVENTIONS.items():
                if genre_key in name or name in genre_key:
                    genre_data = data
                    genre_key = name
                    break

        if not genre_data:
            return {
                "genre": genre,
                "error": f"Genre '{genre}' not in conventions database",
                "known_genres": list(_GENRE_CONVENTIONS.keys()),
            }

        met_required: list[str] = []
        unmet_required: list[str] = []
        for req in genre_data["required"]:
            term = req.replace("_", " ")
            if term in text or req in text:
                met_required.append(req)
            else:
                unmet_required.append(req)

        met_optional: list[str] = []
        for opt in genre_data["optional"]:
            term = opt.replace("_", " ")
            if term in text or opt in text:
                met_optional.append(opt)

        adherence = len(met_required) / len(genre_data["required"]) if genre_data["required"] else 0

        return {
            "genre": genre_data.get("name", genre),
            "conflict_type": genre_data["conflict_type"],
            "required_conventions_met": met_required,
            "required_conventions_missing": unmet_required,
            "optional_conventions_present": met_optional,
            "adherence_score": round(adherence, 3),
            "framework_cited": "McKee / Field genre conventions",
        }

    # ── Helpers ───────────────────────────────────────────────────────
    @staticmethod
    def _extract_want(text: str) -> str:
        patterns = [
            r'wants?\s+(?:to\s+)?([\w\s]{3,40}?)(?:\.|,|but|and|while)',
            r'(?:goal|objective|desire)\s*(?:is|:)\s*([\w\s]{3,40}?)(?:\.|,)',
            r'(?:seeks?|pursues?|strives?\s+for)\s+([\w\s]{3,40}?)(?:\.|,)',
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1).strip()
        return "unstated (infer from character actions)"

    @staticmethod
    def _infer_need(text: str, want: str) -> str:
        need_patterns = [
            r'needs?\s+(?:to\s+)?([\w\s]{3,40}?)(?:\.|,|but|and)',
            r'must\s+(?:learn|accept|realize|understand)\s+([\w\s]{3,40}?)(?:\.|,)',
        ]
        for pat in need_patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1).strip()

        need_hints = {
            "power": "learn humility or responsibility",
            "revenge": "find peace or forgiveness",
            "wealth": "discover what truly matters",
            "fame": "find authentic self-worth",
            "love": "learn to love self first",
            "survival": "find meaning beyond survival",
            "freedom": "accept responsibility that comes with freedom",
            "knowledge": "apply wisdom with compassion",
            "approval": "develop internal validation",
            "control": "learn to trust and let go",
        }
        for kw, hint in need_hints.items():
            if kw in want.lower():
                return hint
        return "internal transformation (to be discovered)"

    @staticmethod
    def _infer_lie(text: str, want: str, need: str) -> str:
        lie_patterns = [
            r'believes?\s+(?:that\s+)?([\w\s]{3,60}?)(?:\.|,|but)',
            r'(?:false|mistaken)\s+belief\s+(?:that|about)\s+([\w\s]{3,60}?)(?:\.|,)',
        ]
        for pat in lie_patterns:
            m = re.search(pat, text)
            if m:
                return m.group(1).strip()

        return f"Believes that achieving '{want}' will bring fulfillment, when actually needs '{need}'"

    @staticmethod
    def _classify_archetype(text: str) -> str:
        scores: dict[str, int] = {}
        archetype_keywords: dict[str, list[str]] = {
            "hero": ["hero", "protagonist", "chosen", "destiny", "brave", "save", "protect"],
            "mentor": ["mentor", "guide", "teach", "wise", "elder", "master", "train"],
            "shadow": ["villain", "dark", "shadow", "enemy", "evil", "destroy", "corrupt"],
            "trickster": ["trick", "deceive", "joke", "prank", "chaos", "mischief", "clever"],
            "herald": ["herald", "messenger", "news", "announce", "prophecy", "call"],
        }
        for arch, keywords in archetype_keywords.items():
            scores[arch] = sum(1 for kw in keywords if kw in text)
        if max(scores.values()) == 0:
            return "hero"
        return max(scores, key=scores.__getitem__)

    @staticmethod
    def _infer_arc(text: str, want: str, need: str) -> str:
        if any(w in text for w in ["change", "transform", "learn", "grow", "realize", "accept"]):
            return "positive_change_arc"
        if any(w in text for w in ["fall", "corrupt", "decline", "tragic", "destroy", "lose"]):
            return "negative_change_arc (tragic)"
        if any(w in text for w in ["flat", "unchanged", "steadfast", "unchanging"]):
            return "flat_arc (character changes world)"
        return "positive_change_arc (default assumption)"


# ── CLI demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = NarratologistEngine()
    print(f"NarratologistEngine available: {engine.available}")

    story = (
        "A hero's journey: ordinary world, then call to adventure. "
        "The mentor guides the hero through the crossing threshold into tests and allies. "
        "The ordeal at the inmost cave leads to reward and road back, "
        "culminating in resurrection and return with elixir."
    )
    print("\nStructure analysis:")
    struct = engine.analyze_structure(story)
    print(f"  Type: {struct['structure_type']}")
    print(f"  Framework: {struct['framework_cited']}")
    print(f"  Completeness: {struct['completeness']}")

    char_desc = "A young hero who wants power to avenge his parents, needs to learn forgiveness. He believes revenge will bring him peace."
    print("\nCharacter assessment:")
    char = engine.assess_character(char_desc)
    print(f"  Want: {char['want']}")
    print(f"  Need: {char['need']}")
    print(f"  Lie: {char['lie']}")
    print(f"  Framework: {char['framework_cited']}")

    print("\nControlling idea:")
    print(f"  {engine.identify_controlling_idea('A story about love and sacrifice where the theme is: true love requires letting go')}")

    print("\nGenre check (tragedy):")
    tragedy = "A flawed protagonist of noble birth experiences a reversal of fortune leading to recognition and catharsis"
    gc = engine.check_genre_conventions(tragedy, "tragedy")
    print(f"  Required met: {gc['required_conventions_met']}")
    print(f"  Adherence: {gc['adherence_score']}")
