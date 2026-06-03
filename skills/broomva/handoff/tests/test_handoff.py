"""
TDD: handoff — Fresh-session handoff document drafting
Validates SKILL.md structure, template rules, and anti-patterns.
"""
import os
import pytest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")


def read_skill():
    with open(SKILL_MD, "r", encoding="utf-8") as f:
        return f.read()


class TestHandoffStructure:
    """CT-1: SKILL.md structure validation."""

    def test_skill_md_exists(self):
        assert os.path.isfile(SKILL_MD), "SKILL.md must exist"

    def test_has_frontmatter(self):
        content = read_skill()
        assert content.startswith("---"), "SKILL.md must have YAML frontmatter"
        assert "name:" in content, "Frontmatter must include 'name'"
        assert "handoff" in content.lower(), "Must identify skill name"

    def test_has_canonical_shape(self):
        content = read_skill()
        assert "TL;DR" in content or "TL.DR" in content.replace(".", "."), \
            "Must include TL;DR section"
        assert "State of the world" in content, \
            "Must include State of the world section"

    def test_has_trigger_keywords(self):
        content = read_skill()
        triggers = ["handoff", "fresh-session", "pickup", "resume tomorrow"]
        found = sum(1 for t in triggers if t in content.lower())
        assert found >= 2, f"Must document trigger keywords (found {found})"


class TestHandoffAntiPatterns:
    """CT-2: Anti-pattern coverage."""

    def test_all_anti_patterns_documented(self):
        content = read_skill()
        patterns = [
            "Missing P15",
            "No \"first action\"",
            "PR table without SHAs",
            "Lessons buried",
            "Aspirational scope",
        ]
        for p in patterns:
            assert p.lower() in content.lower(), \
                f"Must document anti-pattern: {p}"

    def test_validation_checklist(self):
        content = read_skill()
        expected_checks = [
            "TL;DR",
            "P15 snapshot",
            "PR table",
            "First action",
            "Pickup state",
        ]
        for check in expected_checks:
            assert check in content, f"Validation checklist must include '{check}'"


class TestHandoffComposition:
    """CT-3: Composition rules."""

    def test_composition_rules_documented(self):
        content = read_skill()
        assert "persist" in content.lower(), "Must document persist composition"
        assert "bookkeeping" in content.lower(), "Must document bookkeeping composition"

    def test_file_placement_rules(self):
        content = read_skill()
        assert "docs/handoffs/" in content, "Must document workspace handoff path"
        assert "Project-local" in content or "project-local" in content.lower(), \
            "Must document project-local placement"


class TestHandoffAvailable:
    """CT-4: Availability."""

    def test_skill_substantial(self):
        content = read_skill()
        assert len(content) > 500, "SKILL.md must have substantial content"

    def test_template_reference_exists(self):
        ref_dir = os.path.join(SKILL_DIR, "references")
        if os.path.isdir(ref_dir):
            template = os.path.join(ref_dir, "handoff-template.md")
            assert os.path.isfile(template), "handoff-template.md must exist"
