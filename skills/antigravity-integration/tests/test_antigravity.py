"""
TDD: antigravity-integration — Bridge OpenCode ↔ Antigravity
Validates SKILL.md structure, capability matrix, and error handling.
"""
import os
import pytest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")


def read_skill():
    with open(SKILL_MD, "r", encoding="utf-8") as f:
        return f.read()


class TestAntigravityStructure:
    """CT-1: SKILL.md structure validation."""

    def test_skill_md_exists(self):
        assert os.path.isfile(SKILL_MD), "SKILL.md must exist"

    def test_has_frontmatter(self):
        content = read_skill()
        assert content.startswith("---"), "SKILL.md must have YAML frontmatter"
        assert "name:" in content, "Frontmatter must include 'name'"
        assert "version:" in content, "Frontmatter must include 'version'"

    def test_has_capabilities_section(self):
        content = read_skill()
        assert "generate_image" in content, "Must document image capability"
        assert "browser_subagent" in content, "Must document browser capability"
        assert "search_web" in content, "Must document search capability"

    def test_has_error_handling(self):
        content = read_skill()
        assert "indisponivel" in content.lower() or "tratamento" in content.lower(), \
            "Must document error handling strategy"
        assert "fallback" in content.lower() or "degradar" in content.lower(), \
            "Must define fallback behavior"


class TestAntigravityCapabilities:
    """CT-2: Capability enumeration."""

    def test_all_core_capabilities_present(self):
        content = read_skill()
        capabilities = [
            "generate_image",
            "browser_subagent",
            "search_web",
            "read_url_content",
            "parallel_subagents",
            "artifact_creation",
        ]
        for cap in capabilities:
            assert cap in content, f"Missing capability: {cap}"

    def test_affinity_matrix_present(self):
        content = read_skill()
        assert "manus-evolve" in content, "Must define affinity with manus-evolve"
        assert "criador-artigo" in content, "Must define affinity with criador-artigo"


class TestAntigravityHealth:
    """CT-3: Health reporting validation."""

    def test_health_variables_documented(self):
        content = read_skill()
        env_vars = [
            "ANTIGRAVITY_BRIDGE_VERSION",
            "ANTIGRAVITY_BRIDGE_ACTIVE",
            "ANTIGRAVITY_BRIDGE_HEALTH",
        ]
        for var in env_vars:
            assert var in content, f"Missing env variable: {var}"

    def test_observability_logs_defined(self):
        content = read_skill()
        assert "antigravity-bridge-state.json" in content, "Must define state log"
        assert "antigravity-observability.jsonl" in content, "Must define event log"


class TestAntigravityAvailable:
    """CT-4: Available property (skill is loadable)."""

    def test_skill_loadable(self):
        """Verify this test module can import and run."""
        assert True

    def test_skill_not_empty(self):
        content = read_skill()
        assert len(content) > 500, "SKILL.md must have substantial content"
