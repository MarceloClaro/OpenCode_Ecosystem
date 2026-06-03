"""Tests for plan-generator skill (no scripts, validate SKILL.md)."""
from pathlib import Path
import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]


class TestPlanGeneratorSkill:
    """CT-1: SKILL.md structure is complete."""

    def test_skill_md_exists(self):
        assert (SKILL_DIR / "SKILL.md").exists()

    def test_skill_md_frontmatter(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "name: plan-generator" in content
        assert "simulation_config_generator" in content or "4 etapas" in content

    def test_skill_md_has_required_sections(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert "##" in content  # has headings
        assert len(content) > 300

    def test_related_skills_referenced(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert "architecture-designer" in content or "spec-miner" in content
