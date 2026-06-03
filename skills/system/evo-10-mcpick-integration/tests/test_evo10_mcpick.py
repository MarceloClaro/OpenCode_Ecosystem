"""TDD tests for evo-10-mcpick-integration system skill."""

import pathlib

SKILL_DIR = pathlib.Path(__file__).parent.parent
SKILL_MD = SKILL_DIR / "SKILL.md"


def test_skill_md_exists():
    assert SKILL_MD.exists(), f"SKILL.md not found at {SKILL_MD}"


def test_has_category():
    content = SKILL_MD.read_text(encoding="utf-8")
    assert "category:" in content, "SKILL.md must declare a category in frontmatter"


def test_has_version():
    content = SKILL_MD.read_text(encoding="utf-8")
    assert "version:" in content, "SKILL.md must declare a version in frontmatter"
