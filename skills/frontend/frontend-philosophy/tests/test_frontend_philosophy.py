"""
TDD: frontend-philosophy — 5 Pillars of Intentional UI
Validates SKILL.md structure and pillar enumeration.
"""
import os
import pytest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")


def read_skill():
    with open(SKILL_MD, "r", encoding="utf-8") as f:
        return f.read()


class TestFrontendPhilosophyStructure:
    """CT-1: SKILL.md structure validation."""

    def test_skill_md_exists(self):
        assert os.path.isfile(SKILL_MD), "SKILL.md must exist"

    def test_has_frontmatter(self):
        content = read_skill()
        assert content.startswith("---"), "SKILL.md must have YAML frontmatter"
        assert "name:" in content, "Frontmatter must include 'name'"
        assert "frontend-philosophy" in content, "Must identify skill name"

    def test_has_reference_section(self):
        content = read_skill()
        assert "reference" in content.lower(), "Must reference detail files"

    def test_mentions_five_pillars(self):
        content = read_skill()
        assert "5 Pillars" in content or "5 pilares" in content.lower() or \
               "the-5-pillars" in content, "Must reference the 5 pillars"


class TestFrontendPhilosophyReferences:
    """CT-2: Reference files integrity."""

    def test_adherence_checklist_exists(self):
        ref_dir = os.path.join(SKILL_DIR, "reference")
        if os.path.isdir(ref_dir):
            checklist = os.path.join(ref_dir, "adherence-checklist.md")
            assert os.path.isfile(checklist), "adherence-checklist.md must exist"

    def test_five_pillars_doc_exists(self):
        ref_dir = os.path.join(SKILL_DIR, "reference")
        if os.path.isdir(ref_dir):
            pillars = os.path.join(ref_dir, "the-5-pillars.md")
            assert os.path.isfile(pillars), "the-5-pillars.md must exist"


class TestFrontendPhilosophyContent:
    """CT-3: Content validation."""

    def test_skill_not_empty(self):
        content = read_skill()
        assert len(content) > 100, "SKILL.md must have content"

    def test_allowed_tools_specified(self):
        content = read_skill()
        assert "allowed-tools" in content.lower(), "Must specify allowed tools"


class TestFrontendPhilosophyAvailable:
    """CT-4: Availability."""

    def test_skill_directory_complete(self):
        assert os.path.isdir(SKILL_DIR), "Skill directory must exist"

    def test_no_empty_files(self):
        for root, dirs, files in os.walk(SKILL_DIR):
            for f in files:
                if f.endswith(".md"):
                    path = os.path.join(root, f)
                    size = os.path.getsize(path)
                    assert size > 10, f"File {f} must not be empty ({size} bytes)"
