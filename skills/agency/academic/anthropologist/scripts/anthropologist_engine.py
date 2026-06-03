"""Anthropologist reasoning engine for OpenCode Ecosystem.
Cultural analysis, kinship validation, ritual function analysis.

Core rules drawn from structural anthropology (Levi-Strauss),
kinship theory (Murdock, Radcliffe-Brown), and cultural materialism
(Harris, White). Standard library only — regex-based pattern matching
with rule-governed inference.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

# ── Kinship systems catalog ───────────────────────────────────────────
_VALID_KINSHIP: dict[str, dict[str, Any]] = {
    "patrilineal": {
        "descent": "male line",
        "inheritance": "father to son",
        "residence": "patrilocal",
        "lineage": "agnatic",
        "regions": ["Middle East", "East Asia", "patrilineal bands"],
    },
    "matrilineal": {
        "descent": "female line",
        "inheritance": "mother to daughter",
        "residence": "matrilocal",
        "lineage": "uterine",
        "regions": ["Iroquois", "Nayar", "Minangkabau", "Trobriand"],
    },
    "bilateral": {
        "descent": "both lines",
        "inheritance": "equally distributed",
        "residence": "neolocal",
        "lineage": "cognatic",
        "regions": ["modern Western", "Inuit", "!Kung"],
    },
    "ambilineal": {
        "descent": "chosen line",
        "inheritance": "negotiated",
        "residence": "ambilateral",
        "lineage": "ramage",
        "regions": ["Polynesia", "Pacific Northwest"],
    },
    "double": {
        "descent": "parallel lines",
        "inheritance": "split by type",
        "residence": "duolocal",
        "lineage": "double unilineal",
        "regions": ["Yako Nigeria", "Australian aboriginal"],
    },
}

_SUBSISTENCE_PATTERNS: dict[str, list[str]] = {
    "agricultural": [
        r"\bagricultur", r"\bfarm", r"\bcrop\b", r"\bharvest", r"\bcultivat",
        r"\birrigat", r"\bplow", r"\bterrace", r"\bsubsistence\s*farm",
    ],
    "pastoral": [
        r"\bpastoral", r"\bherd", r"\bcattle", r"\bnomad", r"\blivestock",
        r"\bshepherd", r"\btranshumance", r"\bgrazing",
    ],
    "hunter-gatherer": [
        r"\bhunt", r"\bgather", r"\bforag", r"\bfishing\b", r"\btrapping",
        r"\bband\s*society", r"\bseasonal\s*round",
    ],
    "industrial": [
        r"\bindustr", r"\bfactor", r"\burban", r"\bmanufactur", r"\bcapitalis",
        r"\bmarket\s*econom", r"\bwage\s*labor",
    ],
}

_SOCIAL_PATTERNS: dict[str, list[str]] = {
    "band": [r"\bband\b(?!\s*society)", r"\begalitarian\s*band"],
    "tribe": [r"\btribe", r"\btribal", r"\bsegmentary\s*lineage", r"\bbig\s*man"],
    "chiefdom": [r"\bchiefdom", r"\bchieftain", r"\branked\s*society", r"\bredistribut"],
    "state": [r"\bstate\b", r"\bbureaucra", r"\bmonarch", r"\bempire", r"\bstanding\s*army"],
}

_BELIEF_PATTERNS: dict[str, list[str]] = {
    "ancestor_worship": [r"\bancestor\s*worship", r"\bancestor\s*cult", r"\bvenerat.*ancestor"],
    "animism": [r"\banimis", r"\bspirit\s*of\s*nature", r"\banimat"],
    "polytheism": [r"\bpolytheis", r"\bpantheon", r"\bmany\s*gods", r"\bmultiple\s*gods"],
    "monotheism": [r"\bmonotheis", r"\bone\s*god", r"\bsingle\s*god", r"\bsupreme\s*deity"],
    "shamanism": [r"\bshaman", r"\btrance", r"\bspirit\s*healer"],
    "totemism": [r"\btotem", r"\bclan\s*animal", r"\btotemic"],
}

# ── Contradiction rules ───────────────────────────────────────────────
_COHERENCE_RULES: list[dict[str, str | list[str]]] = [
    {
        "if": ["patrilineal", "matrilineal"],
        "then": "Cannot be simultaneously patrilineal and matrilineal in the same descent group",
    },
    {
        "if": ["matrilineal", "patrilocal"],
        "then": "Matrilineal societies typically practice matrilocal or avunculocal residence, not patrilocal",
    },
    {
        "if": ["patrilineal", "matrilocal"],
        "then": "Patrilineal societies rarely practice matrilocal residence",
    },
    {
        "if": ["hunter-gatherer", "state"],
        "then": "Hunter-gatherer bands lack state-level political organization",
    },
    {
        "if": ["agricultural", "hunter-gatherer"],
        "then": "Cannot simultaneously be exclusively agricultural and exclusively hunter-gatherer societies may combine both",
    },
    {
        "if": ["monotheism", "polytheism"],
        "then": "Monotheism and polytheism are generally mutually exclusive at the doctrinal level",
    },
    {
        "if": ["pastoral", "sedentary"],
        "then": "Strict pastoralism requires mobility; sedentary pastoralism needs to specify agro-pastoralism",
    },
]


@dataclass
class CulturalAnalysis:
    """Structured output from anthropological cultural analysis."""

    society_name: str = ""
    subsistence: dict[str, str] = field(default_factory=dict)
    social_organization: dict[str, str] = field(default_factory=dict)
    belief_system: dict[str, str] = field(default_factory=dict)
    coherence_issues: list[str] = field(default_factory=list)
    score: float = 0.0
    _raw_text: str = ""


class AnthropologistEngine:
    """Rule-based cultural analysis engine."""

    def __init__(self) -> None:
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def analyze_culture(self, description: str) -> CulturalAnalysis:
        """Analyze a cultural description for anthropological coherence.

        Extracts subsistence mode, social organization, and belief system
        using regex pattern matching against known anthropological categories.
        """
        analysis = CulturalAnalysis(
            society_name=self._extract_name(description),
            _raw_text=description,
        )

        analysis.subsistence = self._classify(description, _SUBSISTENCE_PATTERNS)
        analysis.social_organization = self._classify(description, _SOCIAL_PATTERNS)
        analysis.belief_system = self._classify(description, _BELIEF_PATTERNS)
        analysis.coherence_issues = self.check_coherence(analysis)
        analysis.score = self._calculate_score(analysis)

        return analysis

    def check_coherence(self, analysis: CulturalAnalysis) -> list[str]:
        issues: list[str] = []
        flat_labels: set[str] = set()

        for cat_labels in [
            analysis.subsistence.values(),
            analysis.social_organization.values(),
            analysis.belief_system.values(),
        ]:
            for label in cat_labels:
                flat_labels.add(label)

        raw_desc = (analysis._raw_text + " " + analysis.society_name).lower()
        kinship_terms = {"matrilineal", "patrilineal", "bilateral", "ambilineal", "double"}
        for kt in kinship_terms:
            if kt in raw_desc:
                flat_labels.add(kt)

        for rule in _COHERENCE_RULES:
            conditions = rule["if"]
            if isinstance(conditions, list) and all(
                any(c.lower() in lbl.lower() for lbl in flat_labels) for c in conditions
            ):
                issues.append(str(rule["then"]))

        kinship_terms = {"matrilineal", "patrilineal", "bilateral", "ambilineal", "double"}
        if len(flat_labels & kinship_terms) > 1:
            issues.append(
                "Multiple kinship/descent systems detected simultaneously; "
                "specify whether different groups or historical periods are being described"
            )

        return issues

    def validate_kinship(self, kinship_type: str) -> dict[str, Any]:
        """Validate a kinship system against known typologies."""
        key = kinship_type.strip().lower().replace(" ", "-")
        if key in _VALID_KINSHIP:
            return {
                "valid": True,
                "type": key,
                "details": _VALID_KINSHIP[key],
            }
        for name, data in _VALID_KINSHIP.items():
            if key in name or name in key:
                return {"valid": True, "type": name, "details": data}

        return {
            "valid": False,
            "type": key,
            "error": f"Unrecognized kinship system '{kinship_type}'. "
            f"Valid systems: {', '.join(_VALID_KINSHIP)}",
            "suggestion": "Consult Murdock's Ethnographic Atlas for known typologies",
        }

    # ── Internal helpers ──────────────────────────────────────────────
    def _extract_name(self, description: str) -> str:
        m = re.search(r'"([^"]+)"', description)
        if m:
            return m.group(1)
        m = re.search(r"'([^']+)'", description)
        if m:
            return m.group(1)
        words = description.split()
        cap_words = [w for w in words if w[0].isupper() and len(w) > 2]
        if cap_words:
            return " ".join(cap_words[:3])
        return description[:60].strip()

    @staticmethod
    def _classify(text: str, patterns: dict[str, list[str]]) -> dict[str, str]:
        result: dict[str, str] = {}
        text_lower = text.lower()
        for category, regex_list in patterns.items():
            for regex in regex_list:
                if re.search(regex, text_lower):
                    result[regex] = category
        return result

    def _calculate_score(self, analysis: CulturalAnalysis) -> float:
        score = 1.0
        if analysis.subsistence:
            score -= 0.05
        if analysis.social_organization:
            score -= 0.10
        if analysis.belief_system:
            score -= 0.05
        for issue in analysis.coherence_issues:
            score -= 0.15
        return max(0.0, min(1.0, score))


# ── CLI demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = AnthropologistEngine()
    print(f"AnthropologistEngine available: {engine.available}")

    samples = [
        "A patrilineal agricultural society with ancestor worship and tribal organization",
        "A matrilineal society where inheritance passes only through fathers",
        "The 'Baktun' people are hunter-gatherers living in egalitarian bands",
    ]
    for desc in samples:
        result = engine.analyze_culture(desc)
        print(f"\n{'='*60}")
        print(f"Society: {result.society_name}")
        print(f"Subsistence: {result.subsistence}")
        print(f"Social org:  {result.social_organization}")
        print(f"Beliefs:     {result.belief_system}")
        print(f"Coherence:   {result.coherence_issues}")
        print(f"Score:       {result.score:.2f}")

    print("\nKinship validation:")
    for ktype in ("patrilineal", "matrilineal", "nonsense_system"):
        print(f"  {ktype}: {engine.validate_kinship(ktype)['valid']}")
