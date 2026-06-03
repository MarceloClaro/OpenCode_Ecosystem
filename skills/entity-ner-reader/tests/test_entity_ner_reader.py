"""Tests for entity-ner-reader skill."""
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import pytest


class TestEntityReader:
    """CT-1: EntityReader core functionality."""

    @pytest.fixture
    def reader(self):
        from entity_reader import EntityReader, MockGraphStorage
        storage = MockGraphStorage()
        return EntityReader(storage)

    def test_filter_defined_entities(self, reader):
        result = reader.filter_defined_entities("demo")
        assert result.total_count >= 7
        assert result.filtered_count >= 5
        assert "Person" in result.entity_types

    def test_get_entities_by_type(self, reader):
        persons = reader.get_entities_by_type("demo", "Person")
        assert len(persons) >= 2
        for p in persons:
            assert "Person" in p.labels

    def test_get_entity_with_context(self, reader):
        entity = reader.get_entity_with_context("demo", "ent-001")
        assert entity is not None
        assert entity.name == "Carlos Silva"
        assert len(entity.related_edges) >= 1

    def test_empty_filter_returns_nothing(self, reader):
        result = reader.filter_defined_entities(
            "demo", defined_entity_types=["NonExistentType"]
        )
        assert result.filtered_count == 0


class TestRefineGraph:
    """CT-2: Refine graph bridge works."""

    def test_ensure_entity_tables(self):
        import sqlite3
        from refine_graph import ensure_entity_tables
        conn = sqlite3.connect(":memory:")
        ensure_entity_tables(conn)
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        assert "entities" in tables
        assert "entity_edges" in tables
        assert "entity_types" in tables
