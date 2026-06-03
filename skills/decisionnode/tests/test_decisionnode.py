"""Tests for decisionnode skill (no scripts, validate SKILL.md)."""
from pathlib import Path
import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]


class TestDecisionNodeSkill:
    """CT-1: SKILL.md structure validation."""

    def test_skill_md_exists(self):
        assert (SKILL_DIR / "SKILL.md").exists()

    def test_skill_md_frontmatter(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "name: decisionnode" in content
        assert "description:" in content

    def test_references_exist(self):
        refs = SKILL_DIR / "references"
        assert refs.is_dir()
        ref_files = list(refs.glob("*.md"))
        assert len(ref_files) >= 3

    def test_cli_and_mcp_documented(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert "CLI" in content or "cli" in content
        assert "MCP" in content or "mcp" in content
