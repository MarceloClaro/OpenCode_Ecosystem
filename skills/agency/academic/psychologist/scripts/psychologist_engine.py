"""Psychologist reasoning engine for OpenCode Ecosystem.
Character personality profiling, relationship dynamics analysis,
defense mechanism identification, and attachment style assessment.

Based on:
- Big Five (OCEAN) personality model (Costa & McCrae)
- Attachment theory (Bowlby, Ainsworth)
- Defense mechanisms (Anna Freud, Vaillant)
- Relationship dynamics (Gottman, transactional analysis)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ── Big Five trait markers ────────────────────────────────────────────
_BIG_FIVE_MARKERS: dict[str, dict[str, list[str]]] = {
    "openness": {
        "high": ["curious", "creative", "imaginative", "artistic", "adventurous",
                 "open-minded", "unconventional", "intellectual", "philosophical", "exploratory"],
        "low": ["conventional", "practical", "traditional", "routine-oriented",
                "conservative", "down-to-earth", "prefers familiarity", "cautious with new ideas"],
    },
    "conscientiousness": {
        "high": ["organized", "disciplined", "diligent", "reliable", "responsible",
                 "methodical", "thorough", "goal-oriented", "punctual", "persistent"],
        "low": ["spontaneous", "flexible", "disorganized", "impulsive", "careless",
                "procrastinating", "laid-back", "unstructured", "casual about deadlines"],
    },
    "extraversion": {
        "high": ["outgoing", "energetic", "talkative", "assertive", "sociable",
                 "enthusiastic", "attention-seeking", "gregarious", "lively", "exuberant"],
        "low": ["introverted", "reserved", "quiet", "solitary", "reflective",
                "prefers small groups", "independent", "thoughtful", "private", "withdrawn"],
    },
    "agreeableness": {
        "high": ["compassionate", "cooperative", "trusting", "empathetic", "altruistic",
                 "considerate", "forgiving", "helpful", "warm", "generous"],
        "low": ["skeptical", "competitive", "challenging", "critical", "guarded",
                "blunt", "self-interested", "suspicious", "detached", "argumentative"],
    },
    "neuroticism": {
        "high": ["anxious", "moody", "insecure", "worried", "self-conscious",
                 "emotionally reactive", "prone to stress", "pessimistic", "vulnerable", "tense"],
        "low": ["emotionally stable", "calm", "resilient", "confident", "even-tempered",
                "secure", "relaxed", "adaptable", "unflappable", "optimistic"],
    },
}

_ATTACHMENT_STYLES: dict[str, dict[str, Any]] = {
    "secure": {
        "traits": ["comfortable with intimacy", "trusts others", "balanced independence and closeness",
                   "communicates needs directly", "resilient in conflict"],
        "origin": "Consistent, responsive caregiving in childhood",
    },
    "anxious": {
        "traits": ["fear of abandonment", "seeks constant reassurance", "preoccupied with relationship",
                   "emotional highs and lows", "clinging behavior", "jealousy-prone"],
        "origin": "Inconsistent caregiving — sometimes responsive, sometimes unavailable",
    },
    "avoidant": {
        "traits": ["discomfort with closeness", "values independence above all", "dismissive of emotions",
                   "withdraws under stress", "difficulty trusting", "self-reliant to a fault"],
        "origin": "Consistently unresponsive or rejecting caregiving",
    },
    "disorganized": {
        "traits": ["fear without solution", "approach-avoidance conflict", "unpredictable reactions",
                   "history of trauma or loss", "dissociative tendencies", "confused attachment signals"],
        "origin": "Frightening or frightened caregiving — abuse, neglect, unresolved trauma",
    },
}

_DEFENSE_MECHANISMS: dict[str, dict[str, Any]] = {
    "denial": {
        "indicators": ["refuses to acknowledge", "acts as if nothing happened",
                       "minimizes severity", "insists everything is fine", "doesn't want to talk about it"],
        "level": "primitive",
    },
    "projection": {
        "indicators": ["accuses others of", "everyone else is", "it's not me, it's them",
                       "they are the ones who", "blames others for own feelings"],
        "level": "immature",
    },
    "rationalization": {
        "indicators": ["it's actually a good thing because", "this happened for a reason",
                       "in the long run this is better", "it was for the best",
                       "logical explanation for emotional decision", "well, technically"],
        "level": "neurotic",
    },
    "displacement": {
        "indicators": ["took it out on", "got angry at the wrong person",
                       "kicked the dog", "yelled at subordinates", "transferred frustration to"],
        "level": "neurotic",
    },
    "sublimation": {
        "indicators": ["channeled into work", "threw myself into", "used art to express",
                       "transformed anger into activism", "put energy into exercise"],
        "level": "mature",
    },
    "reaction_formation": {
        "indicators": ["protesting too much", "exaggerated opposite behavior",
                       "over-the-top niceness masking hostility", "zealous opposition to own desires"],
        "level": "neurotic",
    },
    "repression": {
        "indicators": ["can't remember", "blocked it out", "doesn't recall",
                       "vague about details", "unexplained gaps in memory"],
        "level": "neurotic",
    },
    "intellectualization": {
        "indicators": ["analyzes feelings instead of feeling them", "clinical language for personal pain",
                       "detached academic discussion of own trauma", "focuses on facts, avoids emotions"],
        "level": "neurotic",
    },
    "humor": {
        "indicators": ["makes jokes about it", "uses humor to deflect", "laughs it off",
                       "self-deprecating jokes in crisis", "comedic relief in serious situations"],
        "level": "mature",
    },
    "altruism": {
        "indicators": ["helps others with same problem", "becomes advocate for",
                       "volunteers after personal tragedy", "turns pain into service"],
        "level": "mature",
    },
}

_PERSONALITY_DISCLAIMER = (
    "NOT A CLINICAL DIAGNOSIS. This is a literary/character-based personality "
    "profiling tool for narrative analysis. Does not substitute professional "
    "psychological assessment."
)


@dataclass
class PersonalityProfile:
    traits: dict[str, dict[str, Any]]
    summary: str
    disclaimer: str


@dataclass
class DynamicsReport:
    relationship_type: str
    attachment_compatibility: float
    potential_conflicts: list[str]
    potential_strengths: list[str]
    disclaimer: str


class PsychologistEngine:
    """Rule-based character psychology analysis engine."""

    def __init__(self) -> None:
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def profile_character(self, description: str) -> dict[str, Any]:
        """Generate a Big Five (OCEAN) personality profile from a character description."""
        text = description.lower()
        traits: dict[str, dict[str, Any]] = {}

        for trait, markers in _BIG_FIVE_MARKERS.items():
            high_score = sum(1 for m in markers["high"] if m.lower() in text)
            low_score = sum(1 for m in markers["low"] if m.lower() in text)

            if high_score == 0 and low_score == 0:
                percentile = 50
                direction = "neutral"
            else:
                total = high_score + low_score
                if high_score >= low_score:
                    direction = "high"
                    percentile = round(50 + (high_score / total) * 40) if total > 0 else 55
                else:
                    direction = "low"
                    percentile = round(50 - (low_score / total) * 40) if total > 0 else 45

            traits[trait] = {
                "direction": direction,
                "percentile": min(95, max(5, percentile)),
                "evidence_high": [m for m in markers["high"] if m.lower() in text][:5],
                "evidence_low": [m for m in markers["low"] if m.lower() in text][:5],
            }

        highest_trait = max(traits, key=lambda t: traits[t]["percentile"])

        summary = self._generate_summary(traits, highest_trait)

        return {
            "traits": traits,
            "summary": summary,
            "framework": "Big Five (OCEAN) — Costa & McCrae",
            "disclaimer": _PERSONALITY_DISCLAIMER,
        }

    def analyze_dynamics(self, char_a: str, char_b: str) -> dict[str, Any]:
        """Analyze relationship dynamics between two character descriptions."""
        a = char_a.lower()
        b = char_b.lower()

        a_extra = _BIG_FIVE_MARKERS["extraversion"]
        b_extra = _BIG_FIVE_MARKERS["extraversion"]
        a_high_e = any(m in a for m in a_extra["high"])
        b_high_e = any(m in b for m in b_extra["high"])

        a_agree = _BIG_FIVE_MARKERS["agreeableness"]
        b_agree = _BIG_FIVE_MARKERS["agreeableness"]
        a_high_a = any(m in a for m in a_agree["high"])
        b_high_a = any(m in b for m in b_agree["high"])

        a_neuro = _BIG_FIVE_MARKERS["neuroticism"]
        b_neuro = _BIG_FIVE_MARKERS["neuroticism"]
        a_high_n = any(m in a for m in a_neuro["high"])
        b_high_n = any(m in b for m in b_neuro["high"])

        attachment_a = self.assess_attachment_style(char_a)
        attachment_b = self.assess_attachment_style(char_b)

        compatibility = self._compute_attachment_compatibility(attachment_a, attachment_b)

        conflicts: list[str] = []
        strengths: list[str] = []

        if a_high_e and not b_high_e and not any(m in b for m in b_extra["low"]):
            conflicts.append("Extraversion mismatch: one seeks social stimulation, the other may feel drained")
        if a_high_n and b_high_n:
            conflicts.append("Both high in neuroticism: risk of escalating emotional volatility")
        if a_high_a and not b_high_a:
            conflicts.append("Agreeableness asymmetry: one may feel taken advantage of")
        if attachment_a == "anxious" and attachment_b == "avoidant":
            conflicts.append("Anxious-avoidant trap: pursuer-distancer dynamic likely")
        if not a_high_n and not b_high_n:
            strengths.append("Both emotionally stable: conflicts likely resolved calmly")
        if a_high_a and b_high_a:
            strengths.append("Mutual agreeableness: cooperation and empathy should flow easily")

        if not conflicts:
            conflicts.append("No major incompatibilities detected from trait markers")
        if not strengths:
            strengths.append("Compatibility appears neutral — evaluate with deeper context")

        return {
            "character_a_attachment": attachment_a,
            "character_b_attachment": attachment_b,
            "attachment_compatibility": round(compatibility, 3),
            "potential_conflicts": conflicts,
            "potential_strengths": strengths,
            "framework": "Gottman conflict theory + Bowlby attachment + OCEAN trait interaction",
            "disclaimer": _PERSONALITY_DISCLAIMER,
        }

    def identify_defense_mechanisms(self, behavior: str) -> list[dict[str, Any]]:
        """Identify defense mechanisms present in a behavioral description."""
        text = behavior.lower()
        findings: list[dict[str, Any]] = []

        for mechanism, data in _DEFENSE_MECHANISMS.items():
            matches = []
            pattern_matches: list[str] = []
            for indicator in data["indicators"]:
                indicator_lower = indicator.lower()
                words = indicator_lower.split()
                if len(words) >= 3:
                    key_terms = [w for w in words if len(w) > 3]
                    if key_terms and all(term in text for term in key_terms):
                        matches.append(indicator)
                        continue
                if indicator_lower in text:
                    matches.append(indicator)
                    continue
                if re.search(re.escape(indicator_lower), text):
                    pattern_matches.append(indicator)

            if matches or pattern_matches:
                findings.append({
                    "mechanism": mechanism,
                    "level": data["level"],
                    "evidence": matches + pattern_matches,
                    "confidence": min(0.95, len(matches) * 0.3 + len(pattern_matches) * 0.2 + 0.3),
                })

        return sorted(findings, key=lambda x: x["confidence"], reverse=True)

    def assess_attachment_style(self, relationship_desc: str) -> str:
        """Identify attachment style from a relationship description."""
        text = relationship_desc.lower()
        scores: dict[str, int] = {}

        for style, data in _ATTACHMENT_STYLES.items():
            score = 0
            for trait in data["traits"]:
                for word in trait.split():
                    if len(word) > 3 and word in text:
                        score += 1
                phrase = trait.lower()
                if phrase in text:
                    score += 2
            scores[style] = score

        best = max(scores, key=scores.__getitem__)
        if scores[best] == 0:
            return "secure"

        runner_up = sorted(scores, key=scores.__getitem__, reverse=True)[1]
        if scores[best] == scores[runner_up] and scores[best] > 0:
            return f"{best}/{runner_up} (mixed presentation)"

        return best

    # ── Helpers ───────────────────────────────────────────────────────
    @staticmethod
    def _generate_summary(traits: dict[str, dict[str, Any]], highest: str) -> str:
        high_dir = traits[highest]["direction"]
        summaries: dict[str, str] = {
            "openness": "highly creative and intellectually curious" if high_dir == "high" else "practical and conventional in approach",
            "conscientiousness": "highly organized and disciplined" if high_dir == "high" else "spontaneous and flexible in style",
            "extraversion": "outgoing and socially energized" if high_dir == "high" else "introspective and reserved",
            "agreeableness": "empathetic and cooperative" if high_dir == "high" else "skeptical and independent-minded",
            "neuroticism": "emotionally sensitive and reactive" if high_dir == "high" else "emotionally stable and resilient",
        }
        return f"Primary trait: high {highest} — {summaries.get(highest, 'balanced profile')}"

    @staticmethod
    def _compute_attachment_compatibility(style_a: str, style_b: str) -> float:
        matrix: dict[tuple[str, str], float] = {
            ("secure", "secure"): 0.95,
            ("secure", "anxious"): 0.65,
            ("anxious", "secure"): 0.65,
            ("secure", "avoidant"): 0.50,
            ("avoidant", "secure"): 0.50,
            ("secure", "disorganized"): 0.35,
            ("disorganized", "secure"): 0.35,
            ("anxious", "anxious"): 0.40,
            ("avoidant", "avoidant"): 0.30,
            ("anxious", "avoidant"): 0.20,
            ("avoidant", "anxious"): 0.20,
            ("disorganized", "disorganized"): 0.15,
        }
        base_a = style_a.split("/")[0].strip()
        base_b = style_b.split("/")[0].strip()
        return matrix.get((base_a, base_b), 0.50)


# ── CLI demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = PsychologistEngine()
    print(f"PsychologistEngine available: {engine.available}")

    char_desc = (
        "A curious, imaginative, and creative individual who is somewhat disorganized "
        "and introverted. They are compassionate and trusting, but also anxious and "
        "prone to worry. They withdraw under stress and find it hard to trust others."
    )
    print("\nBig Five Profile:")
    profile = engine.profile_character(char_desc)
    for trait, data in profile["traits"].items():
        print(f"  {trait}: {data['direction']} ({data['percentile']}%)")
    print(f"  Summary: {profile['summary']}")

    print("\nDefense mechanisms:")
    for dm in engine.identify_defense_mechanisms("He keeps insisting everything is fine even though he lost his job. He jokes about it constantly and says it's actually a good thing because now he has more time."):
        print(f"  {dm['mechanism']} ({dm['level']}): {dm['confidence']:.2f}")

    print("\nAttachment style:")
    print(f"  {engine.assess_attachment_style('She fears abandonment and constantly seeks reassurance from her partner, experiencing emotional highs and lows. She is clingy and jealous.')}")

    print("\nRelationship dynamics:")
    dyn = engine.analyze_dynamics(
        "outgoing, talkative, assertive person who trusts easily and is emotionally stable",
        "quiet, reserved, withdrawn person who is suspicious of others and anxious"
    )
    print(f"  Attachment A: {dyn['character_a_attachment']}")
    print(f"  Attachment B: {dyn['character_b_attachment']}")
    print(f"  Compatibility: {dyn['attachment_compatibility']}")
    print(f"  Conflicts: {dyn['potential_conflicts']}")
