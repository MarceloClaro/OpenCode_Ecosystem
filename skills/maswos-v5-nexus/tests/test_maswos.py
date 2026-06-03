"""
TDD: maswos-v5-nexus — Framework MASWOS V5 NEXUS
Validates SKILL.md structure, reference files integrity, and component enumeration.
"""
import os
import pytest

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_MD = os.path.join(SKILL_DIR, "SKILL.md")
REFS_DIR = os.path.join(SKILL_DIR, "references")


def read_skill():
    with open(SKILL_MD, "r", encoding="utf-8") as f:
        return f.read()


class TestMaswosStructure:
    """CT-1: SKILL.md structure validation."""

    def test_skill_md_exists(self):
        assert os.path.isfile(SKILL_MD), "SKILL.md must exist"

    def test_has_frontmatter(self):
        content = read_skill()
        assert content.startswith("---"), "SKILL.md must have YAML frontmatter"
        assert "name:" in content, "Frontmatter must include 'name'"
        assert "version:" in content, "Frontmatter must include 'version'"
        assert "maswos-v5-nexus" in content, "Must reference framework name"

    def test_references_directory_exists(self):
        assert os.path.isdir(REFS_DIR), "references/ directory must exist"


class TestMaswosReferences:
    """CT-2: Reference file integrity."""

    def test_all_references_present(self):
        expected_refs = [
            "architecture.md",
            "rag-strategies.md",
            "agents-and-skills.md",
            "audit-module.md",
            "mcp-integration.md",
        ]
        for ref in expected_refs:
            path = os.path.join(REFS_DIR, ref)
            assert os.path.isfile(path), f"Missing reference: {ref}"

    def test_references_have_content(self):
        for fname in os.listdir(REFS_DIR):
            if fname.endswith(".md"):
                path = os.path.join(REFS_DIR, fname)
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                assert len(content) > 50, f"Reference {fname} must have content (got {len(content)} chars)"

    def test_skill_describes_components(self):
        content = read_skill()
        assert "130+" in content or "agentes" in content.lower(), \
            "Must mention 130+ agents"
        assert "RAG" in content, "Must mention RAG strategies"
        assert "Qualis" in content, "Must mention Qualis A1"


class TestMaswosComponents:
    """CT-3: Component enumeration."""

    def test_rag_strategies_enumerated(self):
        content = read_skill()
        strategies = ["Vanilla", "Memory", "Graph", "Hybrid", "CRAG", "Adaptive", "Fusion", "HyDE"]
        found = sum(1 for s in strategies if s in content)
        assert found >= 4, f"Must mention at least 4 RAG strategies (found {found})"

    def test_pipeline_documented(self):
        content = read_skill()
        assert "pipeline" in content.lower(), "Must document pipeline"
        assert "auditoria" in content.lower() or "audit" in content.lower(), \
            "Must document audit module"


class TestMaswosAvailable:
    """CT-4: Availability."""

    def test_all_refs_readable(self):
        for fname in os.listdir(REFS_DIR):
            path = os.path.join(REFS_DIR, fname)
            with open(path, "r", encoding="utf-8") as f:
                f.read(100)  # Readable check
        assert True

    def test_skill_size_substantial(self):
        content = read_skill()
        assert len(content) > 200, "SKILL.md must be substantial"
