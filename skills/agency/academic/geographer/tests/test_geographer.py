"""TDD tests for GeographerEngine — geography validation, climate, rivers, settlement."""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))
from geographer_engine import GeographerEngine, GeoReport


class TestGeographer:
    def setup_method(self):
        self.engine = GeographerEngine()

    # ── Geography coherence ───────────────────────────────────────────
    def test_geography_coherence_returns_report(self):
        result = self.engine.validate_geography(
            "The region 'TestValley' at latitude 45.0 has coastal terrain and a river"
        )
        assert isinstance(result, GeoReport)
        assert result.region_name == "TestValley"

    def test_geography_coherence_extracts_latitude(self):
        result = self.engine.validate_geography(
            "Region at latitude -5.2 with tropical coastal terrain"
        )
        assert result.latitude_zone != ""
        assert result.climate_classification != ""

    def test_geography_coherence_no_latitude(self):
        result = self.engine.validate_geography("A region with coastal terrain")
        assert isinstance(result, GeoReport)
        assert isinstance(result.score, float)

    # ── River validation ──────────────────────────────────────────────
    def test_river_doesnt_split(self):
        issues = self.engine.validate_rivers([
            {"name": "Test River", "splits_into": 3, "source_elevation": 1000, "mouth_elevation": 0}
        ])
        assert len(issues) > 0
        assert any("bifurcation" in i.lower() or "split" in i.lower() for i in issues)

    def test_river_flows_downhill(self):
        issues = self.engine.validate_rivers([
            {"name": "Uphill River", "source_elevation": 100, "mouth_elevation": 200}
        ])
        assert len(issues) > 0
        assert any("exceed" in i.lower() or "above" in i.lower() for i in issues)

    def test_river_valid_passes(self):
        issues = self.engine.validate_rivers([
            {"name": "Good River", "source_elevation": 3000, "mouth_elevation": 0, "tributaries": [
                {"name": "Side Creek", "source_elevation": 1500, "mouth_elevation": 500}
            ]}
        ])
        assert len(issues) == 0

    def test_tributary_must_flow_downhill(self):
        issues = self.engine.validate_rivers([
            {"name": "Main", "source_elevation": 2000, "mouth_elevation": 0, "tributaries": [
                {"name": "Bad Creek", "source_elevation": 100, "mouth_elevation": 500}
            ]}
        ])
        assert len(issues) > 0

    def test_duplicate_river_names(self):
        issues = self.engine.validate_rivers([
            {"name": "Same", "source_elevation": 100, "mouth_elevation": 0},
            {"name": "Same", "source_elevation": 200, "mouth_elevation": 0},
        ])
        assert len(issues) > 0
        assert any("duplicate" in i.lower() for i in issues)

    # ── Climate rules ─────────────────────────────────────────────────
    def test_climate_latitude_rule_tropical(self):
        result = self.engine.check_climate(5.0, "coastal")
        assert result["valid"] is True
        assert "tropical" in result["zone"]

    def test_climate_latitude_rule_polar(self):
        result = self.engine.check_climate(80.0, "coastal")
        assert result["valid"] is True
        assert "polar" in result["zone"]

    def test_climate_latitude_rule_temperate(self):
        result = self.engine.check_climate(45.0, "steppe")
        assert result["valid"] is True
        assert "temperate" in result["zone"]

    def test_climate_invalid_latitude(self):
        result = self.engine.check_climate(100.0, "desert")
        assert result["valid"] is False

    def test_climate_includes_biome(self):
        result = self.engine.check_climate(5.0, "desert")
        assert "terrestrial_biome" in result

    # ── Settlement analysis ───────────────────────────────────────────
    def test_settlement_requires_water(self):
        result = self.engine.analyze_settlement({
            "name": "Dry Town",
            "terrain": "arid plain",
            "description": "far from any water source"
        })
        assert result["viable"] is False
        assert "freshwater" in result["requirements_unmet"]

    def test_settlement_viable_with_water_and_land(self):
        result = self.engine.analyze_settlement({
            "name": "River Town",
            "terrain": "fertile river valley",
            "description": "near a spring with fertile soil and trade route"
        })
        assert result["viable"] is True
        assert "freshwater" in result["requirements_met"]

    def test_settlement_score_range(self):
        result = self.engine.analyze_settlement({
            "name": "X", "terrain": "mountain pass", "description": "rocky cliff"
        })
        assert 0.0 <= result["score"] <= 1.0

    # ── Engine property ───────────────────────────────────────────────
    def test_available_property(self):
        assert self.engine.available is True

    def test_score_in_range(self):
        report = self.engine.validate_geography("A region")
        assert 0.0 <= report.score <= 1.0

    # ── Warning detection ─────────────────────────────────────────────
    def test_desert_river_warning(self):
        report = self.engine.validate_geography(
            "A desert with a perennial river but no glaciers or snowmelt"
        )
        assert len(report.warnings) > 0
