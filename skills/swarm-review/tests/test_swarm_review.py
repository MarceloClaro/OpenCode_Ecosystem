"""Tests for swarm-review skill (no scripts, validate SKILL.md)."""
from pathlib import Path
import pytest

SKILL_DIR = Path(__file__).resolve().parents[1]


class TestSwarmReviewSkill:
    """CT-1: SKILL.md structure is complete."""

    def test_skill_md_exists(self):
        assert (SKILL_DIR / "SKILL.md").exists()

    def test_skill_md_frontmatter(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert content.startswith("---")
        assert "name: swarm-review" in content
        assert "OASIS" in content or "MiroFish" in content

    def test_references_contain_personas(self):
        refs = SKILL_DIR / "references"
        assert refs.is_dir()
        ref_files = list(refs.glob("*.md"))
        assert len(ref_files) >= 2
        for f in ref_files:
            content = f.read_text(encoding="utf-8")
            assert len(content) > 30

    def test_multi_agent_perspectives_documented(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert "segurança" in content or "security" in content
        assert "performance" in content
