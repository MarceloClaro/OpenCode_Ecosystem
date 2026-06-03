"""Tests for oasis-profile-gen skill."""
import sys
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import pytest


class TestProfileGenerator:
    """CT-1: Heuristic profile generation."""

    def test_heuristic_profile_required_fields(self):
        from generate_profiles import generate_heuristic_profile, validate_profile
        entity = {
            "name": "Test Person", "summary": "A test person",
            "attributes": {}, "entity_type": "Person",
        }
        profile = generate_heuristic_profile(entity)
        assert "name" in profile
        assert "bio" in profile
        assert "persona" in profile
        assert "mbti" in profile
        assert "interests" in profile

    def test_validate_profile_valid(self):
        from generate_profiles import validate_profile
        profile = {
            "name": "Alice", "bio": "Bio", "persona": "Persona",
            "interests": ["tech"], "mbti": "INTJ",
            "topics": ["AI"], "speaking_style": "formal",
        }
        result = validate_profile(profile)
        assert result["valid"] is True
        assert result["errors"] == []

    def test_validate_profile_missing_field(self):
        from generate_profiles import validate_profile
        profile = {"name": "Bob"}
        result = validate_profile(profile)
        assert result["valid"] is False
        assert len(result["errors"]) > 0

    def test_simulation_config_generation(self):
        from generate_profiles import generate_heuristic_profile, generate_simulation_config
        profiles = [
            generate_heuristic_profile({
                "name": f"Agent{i}", "summary": "", "attributes": {},
                "entity_type": "Person",
            })
            for i in range(3)
        ]
        config = generate_simulation_config(profiles, "test requirement")
        assert config["agent_configs"] is not None
        assert len(config["agent_configs"]) == 3
        assert "time_config" in config
