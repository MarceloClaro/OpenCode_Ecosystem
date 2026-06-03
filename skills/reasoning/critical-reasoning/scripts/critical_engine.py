"""Critical Reasoning Engine — Argument Analysis for OpenCode Ecosystem.

Decomposes arguments, detects logical fallacies, evaluates argument
strength, and generates counter-arguments.
"""

from typing import Any, Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
import re
import time


FALLACIES = {
    "ad_hominem": {
        "name": "Ad Hominem",
        "pattern": r"(you are|you're)\s+(stupid|wrong|biased|ignorant|lying)",
        "description": "Attacks the person instead of the argument"
    },
    "straw_man": {
        "name": "Straw Man",
        "pattern": r"(so you('re| are) saying|you think|you believe)",
        "description": "Misrepresents opponent's position to attack it more easily"
    },
    "false_dilemma": {
        "name": "False Dilemma",
        "pattern": r"(either|only two|just two|binary).*(or|choice)",
        "description": "Presents only two options when more exist"
    },
    "slippery_slope": {
        "name": "Slippery Slope",
        "pattern": r"(if we|once we|this will lead to).*(then|eventually|ultimately)",
        "description": "Claims one action will inevitably lead to extreme consequences"
    },
    "appeal_to_authority": {
        "name": "Appeal to Authority",
        "pattern": r"(according to|experts say|scientists say|studies show)(?!.*doi|.*DOI|.*arXiv)",
        "description": "Cites authority without providing specific evidence"
    },
    "hasty_generalization": {
        "name": "Hasty Generalization",
        "pattern": r"(always|never|everyone|nobody|all|none)\s",
        "description": "Draws universal conclusion from insufficient evidence"
    },
    "post_hoc": {
        "name": "Post Hoc Ergo Propter Hoc",
        "pattern": r"(after|since|because of).*(then|therefore|consequently)",
        "description": "Assumes causation from temporal sequence"
    },
    "begging_question": {
        "name": "Begging the Question",
        "pattern": r"(obviously|clearly|of course|naturally|everyone knows)",
        "description": "Assumes the conclusion in the premise"
    },
    "red_herring": {
        "name": "Red Herring",
        "pattern": r"(but what about|what about|yes but|however).{50,}",
        "description": "Introduces irrelevant topic to distract"
    },
    "circular_reasoning": {
        "name": "Circular Reasoning",
        "pattern": r"(because.*therefore|thus.*because|hence.*since)",
        "description": "Uses the conclusion as a premise"
    },
    "appeal_to_emotion": {
        "name": "Appeal to Emotion",
        "pattern": r"(think of the children|imagine if|what if it were your|terrible|horrific|disgusting)",
        "description": "Manipulates emotions instead of using logic"
    },
    "bandwagon": {
        "name": "Bandwagon",
        "pattern": r"(everyone is|most people|everybody|all the)",
        "description": "Claims something is true because many believe it"
    },
    "false_equivalence": {
        "name": "False Equivalence",
        "pattern": r"(just like|same as|no different from|equivalent to)",
        "description": "Falsely equates two incomparable things"
    },
    "composition_fallacy": {
        "name": "Composition Fallacy",
        "pattern": r"(each|every part|every member).*(therefore|so|thus).*(whole|entire|all)",
        "description": "Assumes whole has same properties as parts"
    },
    "division_fallacy": {
        "name": "Division Fallacy",
        "pattern": r"(the whole|the entire|the system).*(therefore|so|thus).*(each|every)",
        "description": "Assumes parts have same properties as whole"
    },
}

COGNITIVE_BIASES = {
    "confirmation_bias": "Favoring information that confirms existing beliefs",
    "anchoring": "Relying too heavily on first piece of information",
    "availability": "Overestimating importance of recent/memorable information",
    "overconfidence": "Excessive confidence in one's own judgment",
    "framing": "Drawing different conclusions from same data based on presentation",
}


