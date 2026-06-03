"""Tests for machine-states skill (no scripts, validate SKILL.md)."""
from pathlib import Path
import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]


class TestMachineStatesSkill:
    """CT-1: SKILL.md structure is complete."""

    def test_skill_md_exists(self):
        assert (SKILL_DIR / "SKILL.md").exists()

    def test_skill_md_frontmatter(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "name: machine-states" in content
        assert "SimulationStatus" in content or "state machine" in content

    def test_references_exist(self):
        refs = SKILL_DIR / "references"
        assert refs.is_dir()
        ref_files = list(refs.glob("*.md"))
        assert len(ref_files) >= 1

    def test_state_diagram_referenced(self):
        ref_diagram = SKILL_DIR / "references" / "state-diagram.md"
        assert ref_diagram.exists()
        content = ref_diagram.read_text(encoding="utf-8")
        assert len(content) > 50
