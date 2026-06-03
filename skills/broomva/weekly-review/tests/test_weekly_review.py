"""
TDD: weekly-review — Weekly vault + git activity scanner
Validates SKILL.md structure, output format, and behavioral rules.
"""
import os
import pytest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")


def read_skill():
    with open(SKILL_MD, "r", encoding="utf-8") as f:
        return f.read()


class TestWeeklyReviewStructure:
    """CT-1: SKILL.md structure validation."""

    def test_skill_md_exists(self):
        assert os.path.isfile(SKILL_MD), "SKILL.md must exist"

    def test_has_frontmatter(self):
        content = read_skill()
        assert content.startswith("---"), "SKILL.md must have YAML frontmatter"
        assert "name:" in content, "Frontmatter must include 'name'"
        assert "weekly-review" in content.lower(), "Must identify skill name"

    def test_has_six_workflow_steps(self):
        content = read_skill()
        steps = [
            "Scan vault" in content or "scan vault" in content.lower(),
            "Scan git" in content or "scan git" in content.lower(),
            "Extract completed" in content or "extract completed" in content.lower(),
            "Find open" in content or "find open" in content.lower(),
            "Identify themes" in content or "identify themes" in content.lower(),
            "Generate next" in content or "generate next" in content.lower(),
        ]
        assert sum(steps) >= 4, f"Must document at least 4/6 steps (found {sum(steps)})"

    def test_has_output_format(self):
        content = read_skill()
        assert "Output Format" in content or "output format" in content.lower(), \
            "Must define output format"


class TestWeeklyReviewFormat:
    """CT-2: Output format validation."""

    def test_weekly_at_a_glance_section(self):
        content = read_skill()
        assert "Week at a Glance" in content, "Must have Week at a Glance"
        assert "Commits" in content, "Must track commits"
        assert "Notes" in content, "Must track notes"

    def test_priorities_section(self):
        content = read_skill()
        assert "Next Week" in content or "Priorities" in content, \
            "Must have priorities section"

    def test_project_activity_table(self):
        content = read_skill()
        assert "Project Activity" in content or "project activity" in content.lower(), \
            "Must have project activity section"
        assert "Status" in content, "Must track project status"


class TestWeeklyReviewBehavior:
    """CT-3: Behavioral rules validation."""

    def test_data_driven_rule(self):
        content = read_skill()
        assert "emerge from the data" in content.lower() or \
               "not be invented" in content.lower() or \
               "emerge from data" in content.lower(), \
            "Must require data-driven priorities"

    def test_sparse_vault_fallback(self):
        content = read_skill()
        assert "git" in content.lower(), "Must reference git activity fallback"

    def test_scannable_rule(self):
        content = read_skill()
        assert "scannable" in content.lower() or "3 minutes" in content, \
            "Must document scannability requirement"


class TestWeeklyReviewAvailable:
    """CT-4: Availability."""

    def test_skill_substantial(self):
        content = read_skill()
        assert len(content) > 300, "SKILL.md must have substantial content"

    def test_vault_integration(self):
        content = read_skill()
        assert "vault" in content.lower() or "save to" in content.lower(), \
            "Must document vault integration"
