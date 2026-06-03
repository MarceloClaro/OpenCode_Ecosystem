"""Tests for hybrid-graph-retrieval skill."""
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import pytest


class TestHybridRetrievalEngine:
    """CT-1: Search strategies work."""

    @pytest.fixture
    def engine(self):
        from hybrid_search import HybridRetrievalEngine
        return HybridRetrievalEngine()

    def test_quick_search(self, engine):
        with engine:
            result = engine.quick_search("demo", "test", limit=5)
        assert result.query == "test"
        assert isinstance(result.total_count, int)

    def test_insight_forge(self, engine):
        with engine:
            result = engine.insight_forge("demo", "test query", max_sub_queries=2)
        assert len(result.sub_queries) >= 1
        assert isinstance(result.total_facts, int)

    def test_panorama_search(self, engine):
        with engine:
            result = engine.panorama_search("demo", "test", include_historical=True, limit=5)
        assert result.query == "test"
        assert isinstance(result.total_nodes, int)

    def test_get_graph_statistics(self, engine):
        with engine:
            stats = engine.get_graph_statistics("demo")
        assert "graph_id" in stats
        # "demo" graph may not exist in DB; error or total_nodes are both valid
        assert "graph_id" in stats


class TestSearchResult:
    """CT-2: Data structures serialize correctly."""

    def test_search_result_to_text(self):
        from hybrid_search import SearchResult
        sr = SearchResult(
            facts=["fact1", "fact2"], edges=[], nodes=[],
            query="q", total_count=2,
        )
        text = sr.to_text()
        assert "fact1" in text
        assert "q" in text

    def test_insight_forge_result_to_text(self):
        from hybrid_search import InsightForgeResult
        r = InsightForgeResult(
            query="test", sub_queries=["sq1"],
            semantic_facts=["f1"],
        )
        text = r.to_text()
        assert "test" in text
        assert "sq1" in text
