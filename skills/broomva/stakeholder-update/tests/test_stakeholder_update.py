"""
TDD: stakeholder-update — Multi-audience project communication
Validates SKILL.md structure, three-version format, and behavioral rules.
"""
import os
import pytest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")


def read_skill():
    with open(SKILL_MD, "r", encoding="utf-8") as f:
        return f.read()


class TestStakeholderUpdateStructure:
    """CT-1: SKILL.md structure validation."""

    def test_skill_md_exists(self):
        assert os.path.isfile(SKILL_MD), "SKILL.md must exist"

    def test_has_frontmatter(self):
        content = read_skill()
        assert content.startswith("---"), "SKILL.md must have YAML frontmatter"
        assert "name:" in content, "Frontmatter must include 'name'"
        assert "stakeholder-update" in content.lower(), "Must identify skill name"

    def test_has_three_versions(self):
        content = read_skill()
        assert "Technical" in content and "Business" in content and "Customer" in content, \
            "Must define three audience versions"

    def test_has_workflow_steps(self):
        content = read_skill()
        assert "Gather" in content or "gather" in content.lower(), \
            "Must include gather step"
        assert "Extract" in content or "extract" in content.lower(), \
            "Must include extract step"


class TestStakeholderUpdateVersions:
    """CT-2: Three-version format validation."""

    def test_technical_version_template(self):
        content = read_skill()
        assert "Technical Version" in content, "Must have Technical section"
        assert "PRs" in content or "commits" in content.lower() or \
               "code" in content.lower(), "Technical version must reference code"

    def test_business_version_template(self):
        content = read_skill()
        assert "Business" in content, "Must have Business section"
        assert "metric" in content.lower() or "revenue" in content.lower() or \
               "timeline" in content.lower(), "Business version must reference metrics"

    def test_customer_version_template(self):
        content = read_skill()
        assert "Customer" in content, "Must have Customer section"
        assert "user" in content.lower() or "benefit" in content.lower(), \
            "Customer version must reference user benefits"

    def test_output_format_has_all_sections(self):
        content = read_skill()
        assert "Technical Version" in content
        assert "Business Version" in content
        assert "Customer-Facing Version" in content


class TestStakeholderUpdateBehavior:
    """CT-3: Behavioral rules validation."""

    def test_never_invent_facts(self):
        content = read_skill()
        assert "Never invent" in content or "never invent" in content.lower() or \
               "only reframe" in content.lower(), \
            "Must have rule against inventing facts"

    def test_standalone_rule(self):
        content = read_skill()
        assert "stand alone" in content.lower() or "standalone" in content.lower(), \
            "Must document standalone requirement"

    def test_vault_save_path(self):
        content = read_skill()
        assert "vault" in content.lower() or "updates" in content.lower(), \
            "Must document vault save path"


class TestStakeholderUpdateAvailable:
    """CT-4: Availability."""

    def test_skill_substantial(self):
        content = read_skill()
        assert len(content) > 200, "SKILL.md must have substantial content"

    def test_trigger_keywords_present(self):
        content = read_skill()
        triggers = ["stakeholder update", "communicate this", "translate for leadership"]
        found = sum(1 for t in triggers if t in content.lower())
        assert found >= 1, f"Must document trigger keywords (found {found})"
