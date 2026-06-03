"""Geographer reasoning engine for OpenCode Ecosystem.
Geographic validation, climate inference, river network analysis,
and settlement viability assessment.

Based on physical geography principles: Koppen climate classification
simplified, Strahler stream ordering concepts, Christaller's central
place theory, and basic geomorphology rules.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any


# ── Climate zones by latitude band ────────────────────────────────────
_CLIMATE_BY_LAT: list[dict[str, Any]] = [
    {"range": (-90, -66.5), "zone": "polar", "temps": "extreme cold", "precip": "low"},
    {"range": (-66.5, -55), "zone": "subpolar", "temps": "cold, short summer", "precip": "low-moderate"},
    {"range": (-55, -35), "zone": "temperate", "temps": "cool, seasonal", "precip": "moderate"},
    {"range": (-35, -23.5), "zone": "subtropical", "temps": "warm, mild winter", "precip": "moderate-high"},
    {"range": (-23.5, 0), "zone": "tropical", "temps": "hot, humid", "precip": "high"},
    {"range": (0, 23.5), "zone": "tropical", "temps": "hot, humid", "precip": "high"},
    {"range": (23.5, 35), "zone": "subtropical", "temps": "warm, mild winter", "precip": "moderate-high"},
    {"range": (35, 55), "zone": "temperate", "temps": "seasonal", "precip": "moderate"},
    {"range": (55, 66.5), "zone": "subpolar", "temps": "cold, short summer", "precip": "low-moderate"},
    {"range": (66.5, 90), "zone": "polar", "temps": "extreme cold", "precip": "low"},
]

# Orographic/terrain modifiers
_TERRAIN_MODIFIERS: dict[str, dict[str, Any]] = {
    "coastal": {"temp_mod": "moderated", "precip_mod": "increased", "humidity": "high"},
    "mountain": {"temp_mod": "colder with altitude", "precip_mod": "orographic enhancement", "humidity": "variable"},
    "rain_shadow": {"temp_mod": "warmer", "precip_mod": "severely reduced", "humidity": "low", "also": "leeward side of mountains"},
    "desert": {"temp_mod": "extreme diurnal range", "precip_mod": "very low", "humidity": "very low"},
    "steppe": {"temp_mod": "continental extremes", "precip_mod": "low", "humidity": "low"},
    "continental_interior": {"temp_mod": "large annual range", "precip_mod": "reduced", "humidity": "moderate-low"},
    "island": {"temp_mod": "maritime moderation", "precip_mod": "moderate-high", "humidity": "high"},
    "monsoon_region": {"temp_mod": "seasonal", "precip_mod": "intense seasonal", "humidity": "seasonal"},
}

_SETTLEMENT_REQUIREMENTS: list[dict[str, Any]] = [
    {"need": "freshwater", "critical": True, "examples": ["river", "lake", "spring", "aquifer", "well"]},
    {"need": "arable_land", "critical": True, "examples": ["fertile", "soil", "plain", "valley", "delta"]},
    {"need": "defensibility", "critical": False, "examples": ["hill", "elevation", "fortified", "island"]},
    {"need": "trade_route", "critical": False, "examples": ["crossroads", "port", "harbor", "pass", "ford"]},
]

_RIVER_FLOW_RULES: list[dict[str, Any]] = [
    {"rule": "tributaries join, not split", "violation": "River bifurcation (splitting) is rare except in deltas"},
    {"rule": "flow from high to low", "violation": "Rivers cannot flow uphill without mechanical pumping"},
    {"rule": "confluence increases volume", "violation": "Downstream discharge should exceed upstream at confluences"},
    {"rule": "source from precipitation", "violation": "Perennial rivers require consistent water source (glacier, aquifer, rainfall)"},
    {"rule": "drainage basin closed", "violation": "Endorheic basins have no outlet to sea; water leaves by evaporation"},
]


@dataclass
class GeoReport:
    region_name: str = ""
    latitude_zone: str = ""
    climate_classification: str = ""
    terrain_types: dict[str, str] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    score: float = 0.0


class GeographerEngine:
    """Rule-based geographic analysis engine."""

    def __init__(self) -> None:
        self._available = True

    @property
    def available(self) -> bool:
        return self._available

    def validate_geography(self, description: str) -> GeoReport:
        """Generate a geographic coherence report from a description.

        Extracts latitude info, classifies climate, identifies terrain,
        and flags warnings about geographic implausibilities.
        """
        report = GeoReport(region_name=self._extract_name(description))

        lat = self._extract_latitude(description)
        if lat is not None:
            report.latitude_zone = self._latitude_zone(lat)
            report.climate_classification = self._classify_climate(lat)

        report.terrain_types = self._identify_terrain(description)
        report.warnings = self._check_warnings(description, lat, report)
        report.score = self._calculate_score(report)

        return report

    def check_climate(self, lat: float, terrain: str) -> dict[str, Any]:
        """Infer climate characteristics from latitude and terrain."""
        if not -90 <= lat <= 90:
            return {"error": "Latitude must be between -90 and 90", "valid": False}

        zone_info = self._latitude_zone_info(lat)
        modifiers = _TERRAIN_MODIFIERS.get(terrain.lower(), {})
        if not modifiers:
            terrain = self._match_terrain(terrain)
            modifiers = _TERRAIN_MODIFIERS.get(terrain, {})

        return {
            "valid": True,
            "latitude": lat,
            "zone": zone_info["zone"],
            "base_temperature": zone_info["temps"],
            "base_precipitation": zone_info["precip"],
            "terrain_modifiers": modifiers,
            "terrestrial_biome": self._infer_biome(zone_info["zone"], terrain),
        }

    def validate_rivers(self, rivers: list[dict[str, Any]]) -> list[str]:
        """Validate a river network description for physical plausibility."""
        issues: list[str] = []
        names: set[str] = set()

        for i, river in enumerate(rivers):
            name = river.get("name", f"river_{i}")
            if name in names:
                issues.append(f"Duplicate river name: {name}")
            names.add(name)

            source_el = river.get("source_elevation")
            mouth_el = river.get("mouth_elevation")
            if source_el is not None and mouth_el is not None and source_el <= mouth_el:
                issues.append(f"River '{name}': source_elevation ({source_el}) must exceed mouth_elevation ({mouth_el})")

            splits_into = river.get("splits_into", 1)
            if isinstance(splits_into, int) and splits_into > 1:
                issues.append(f"River '{name}': bifurcation (splitting into {splits_into}) is uncommon; specify if deltaic")

            tributaries = river.get("tributaries", [])
            if isinstance(tributaries, list):
                for trib in tributaries:
                    trib_name = trib.get("name", "?")
                    trib_source = trib.get("source_elevation")
                    trib_mouth = trib.get("mouth_elevation")
                    if trib_source is not None and trib_mouth is not None and trib_source <= trib_mouth:
                        issues.append(
                            f"Tributary '{trib_name}' of '{name}': source must be above mouth"
                        )

        return issues

    def analyze_settlement(self, location: dict[str, Any]) -> dict[str, Any]:
        """Analyze settlement viability based on geographic factors."""
        name = location.get("name", "Unnamed")
        met: list[str] = []
        unmet: list[str] = []
        details: dict[str, Any] = {}

        for req in _SETTLEMENT_REQUIREMENTS:
            need = req["need"]
            is_met = False
            for example in req["examples"]:
                desc_text = str(location.get("description", "")).lower()
                terrain_text = str(location.get("terrain", "")).lower()
                if example.lower() in desc_text or example.lower() in terrain_text:
                    is_met = True
                    details[need] = f"found: {example}"
                    break
            if is_met:
                met.append(need)
            else:
                unmet.append(need)
                if req["critical"]:
                    details[need] = "MISSING — settlement viability severely compromised"

        viable = all(n not in unmet for n in ["freshwater", "arable_land"])

        return {
            "settlement": name,
            "viable": viable,
            "requirements_met": met,
            "requirements_unmet": unmet,
            "details": details,
            "score": len(met) / len(_SETTLEMENT_REQUIREMENTS),
            "recommendation": "Settlement pattern appears viable" if viable else "Critical resources missing; review location",
        }

    # ── Internal helpers ──────────────────────────────────────────────
    @staticmethod
    def _extract_name(description: str) -> str:
        m = re.search(r"""(?:region|area|place)\s+(?:called|named|of)\s+["']?([A-Z][A-Za-z\s]+)["']?""", description)
        if m:
            return m.group(1).strip()
        m = re.search(r"""["']([A-Z][A-Za-z\s]+)["']""", description)
        if m:
            return m.group(1)
        cap = re.findall(r'\b([A-Z][a-z]{2,}(?:\s[A-Z][a-z]{2,})*)', description)
        if cap:
            return cap[0]
        return description[:50].strip()

    @staticmethod
    def _extract_latitude(description: str) -> float | None:
        m = re.search(r'lat(?:itude)?\s*[:=]?\s*(-?\d+\.?\d*)', description, re.I)
        if m:
            return float(m.group(1))
        m = re.search(r'at\s+(-?\d+\.?\d*)°?\s*[NS]', description, re.I)
        if m:
            val = float(m.group(1))
            if re.search(r'[Ss]', description):
                val = -val
            return val
        return None

    @staticmethod
    def _latitude_zone(lat: float) -> str:
        abs_lat = abs(lat)
        if abs_lat < 23.5:
            return "tropical"
        if abs_lat < 35:
            return "subtropical"
        if abs_lat < 55:
            return "temperate"
        if abs_lat < 66.5:
            return "subpolar"
        return "polar"

    @staticmethod
    def _latitude_zone_info(lat: float) -> dict[str, str]:
        for entry in _CLIMATE_BY_LAT:
            lo, hi = entry["range"]
            if lo <= lat < hi:
                return entry
        return _CLIMATE_BY_LAT[0]

    @staticmethod
    def _classify_climate(lat: float) -> str:
        zone = abs(lat)
        if zone < 10:
            return "Af (tropical rainforest)"
        if zone < 23.5:
            return "Aw/Am (tropical wet/dry or monsoon)"
        if zone < 35:
            return "Cfa/Csa (humid subtropical / Mediterranean)"
        if zone < 55:
            return "Cfb/Dfb (marine west coast / humid continental)"
        if zone < 66.5:
            return "Dfc (subarctic)"
        return "ET/EF (tundra / ice cap)"

    @staticmethod
    def _identify_terrain(description: str) -> dict[str, str]:
        result: dict[str, str] = {}
        text = description.lower()
        for term, data in _TERRAIN_MODIFIERS.items():
            if term.replace("_", " ") in text or term.replace("_", "") in text:
                result[term] = str(data)
        return result

    def _check_warnings(self, description: str, lat: float | None, report: GeoReport) -> list[str]:
        warnings: list[str] = []
        text = description.lower()
        has_glacier = re.search(r'\bglacier', text)
        has_snowmelt = re.search(r'\bsnowmelt', text)
        negated = bool(re.search(r'\bno\s+glacier', text) or re.search(r'\bwithout\s+glacier', text))

        if "desert" in text and "river" in text:
            if not has_glacier and not has_snowmelt:
                warnings.append("Desert river described without glacial/snowmelt source — may be ephemeral (wadi)")
            elif negated:
                warnings.append("Desert river described without glacial/snowmelt source — may be ephemeral (wadi)")
        if "rainforest" in text and lat is not None and abs(lat) > 35:
            warnings.append(f"Rainforest at latitude {abs(lat)}° is atypical; check for orographic or coastal explanation")
        if "mountain" in text and "rain shadow" in text:
            warnings.append("Rain shadow effect correctly noted")

        return warnings

    @staticmethod
    def _match_terrain(terrain_text: str) -> str:
        text = terrain_text.lower().strip()
        for key in _TERRAIN_MODIFIERS:
            if key in text or text in key:
                return key
        return text

    @staticmethod
    def _infer_biome(zone: str, terrain: str) -> str:
        mapping: dict[tuple[str, str], str] = {
            ("tropical", "coastal"): "mangrove / tropical coastal forest",
            ("tropical", "desert"): "hot desert",
            ("tropical", "steppe"): "tropical savanna",
            ("temperate", "coastal"): "temperate rainforest",
            ("temperate", "steppe"): "temperate grassland / prairie",
            ("temperate", "continental_interior"): "temperate broadleaf forest",
            ("subpolar", ""): "taiga / boreal forest",
            ("polar", ""): "tundra",
        }
        return mapping.get((zone, terrain), f"{zone} {terrain}".strip())

    @staticmethod
    def _calculate_score(report: GeoReport) -> float:
        score = 1.0
        if not report.latitude_zone:
            score -= 0.3
        if not report.climate_classification:
            score -= 0.2
        score -= len(report.warnings) * 0.15
        return max(0.0, min(1.0, score))


# ── CLI demo ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    engine = GeographerEngine()
    print(f"GeographerEngine available: {engine.available}")

    desc = "The region called 'Verdantia' at latitude 5.2 has coastal terrain with fertile plains and a major river fed by mountain glaciers"
    report = engine.validate_geography(desc)
    print(f"\nRegion: {report.region_name}")
    print(f"Lat zone: {report.latitude_zone}")
    print(f"Climate: {report.climate_classification}")
    print(f"Terrain: {report.terrain_types}")
    print(f"Warnings: {report.warnings}")
    print(f"Score: {report.score:.2f}")

    print("\nClimate check (lat=45, terrain=coastal):")
    print(engine.check_climate(45, "coastal"))

    print("\nRiver validation:")
    rivers = [
        {"name": "Great River", "source_elevation": 2000, "mouth_elevation": 0, "tributaries": [
            {"name": "Little Creek", "source_elevation": 500, "mouth_elevation": 300}
        ]},
        {"name": "Magic River", "source_elevation": 100, "mouth_elevation": 200},
    ]
    for issue in engine.validate_rivers(rivers):
        print(f"  ISSUE: {issue}")

    print("\nSettlement analysis:")
    loc = {"name": "New Haven", "terrain": "river plain with fertile soil", "description": "hilltop near fresh water spring"}
    print(engine.analyze_settlement(loc))
