"""
TDD tests for content-engine-loop skill (structural validation).
"""
from pathlib import Path
import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent / "content-engine" / "skills" / "content-engine-loop"
SKILL_MD = SKILL_DIR / "SKILL.md"

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


class TestContentEngineLoopSkill:
    """Structural validation of content-engine-loop skill."""

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

    def test_documents_6_phase_pipeline(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        phases = ["LISTEN", "PLAN", "CREATE", "DISTRIBUTE", "MEASURE", "REFINE"]
        found = sum(1 for p in phases if p in content)
        assert found >= 4, f"Only {found}/6 pipeline phases found"

    def test_campaign_structure_documented(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert "campaign" in content.lower()
        assert "content_pieces" in content or "content pieces" in content.lower()
