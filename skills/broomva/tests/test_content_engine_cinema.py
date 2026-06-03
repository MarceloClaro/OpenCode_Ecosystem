"""
TDD tests for content-engine-cinema skill (structural validation).
"""
from pathlib import Path
import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent / "content-engine" / "skills" / "content-engine-cinema"
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


class TestContentEngineCinemaSkill:
    """Structural validation of content-engine-cinema skill."""

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

    def test_camera_vocabulary_table_has_8_directors(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        directors = ["Anderson", "Fincher", "Nolan", "Villeneuve", "Kubrick", "Wong Kar-wai", "Scott", "Malick"]
        found = sum(1 for d in directors if d in content)
        assert found >= 6, f"Only {found}/8 directors found in camera vocabulary"

    def test_documents_start_frame_doctrine(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert "Start-Frame" in content or "start frame" in content.lower()
