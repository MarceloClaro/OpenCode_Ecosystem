"""
TDD tests for handoff skill (structural validation).
"""
from pathlib import Path
import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent / "handoff"
SKILL_MD = SKILL_DIR / "SKILL.md"
TEMPLATE_MD = SKILL_DIR / "references" / "handoff-template.md"

def _read_frontmatter(path):
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    fm = {}
    for line in parts[1].strip().split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip().strip('"').strip("'")
    return fm


class TestHandoffSkill:
    """Structural validation of handoff skill."""

    def test_skill_md_exists(self):
        assert SKILL_MD.exists(), f"SKILL.md not found at {SKILL_MD}"

    def test_frontmatter_present(self):
        fm = _read_frontmatter(SKILL_MD)
        assert fm is not None, "SKILL.md missing YAML frontmatter"

    def test_frontmatter_required_fields(self):
        fm = _read_frontmatter(SKILL_MD)
        required = ["name", "category", "version", "kind"]
        for field in required:
            assert field in fm, f"Missing frontmatter field: {field}"

    def test_category_is_broomva(self):
        fm = _read_frontmatter(SKILL_MD)
        assert fm.get("category") == "broomva"

    def test_handoff_template_exists(self):
        assert TEMPLATE_MD.exists(), f"handoff-template.md not found at {TEMPLATE_MD}"

    def test_canonical_shape_documented(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert "TL;DR" in content
        assert "State of the world" in content or "P15 snapshot" in content
        assert "First action" in content
