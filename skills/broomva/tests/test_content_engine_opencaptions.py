"""
TDD tests for content-engine-opencaptions skill (structural validation).
"""
from pathlib import Path
import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent / "content-engine" / "extensions" / "opencaptions"
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


class TestContentEngineOpencaptionsSkill:
    """Structural validation of content-engine-opencaptions skill."""

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

    def test_hook_and_slug_defined(self):
        fm = _read_frontmatter(SKILL_MD)
        assert fm.get("hook") == "post-production"
        assert fm.get("slug") == "opencaptions"

    def test_documents_6_step_pipeline(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert "Transcribe" in content
        assert "Diarize" in content
        assert "Intent" in content or "Extract Intent" in content
        assert "Validate" in content or "validation" in content.lower()

    def test_validation_pillars_documented(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert "Attribution" in content
        assert "Synchronization" in content or "SYN_001" in content
        assert "Intonation" in content or "INT_001" in content
