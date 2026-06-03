"""Tests for synthesis-agent skill (no scripts, validate SKILL.md)."""
from pathlib import Path
import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]


class TestSynthesisAgentSkill:
    """CT-1: SKILL.md structure is complete."""

    def test_skill_md_exists(self):
        assert (SKILL_DIR / "SKILL.md").exists()

    def test_skill_md_frontmatter(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "name: synthesis-agent" in content
        assert "ReportAgent" in content or "MiroFish" in content

    def test_react_pattern_documented(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert "ReACT" in content or "Reasoning" in content

    def test_consolidation_workflow_described(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert len(content) > 300
        assert "##" in content  # has headings