@dataclass
class ArgumentAnalysis:
    text: str
    premises: List[str] = field(default_factory=list)
    conclusions: List[str] = field(default_factory=list)
    hidden_assumptions: List[str] = field(default_factory=list)
    fallacies: List[Dict[str, str]] = field(default_factory=list)
    biases: List[str] = field(default_factory=list)
    strength: str = "unknown"
    score: float = 0.0
    counterarguments: List[str] = field(default_factory=list)
    time_ms: float = 0.0


class CriticalEngine:
    """Motor de raciocinio critico para analise de argumentos."""

    def __init__(self):
        self.fallacies = FALLACIES
        self.biases = COGNITIVE_BIASES
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def analyze(self, text: str) -> ArgumentAnalysis:
        """Analisa um argumento completo."""
        t0 = time.time()

        analysis = ArgumentAnalysis(text=text)

        analysis.premises = self._extract_premises(text)
        analysis.conclusions = self._extract_conclusions(text)
        analysis.hidden_assumptions = self._detect_hidden_assumptions(text)
        analysis.fallacies = self._detect_fallacies(text)
        analysis.biases = self._detect_biases(text)
        analysis.strength, analysis.score = self._evaluate_strength(analysis)
        analysis.counterarguments = self._generate_counterarguments(analysis)
        analysis.time_ms = (time.time() - t0) * 1000

        return analysis

    def _extract_premises(self, text: str) -> List[str]:
        """Extrai premissas do texto."""
        premises = []
        indicators = [
            r"(?:since|because|given that|assuming that|as|for)\s+(.+?)(?:,|\.|\s*$)",
            r"(?:first|second|third)[,\.]\s*(.+?)(?:\.|;|$)",
            r"^(.+?)(?:\.|;)\s*(?:therefore|thus|hence|so|consequently)",
        ]
        for indicator in indicators:
            matches = re.findall(indicator, text, re.IGNORECASE)
            premises.extend(m.strip() for m in matches if len(m.strip()) > 5)
        return list(dict.fromkeys(premises))[:5]

    def _extract_conclusions(self, text: str) -> List[str]:
        """Extrai conclusoes do texto."""
        conclusions = []
        indicators = [
            r"(?:therefore|thus|hence|so|consequently|it follows that|we can conclude)\s+(.+?)(?:\.|$)",
            r"(.+?)(?:\s*(?:should|must|ought to)\s+.+?)(?:\.|$)",
        ]
        for indicator in indicators:
            matches = re.findall(indicator, text, re.IGNORECASE)
            conclusions.extend(m.strip() for m in matches if len(m.strip()) > 5)
        return list(dict.fromkeys(conclusions))[:3]

    def _detect_hidden_assumptions(self, text: str) -> List[str]:
        """Detecta pressupostos ocultos."""
        assumptions = []

        if re.search(r"should|must|ought to", text, re.IGNORECASE):
            assumptions.append("Assumes the recommended action is feasible")
        if re.search(r"will|going to|inevitably", text, re.IGNORECASE):
            assumptions.append("Assumes future outcomes can be predicted with certainty")
        if re.search(r"everyone|nobody|always|never", text, re.IGNORECASE):
            assumptions.append("Assumes universal quantification without evidence")
        if re.search(r"better|worse|improve|degrade", text, re.IGNORECASE):
            assumptions.append("Assumes a clear value judgment without defining criteria")
        if re.search(r"because|since|caused by", text, re.IGNORECASE):
            assumptions.append("Assumes causation from correlation or temporal sequence")

        return assumptions

    def _detect_fallacies(self, text: str) -> List[Dict[str, str]]:
        """Detecta falacias logicas no texto."""
        detected = []
        text_lower = text.lower()

        for fall_id, fall_data in self.fallacies.items():
            if re.search(fall_data["pattern"], text_lower, re.IGNORECASE):
                if len(detected) < 5:
                    detected.append({
                        "id": fall_id,
                        "name": fall_data["name"],
                        "description": fall_data["description"]
                    })
        return detected

    def _detect_biases(self, text: str) -> List[str]:
        """Detecta vieses cognitivos."""
        found = []
        text_lower = text.lower()

        bias_indicators = {
            "confirmation_bias": [
                r"(?:as I|we already|I've always|we know)",
                r"(?:proves|confirms|validates) (?:my|our|the)",
            ],
            "overconfidence": [
                r"(?:obviously|clearly|undoubtedly|without question|absolutely)",
                r"(?:100%|certainly|definitely|no doubt)",
            ],
            "framing": [
                r"(?:(?:only|just) \d+%|loss|risk|threat|danger)",
            ],
            "anchoring": [
                r"(?:compared to|relative to|benchmark)",
            ],
        }

        for bias, patterns in bias_indicators.items():
            for pat in patterns:
                if re.search(pat, text_lower):
                    if bias not in found:
                        found.append(bias)
                    break
        return found

    def _evaluate_strength(self, analysis: ArgumentAnalysis) -> Tuple[str, float]:
        """Avalia a forca do argumento (0-100)."""
        score = 50.0

        if analysis.premises:
            score += min(20, len(analysis.premises) * 7)
        if analysis.conclusions:
            score += 10
        if not analysis.fallacies:
            score += 20
        else:
            score -= len(analysis.fallacies) * 8
        if not analysis.hidden_assumptions:
            score += 10
        else:
            score -= len(analysis.hidden_assumptions) * 3

        score = max(0, min(100, score))

        if score >= 75:
            return "strong", score
        elif score >= 50:
            return "moderate", score
        elif score >= 25:
            return "weak", score
        return "very_weak", score

    def _generate_counterarguments(self, analysis: ArgumentAnalysis) -> List[str]:
        """Gera contra-argumentos estruturados."""
        counter = []

        if analysis.fallacies:
            for f in analysis.fallacies:
                counter.append(f"Fallacy detected: {f['name']} — {f['description']}")

        if analysis.hidden_assumptions:
            for a in analysis.hidden_assumptions:
                counter.append(f"Challenge assumption: {a}")

        if not analysis.premises:
            counter.append("No clear premises identified — argument lacks foundation")

        if not analysis.conclusions:
            counter.append("No clear conclusion stated — argument is incomplete")

        return counter if counter else ["No significant weaknesses detected"]

    def compare_arguments(self, arg1: str, arg2: str) -> Dict[str, Any]:
        """Compara dois argumentos."""
        a1 = self.analyze(arg1)
        a2 = self.analyze(arg2)

        winner = "arg1" if a1.score > a2.score else "arg2" if a2.score > a1.score else "tie"

        return {
            "arg1": {"strength": a1.strength, "score": a1.score, "fallacies": len(a1.fallacies)},
            "arg2": {"strength": a2.strength, "score": a2.score, "fallacies": len(a2.fallacies)},
            "winner": winner,
            "gap": abs(a1.score - a2.score),
        }

    def debate_judge(self, statements: List[str]) -> Dict[str, Any]:
        """Avalia multiplos argumentos como juiz de debate."""
        analyses = [self.analyze(s) for s in statements]
        ranked = sorted(
            enumerate(analyses),
            key=lambda x: x[1].score,
            reverse=True
        )

        return {
            "ranking": [
                {"position": i + 1, "speaker": f"Speaker {idx + 1}", "score": a.score, "strength": a.strength}
                for i, (idx, a) in enumerate(ranked)
            ],
            "top_fallacies": list(set(
                f["name"]
                for a in analyses
                for f in a.fallacies
            )),
            "overall_quality": sum(a.score for a in analyses) / len(analyses),
        }


if __name__ == "__main__":
    engine = CriticalEngine()

    test_arg = ("If we invest heavily in artificial intelligence, "
                "we will inevitably lose millions of jobs. "
                "Therefore, we should not invest in AI at all. "
                "Everyone knows this is obvious.")

    result = engine.analyze(test_arg)
    print(f"Text: {test_arg}")
    print(f"Strength: {result.strength} ({result.score:.0f}/100)")
    print(f"Fallacies: {[f['name'] for f in result.fallacies]}")
    print(f"Assumptions: {result.hidden_assumptions}")
    print(f"Counter: {result.counterarguments}")
    print(f"Time: {result.time_ms:.1f}ms")
