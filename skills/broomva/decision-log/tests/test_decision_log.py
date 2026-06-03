"""
TDD: decision-log — Decision capture and documentation
Validates SKILL.md structure and output format template.
"""
import os
import pytest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")


def read_skill():
    with open(SKILL_MD, "r", encoding="utf-8") as f:
        return f.read()


class TestDecisionLogStructure:
    """CT-1: SKILL.md structure validation."""

    def test_skill_md_exists(self):
        assert os.path.isfile(SKILL_MD), "SKILL.md must exist"

    def test_has_frontmatter(self):
        content = read_skill()
        assert content.startswith("---"), "SKILL.md must have YAML frontmatter"
        assert "name:" in content, "Frontmatter must include 'name'"
        assert "decision-log" in content, "Must identify skill name"

    def test_has_workflow_steps(self):
        content = read_skill()
        assert "Capture" in content or "capture" in content.lower(), \
            "Must include capture step"
        assert "rationale" in content.lower(), "Must include rationale step"

    def test_has_output_format(self):
        content = read_skill()
        assert "Output Format" in content or "output format" in content.lower(), \
            "Must define output format"


class TestDecisionLogTemplate:
    """CT-2: Output template validation."""

    def test_template_has_required_fields(self):
        content = read_skill()
        required = ["date", "status", "decision-makers", "reversibility", "tags"]
        for field in required:
            assert field in content, f"Template must include '{field}' field"

    def test_template_has_alternatives_section(self):
        content = read_skill()
        assert "Alternatives Considered" in content or \
               "alternatives considered" in content.lower(), \
               "Template must have alternatives section"

    def test_template_has_consequences_section(self):
        content = read_skill()
        assert "Consequences" in content or "consequences" in content.lower(), \
               "Template must have consequences section"


class TestDecisionLogBehavior:
    """CT-3: Behavioral rules validation."""

    def test_alternatives_rule_documented(self):
        content = read_skill()
        assert "skip" in content.lower() or "considered" in content.lower(), \
            "Must document alternatives rule"

    def test_one_way_vs_two_way_door(self):
        content = read_skill()
        assert "one-way" in content.lower() or "two-way" in content.lower() or \
               "reversibility" in content.lower(), "Must document reversibility concept"

    def test_vault_integration(self):
        content = read_skill()
        assert "vault" in content.lower() or "save" in content.lower(), \
            "Must document vault integration"


class TestDecisionLogAvailable:
    """CT-4: Availability."""

    def test_skill_not_empty(self):
        content = read_skill()
        assert len(content) > 300, "SKILL.md must have substantial content"

    def test_frontmatter_valid(self):
        content = read_skill()
        sections = content.split("---")
        assert len(sections) >= 3, "Must have valid YAML frontmatter"
