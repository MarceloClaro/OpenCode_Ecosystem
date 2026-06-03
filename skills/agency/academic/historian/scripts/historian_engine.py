"""Historian reasoning engine for OpenCode Ecosystem.
Anachronism detection, period authenticity assessment, and historical
claim evaluation.

Uses a knowledge base of historical periods, technological timelines,
and material culture references. Standard library only — rule-based
temporal reasoning with explicit confidence levels.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ── Historical periods database ───────────────────────────────────────
_HISTORICAL_PERIODS: dict[str, dict[str, Any]] = {
    "pre_columbian_americas": {
        "name": "Pre-Columbian Americas",
        "start": -13000,
        "end": 1492,
        "region": "Americas",
        "available_crops": ["maize", "beans", "squash", "potato", "quinoa", "tomato", "chili", "cacao", "amaranth", "manioc"],
        "available_animals": ["llama", "alpaca", "guinea_pig", "turkey", "dog"],
        "available_tech": ["stone_tools", "metallurgy_gold_silver_copper", "wheel_as_toy", "terrace_farming", "chinampas"],
        "unavailable": ["iron_smelting", "horse", "cattle", "pig", "sheep", "wheat", "rice", "barley", "firearms", "steel"],
    },
    "medieval_europe": {
        "name": "Medieval Europe",
        "start": 476,
        "end": 1492,
        "region": "Europe",
        "available_crops": ["wheat", "barley", "rye", "oats", "grape", "olive", "cabbage", "onion"],
        "available_animals": ["horse", "cattle", "pig", "sheep", "goat", "chicken", "dog", "cat"],
        "available_tech": ["iron_plow", "watermill", "windmill", "stirrup", "heavy_cavalry", "gothic_architecture", "crossbow"],
            "unavailable": ["potato", "tomato", "maize", "tobacco", "coffee", "tea",
                          "sugar_cane_europe", "firearms_before_1300", "printing_press_before_1440",
                          "mechanical_clock_before_1300", "compass_europe_before_1180",
                          "plastic", "electricity", "automobile", "radio", "antibiotics"],
        },
    "ancient_rome": {
        "name": "Ancient Rome",
        "start": -753,
        "end": 476,
        "region": "Mediterranean",
        "available_crops": ["wheat", "barley", "olive", "grape", "fig", "date", "cabbage"],
        "available_animals": ["horse", "cattle", "pig", "sheep", "goat", "chicken"],
        "available_tech": ["aqueduct", "concrete", "road_network", "legion_organization", "arch", "dome"],
        "unavailable": ["potato", "tomato", "maize", "coffee", "tea", "gunpowder", "stirrup_early_rome", "heavy_plow"],
    },
    "ancient_china": {
        "name": "Ancient China (Han Dynasty)",
        "start": -206,
        "end": 220,
        "region": "East Asia",
        "available_crops": ["rice", "wheat", "millet", "soybean", "tea", "mulberry"],
        "available_animals": ["water_buffalo", "pig", "chicken", "dog", "silkworm"],
        "available_tech": ["paper", "compass_prototype", "seismograph", "iron_casting", "silk_weaving", "wheelbarrow"],
        "unavailable": ["potato", "maize", "coffee", "cotton_widespread", "firearms"],
    },
    "industrial_revolution": {
        "name": "Industrial Revolution",
        "start": 1760,
        "end": 1840,
        "region": "Western Europe / North America",
        "available_crops": ["wheat", "potato", "maize", "cotton", "tea", "coffee", "sugar"],
        "available_animals": ["horse", "cattle", "pig", "sheep", "goat", "chicken"],
        "available_tech": ["steam_engine", "spinning_jenny", "power_loom", "railway", "telegraph", "coal_mining"],
        "unavailable": ["automobile", "airplane", "radio", "computer", "nuclear_power", "plastic", "antibiotics"],
    },
    "ancient_egypt": {
        "name": "Ancient Egypt (Old Kingdom)",
        "start": -2686,
        "end": -2181,
        "region": "Nile Valley",
        "available_crops": ["wheat", "barley", "flax", "papyrus", "fig", "date"],
        "available_animals": ["cattle", "donkey", "sheep", "goat", "cat", "dog", "duck"],
        "available_tech": ["pyramid_construction", "hieroglyphs", "mummification", "calendar", "nilometer"],
        "unavailable": ["horse", "camel_widespread", "iron_smelting", "coinage", "chariot", "glass_blowing"],
    },
}

_ANACHRONISM_RULES: list[dict[str, Any]] = [
    {"item": "potato", "not_before": 1492, "origin": "Americas", "message": "Potatoes are native to the Americas; unavailable in Old World before 1492"},
    {"item": "tomato", "not_before": 1492, "origin": "Americas", "message": "Tomatoes are native to the Americas; unavailable in Old World before 1492"},
    {"item": "maize", "not_before": 1492, "origin": "Americas", "message": "Maize (corn) is native to the Americas; unavailable in Old World before 1492"},
    {"item": "tobacco", "not_before": 1492, "origin": "Americas", "message": "Tobacco is native to the Americas; unavailable in Old World before 1492"},
    {"item": "cacao", "not_before": 1492, "origin": "Americas", "message": "Cacao/chocolate is native to the Americas; unavailable in Old World before 1492"},
    {"item": "horse", "not_before": -3000, "origin": "Eurasia", "message": "Horses were not present in Americas before 1492; in Old World, domesticated ~3500 BCE"},
    {"item": "gunpowder", "not_before": 800, "origin": "China", "message": "Gunpowder invented in China ~9th century CE; unavailable before this date"},
    {"item": "printing_press", "not_before": 1440, "origin": "Europe", "message": "Movable-type printing press invented by Gutenberg ~1440 CE"},
    {"item": "steam_engine", "not_before": 1700, "origin": "Europe", "message": "Practical steam engines developed from ~1700 (Savery/Newcomen/Watt)"},
    {"item": "coffee", "not_before": 800, "origin": "Ethiopia/Arabia", "message": "Coffee cultivation and consumption spread from ~9th century; widespread only after 1500"},
    {"item": "tea", "not_before": -2700, "origin": "China", "message": "Tea originated in China ~2700 BCE; reached Europe only after 1600 CE"},
    {"item": "firearms", "not_before": 1250, "origin": "China", "message": "Firearms emerged in China ~13th century, spread to Europe by 14th century"},
    {"item": "sugar", "not_before": -500, "origin": "India", "message": "Crystallized sugar developed in India ~500 BCE; European beet sugar only from 1801"},
    {"item": "aluminum", "not_before": 1825, "origin": "Europe", "message": "Aluminum metal isolated in 1825; not available in any pre-industrial period"},
    {"item": "plastic", "not_before": 1862, "origin": "Europe", "message": "First synthetic plastic (Parkesine) introduced 1862"},
    {"item": "antibiotics", "not_before": 1928, "origin": "Europe", "message": "Penicillin discovered 1928; antibiotic era begins ~1940s"},
    {"item": "radio", "not_before": 1895, "origin": "Europe", "message": "Radio communication developed by Marconi ~1895"},
    {"item": "automobile", "not_before": 1885, "origin": "Europe", "message": "First practical automobiles ~1885 (Benz/Daimler)"},
    {"item": "electric", "not_before": 1880, "origin": "Global", "message": "Widespread electric lighting and power from ~1880s"},
    {"item": "telephone", "not_before": 1876, "origin": "North America", "message": "Telephone patented by Bell in 1876"},
]


@dataclass
class Anachronism:
    item: str
    period: str
    message: str
    confidence: float
    severity: str


@dataclass
class PeriodReport:
    period_name: str
    region: str
    date_range: str
    available_items: dict[str, list[str]]
    known_anachronisms: list[str]


class HistorianEngine:
    """Rule-based historical reasoning engine for anachronism detection."""

    def __init__(self) -> None:
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def detect_anachronisms(self, text: str, period: str, region: str) -> list[dict[str, Any]]:
        """Detect historical anachronisms in a textual description.

        Cross-references the text against the anachronism rules database
        and the historical period definitions.
        """
        findings: list[dict[str, Any]] = []
        text_lower = text.lower()
        period_data = self._resolve_period(period)

        for rule in _ANACHRONISM_RULES:
            item = rule["item"]
            pattern = re.compile(rf'\b{re.escape(item)}', re.I)
            if not pattern.search(text_lower):
                continue

            if period_data and "unavailable" in period_data:
                item_matches_unavailable = any(
                    item.startswith(u) or u.startswith(item) or item in u or u in item
                    for u in period_data["unavailable"]
                )
                if item_matches_unavailable:
                    findings.append({
                        "item": item,
                        "period": period_data["name"],
                        "message": rule["message"],
                        "confidence": 0.95,
                        "severity": "high",
                    })
                elif item in period_data.get("available_tech", []) or item in period_data.get("available_crops", []):
                    findings.append({
                        "item": item,
                        "period": period_data["name"],
                        "message": f"{item.capitalize()} was available in {period_data['name']}",
                        "confidence": 0.90,
                        "severity": "none",
                    })
                else:
                    findings.append({
                        "item": item,
                        "period": period_data["name"],
                        "message": f"Verify availability of {item} in {period_data['name']}",
                        "confidence": 0.50,
                        "severity": "medium",
                    })
            else:
                findings.append({
                    "item": item,
                    "period": period,
                    "message": rule["message"],
                    "confidence": 0.70,
                    "severity": "medium",
                })

        return findings

    def period_authenticity(self, period: str, region: str) -> dict[str, Any]:
        """Generate an authenticity report for a given historical period."""
        period_data = self._resolve_period(period)

        if not period_data:
            return {
                "period": period,
                "region": region,
                "confidence_level": "low",
                "warning": f"Period '{period}' not found in database. Using generic rules only.",
                "available": [],
                "anachronism_risks": [r["item"] for r in _ANACHRONISM_RULES],
            }

        return {
            "period": period_data["name"],
            "region": period_data["region"],
            "date_range": f"{period_data['start']} to {period_data['end']}",
            "confidence_level": "high",
            "available_crops": period_data.get("available_crops", []),
            "available_animals": period_data.get("available_animals", []),
            "available_tech": period_data.get("available_tech", []),
            "known_unavailable": period_data.get("unavailable", []),
            "anachronism_risks": [
                r["item"] for r in _ANACHRONISM_RULES
                if r["not_before"] > period_data["start"]
            ],
        }

    def evaluate_claim(self, claim: str, period: str) -> dict[str, Any]:
        """Evaluate a specific historical claim for plausibility."""
        period_data = self._resolve_period(period)
        claim_lower = claim.lower()
        evidence: list[str] = []
        counter_evidence: list[str] = []
        confidence = 0.5

        for rule in _ANACHRONISM_RULES:
            item = rule["item"]
            pat = re.compile(rf'\b{re.escape(item)}', re.I)
            if pat.search(claim_lower):
                item = rule["item"]
                is_unavailable = period_data and any(
                    item.startswith(u) or u.startswith(item) or item in u or u in item
                    for u in period_data.get("unavailable", [])
                )
                if is_unavailable:
                    counter_evidence.append(rule["message"])
                    confidence -= 0.3
                elif period_data and (
                    rule["item"] in period_data.get("available_tech", [])
                    or rule["item"] in period_data.get("available_crops", [])
                ):
                    evidence.append(f"{rule['item'].capitalize()} was available in this period")
                    confidence += 0.2

        if period_data:
            for crop in period_data.get("available_crops", []):
                if crop in claim_lower:
                    evidence.append(f"{crop.capitalize()} attested in {period_data['name']}")
                    confidence += 0.05

        confidence = max(0.0, min(1.0, confidence))

        if confidence >= 0.8:
            verdict = "likely accurate"
        elif confidence >= 0.5:
            verdict = "plausible but requires verification"
        elif confidence >= 0.3:
            verdict = "questionable — significant anachronisms detected"
        else:
            verdict = "highly improbable — multiple anachronisms"

        return {
            "claim": claim,
            "period": period_data["name"] if period_data else period,
            "verdict": verdict,
            "confidence": round(confidence, 3),
            "supporting_evidence": evidence,
            "counter_evidence": counter_evidence,
        }

    # ── Helpers ───────────────────────────────────────────────────────
    @staticmethod
    def _resolve_period(period_name: str) -> dict[str, Any] | None:
        key = period_name.lower().replace(" ", "_").replace("-", "_")
        if key in _HISTORICAL_PERIODS:
            return _HISTORICAL_PERIODS[key]
        for name, data in _HISTORICAL_PERIODS.items():
            if key in name or name in key:
                return data
        return None


# ── CLI demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = HistorianEngine()
    print(f"HistorianEngine available: {engine.available}")

    print("\nDetecting anachronisms (potatoes in medieval Europe):")
    for f in engine.detect_anachronisms("The knight ate potatoes and tomatoes with his tea", "medieval_europe", "Europe"):
        print(f"  {f['item']}: {f['severity']} ({f['confidence']})")

    print("\nPeriod authenticity (medieval Europe):")
    report = engine.period_authenticity("medieval_europe", "Europe")
    print(f"  Period: {report['period']}")
    print(f"  Unavailable items: {report.get('known_unavailable', [])[:5]}")
    print(f"  Confidence: {report['confidence_level']}")

    print("\nClaim evaluation:")
    ev = engine.evaluate_claim("Vikings grew potatoes before Columbus", "medieval_europe")
    print(f"  Verdict: {ev['verdict']}")
    print(f"  Confidence: {ev['confidence']}")
    print(f"  Counter: {ev['counter_evidence']}")
