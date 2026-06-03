"""
TDD tests for content-engine-dna skill (structural validation).
"""
from pathlib import Path
import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent / "content-engine" / "skills" / "content-engine-dna"
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


class TestContentEngineDnaSkill:
    """Structural validation of content-engine-dna skill."""

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

    def test_documents_6_step_pipeline(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert "Step 1" in content or "Step 1 --" in content
        assert "Step 6" in content or "Step 6 --" in content

    def test_linting_rules_table_present(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert "provenance-exists" in content
        assert "orphaned-compiled" in content

    def test_references_directory_has_extraction_doc(self):
        ref = SKILL_DIR / "references" / "brand-dna-extraction.md"
        assert ref.exists(), f"brand-dna-extraction.md not found at {ref}"
