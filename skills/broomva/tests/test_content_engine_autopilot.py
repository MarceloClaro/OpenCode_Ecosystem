"""
TDD tests for content-engine-autopilot skill (structural validation).
"""
from pathlib import Path
import pytest

SKILL_DIR = Path(__file__).resolve().parent.parent / "content-engine" / "skills" / "content-engine-autopilot"
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


class TestContentEngineAutopilotSkill:
    """Structural validation of content-engine-autopilot skill."""

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

    def test_documents_supported_tools(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        tools = ["Higgsfield", "Weavy", "Artlist"]
        found = sum(1 for t in tools if t in content)
        assert found >= 2, f"Only {found}/3 key tools found"

    def test_tool_adapter_interface_documented(self):
        content = SKILL_MD.read_text(encoding="utf-8")
        assert "Tool Adapter" in content or "tool adapter" in content.lower()
        assert "login_url" in content or "prompt_selector" in content
