"""
TDD tests for weekly-review skill (structural validation).
"""
from pathlib import Path
import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent / "weekly-review"
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


class TestWeeklyReviewSkill:
    """Structural validation of weekly-review skill."""

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

    def test_documents_six_step_workflow(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert "Scan" in content, "Missing scan step"
        assert "Extract completed" in content or "completed items" in content.lower()
        assert "next week" in content.lower(), "Missing next week priorities"

    def test_output_format_has_required_sections(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert "Week at a Glance" in content
        assert "What Got Done" in content
        assert "Next Week's Priorities" in content
