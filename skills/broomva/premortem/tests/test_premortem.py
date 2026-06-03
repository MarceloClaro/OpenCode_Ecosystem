"""
TDD: premortem — Pre-mortem analysis on plans and decisions
Validates SKILL.md structure, workflow steps, and output format.
"""
import os
import pytest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")


def read_skill():
    with open(SKILL_MD, "r", encoding="utf-8") as f:
        return f.read()


class TestPremortemStructure:
    """CT-1: SKILL.md structure validation."""

    def test_skill_md_exists(self):
        assert os.path.isfile(SKILL_MD), "SKILL.md must exist"

    def test_has_frontmatter(self):
        content = read_skill()
        assert content.startswith("---"), "SKILL.md must have YAML frontmatter"
        assert "name:" in content, "Frontmatter must include 'name'"
        assert "premortem" in content.lower(), "Must identify skill name"

    def test_has_trigger_keywords(self):
        content = read_skill()
        triggers = ["premortem this", "what could kill this", "what could go wrong"]
        found = sum(1 for t in triggers if t in content.lower())
        assert found >= 2, f"Must document trigger keywords (found {found})"

    def test_has_context_gathering_section(self):
        content = read_skill()
        assert "context" in content.lower(), "Must document context gathering"


class TestPremortemWorkflow:
    """CT-2: Workflow steps validation."""

    def test_six_steps_documented(self):
        content = read_skill()
        steps = [
            "step 1" in content.lower() or "set the frame" in content.lower(),
            "step 2" in content.lower() or "generate failure" in content.lower(),
            "step 3" in content.lower() or "deep-dive" in content.lower(),
            "step 4" in content.lower() or "synthesis" in content.lower(),
            "step 5" in content.lower() or "generate the" in content.lower() or "report" in content.lower(),
            "step 6" in content.lower() or "save the transcript" in content.lower(),
        ]
        assert sum(steps) >= 4, f"Must document at least 4/6 steps (found {sum(steps)})"

    def test_output_files_defined(self):
        content = read_skill()
        assert "premortem-report" in content, "Must define report filename"
        assert "premortem-transcript" in content, "Must define transcript filename"
        assert ".html" in content, "Must output HTML report"

    def test_synthesis_components_defined(self):
        content = read_skill()
        components = [
            "Most Likely Failure",
            "Hidden Assumption",
            "Revised Plan",
            "Pre-Launch Checklist",
        ]
        for c in components:
            assert c.lower() in content.lower(), f"Must include '{c}'"


class TestPremortemRules:
    """CT-3: Important rules validation."""

    def test_attribution_chain_present(self):
        content = read_skill()
        assert "Klein" in content or "Kahneman" in content, \
            "Must attribute original method authors"

    def test_context_threshold_rule(self):
        content = read_skill()
        assert "minimum" in content.lower() and "threshold" in content.lower() or \
               "insufficient context" in content.lower() or \
               "minimum bar" in content.lower(), \
            "Must document minimum context threshold"


class TestPremortemAvailable:
    """CT-4: Availability."""

    def test_skill_substantial(self):
        content = read_skill()
        assert len(content) > 800, "SKILL.md must have substantial content"

    def test_bad_targets_documented(self):
        content = read_skill()
        assert "Bad premortem targets" in content or \
               "bad premortem target" in content.lower() or \
               "vague" in content.lower(), \
            "Must document when NOT to use premortem"
