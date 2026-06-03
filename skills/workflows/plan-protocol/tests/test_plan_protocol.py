"""
TDD: plan-protocol — Implementation plan creation and management
Validates SKILL.md structure and protocol rules.
"""
import os
import pytest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")


def read_skill():
    with open(SKILL_MD, "r", encoding="utf-8") as f:
        return f.read()


class TestPlanProtocolStructure:
    """CT-1: SKILL.md structure validation."""

    def test_skill_md_exists(self):
        assert os.path.isfile(SKILL_MD), "SKILL.md must exist"

    def test_has_frontmatter(self):
        content = read_skill()
        assert content.startswith("---"), "SKILL.md must have YAML frontmatter"
        assert "name:" in content, "Frontmatter must include 'name'"
        assert "plan-protocol" in content.lower(), "Must identify protocol name"

    def test_has_checklist(self):
        content = read_skill()
        assert "[ ]" in content or "- [ ]" in content, "Must have checklist items"

    def test_mentions_goal_section(self):
        content = read_skill()
        assert "Goal" in content or "goal" in content.lower(), "Must reference Goal section"


class TestPlanProtocolRules:
    """CT-2: Format rules validation."""

    def test_yaml_frontmatter_required(self):
        content = read_skill()
        assert "YAML" in content or "frontmatter" in content.lower(), \
            "Must require YAML frontmatter"

    def test_status_markers_documented(self):
        content = read_skill()
        assert "COMPLETE" in content, "Must document COMPLETE status"
        assert "IN PROGRESS" in content, "Must document IN PROGRESS status"
        assert "PENDING" in content, "Must document PENDING status"

    def test_current_task_rule(self):
        content = read_skill()
        assert "CURRENT" in content, "Must document CURRENT marker rule"


class TestPlanProtocolReferences:
    """CT-3: Reference file integrity."""

    def test_reference_directory_exists(self):
        ref_dir = os.path.join(SKILL_DIR, "reference")
        assert os.path.isdir(ref_dir), "reference/ directory must exist"

    def test_key_references_present(self):
        ref_dir = os.path.join(SKILL_DIR, "reference")
        if os.path.isdir(ref_dir):
            expected = [
                "plan-format.md",
                "state-machine.md",
                "citations-and-delegations.md",
                "examples.md",
                "troubleshooting.md",
                "before-saving-checklist.md",
            ]
            for ref in expected:
                path = os.path.join(ref_dir, ref)
                assert os.path.isfile(path), f"Missing reference: {ref}"

    def test_references_have_content(self):
        ref_dir = os.path.join(SKILL_DIR, "reference")
        if os.path.isdir(ref_dir):
            for fname in os.listdir(ref_dir):
                if fname.endswith(".md"):
                    path = os.path.join(ref_dir, fname)
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                    assert len(content) > 30, f"Reference {fname} has content"


class TestPlanProtocolAvailable:
    """CT-4: Availability."""

    def test_skill_loadable(self):
        content = read_skill()
        assert len(content) > 200, "SKILL.md must have substantial content"

    def test_allowed_tools_specified(self):
        content = read_skill()
        assert "allowed-tools" in content.lower(), "Must specify allowed tools"
