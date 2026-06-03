"""Tests for ontology-generator skill."""
import sys
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import pytest


class TestOntologyGenerator:
    """CT-1: Ontology generation and validation."""

    def test_module_imports(self):
        from generate_ontology import ONTOLOGY_SYSTEM_PROMPT
        from generate_ontology import PERSON_FALLBACK, ORGANIZATION_FALLBACK
        assert "knowledge graph" in ONTOLOGY_SYSTEM_PROMPT
        assert PERSON_FALLBACK["name"] == "Person"
        assert ORGANIZATION_FALLBACK["name"] == "Organization"

    def test_fallback_types_structure(self):
        from generate_ontology import PERSON_FALLBACK, ORGANIZATION_FALLBACK
        for fallback in [PERSON_FALLBACK, ORGANIZATION_FALLBACK]:
            assert "name" in fallback
            assert "description" in fallback
            assert "attributes" in fallback
            assert len(fallback["attributes"]) >= 1

    def test_constants_defined(self):
        from generate_ontology import (
            MAX_TEXT_LENGTH, MAX_ENTITY_TYPES, MAX_EDGE_TYPES,
        )
        assert MAX_TEXT_LENGTH > 0
        assert MAX_ENTITY_TYPES == 10
        assert MAX_EDGE_TYPES == 10

    def test_main_function_exists(self):
        import generate_ontology
        assert hasattr(generate_ontology, "main")


class TestSkillStructure:
    """CT-2: SKILL.md validates."""

    def test_skill_md_exists(self):
        assert (SKILL_DIR / "SKILL.md").exists()

    def test_references_exist(self):
        refs = SKILL_DIR / "references"
        assert refs.is_dir()
        ref_files = list(refs.glob("*.md"))
        assert len(ref_files) >= 1
