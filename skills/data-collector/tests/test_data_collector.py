"""
TDD: data-collector — World Bank + IBGE data pipeline
Tests DataCollector class, cache, correlations, and CLI.
"""
import os
import sys
import json
import tempfile
import pytest

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts")
sys.path.insert(0, SCRIPTS_DIR)

from data_collector import DataCollector, WORLD_BANK_INDICATORS, IBGE_INDICATORS


class TestDataCollectorInit:
    """CT-1: DataCollector initialization and structure."""

    def test_init_default(self):
        dc = DataCollector()
        assert dc.cache_db.endswith(".db"), "Cache must be SQLite file"
        assert dc.indicators == {}, "Indicators dict starts empty"
        assert dc.dataframe == {}, "DataFrame dict starts empty"

    def test_init_custom_path(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.db")
            dc = DataCollector(cache_db=path)
            assert dc.cache_db == path
            assert os.path.isfile(path), "Cache DB created on init"

    def test_indicator_registry_loaded(self):
        assert len(WORLD_BANK_INDICATORS) >= 20, "Must have 20+ World Bank indicators"
        assert "NY.GDP.PCAP.CD" in WORLD_BANK_INDICATORS, "GDP indicator present"
        assert "SI.POV.GINI" in WORLD_BANK_INDICATORS, "Gini indicator present"

    def test_ibge_data_present(self):
        assert len(IBGE_INDICATORS) >= 3, "Must have 3+ IBGE indicators"
        assert "populacao_milhoes" in IBGE_INDICATORS, "Population indicator present"


class TestDataCollectorMethods:
    """CT-2: Core methods (build_dataframe, summary, correlations)."""

    def test_build_dataframe_structure(self):
        dc = DataCollector()
        df = dc.build_dataframe()
        assert "years" in df, "DataFrame must have years"
        assert len(df["years"]) >= 5, "Must have 5+ years of data"
        assert isinstance(df["years"][0], int), "Years must be integers"

    def test_get_brazil_summary(self):
        dc = DataCollector()
        summary = dc.get_brazil_summary()
        assert "country" in summary, "Summary must have country"
        assert "Brasil" in summary["country"], "Country must be Brasil"
        assert "period" in summary, "Summary must have period"
        assert "sources" in summary, "Summary must have sources"
        assert "indicators" in summary, "Summary must have indicators"
        assert len(summary["indicators"]) > 0, "Must have indicator data"

    def test_compute_correlations(self):
        dc = DataCollector()
        dc.build_dataframe()
        corrs = dc.compute_correlations()
        assert isinstance(corrs, list), "Correlations must be a list"
        # Should have some correlations (at least structure is valid)
        for c in corrs[:3]:
            assert "ind_a" in c, "Correlation must have ind_a"
            assert "ind_b" in c, "Correlation must have ind_b"
            assert "r" in c, "Correlation must have r coefficient"
            assert -1.0 <= c["r"] <= 1.0, "r must be in [-1, 1]"

    def test_summary_indicators_have_trend(self):
        dc = DataCollector()
        summary = dc.get_brazil_summary()
        for ind, info in summary["indicators"].items():
            assert "trend" in info, f"Indicator {ind} must have trend"
            assert info["trend"] in ("up", "down", "stable"), \
                f"Trend must be up/down/stable, got {info['trend']}"
            assert "change_pct" in info, f"Indicator {ind} must have change_pct"


class TestDataCollectorCache:
    """CT-3: SQLite cache and error handling."""

    def test_cache_initialized(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.db")
            dc = DataCollector(cache_db=path)
            import sqlite3
            conn = sqlite3.connect(path)
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = [t[0] for t in tables]
            assert "wb_cache" in table_names, "wb_cache table must exist"
            assert "fetch_log" in table_names, "fetch_log table must exist"
            conn.close()

    def test_fetch_with_empty_cache_returns_empty(self):
        """When no cache and no API, returns empty list gracefully."""
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.db")
            dc = DataCollector(cache_db=path)
            # This will try API and fail gracefully (no network in tests)
            result = dc.fetch_world_bank("NY.GDP.PCAP.CD")
            # Should return empty list or cached data without crashing
            assert isinstance(result, list), "fetch must return list"

    def test_build_dataframe_resilient(self):
        """build_dataframe should not crash even without network."""
        dc = DataCollector()
        df = dc.build_dataframe()
        years = df["years"]
        assert len(years) >= 5, "Should have years even offline"
        # All indicator columns should exist (may have None values)
        for ind in list(WORLD_BANK_INDICATORS.keys())[:5]:
            assert ind in df, f"Column {ind} must be in DataFrame"


class TestDataCollectorAvailable:
    """CT-4: Availability and integration."""

    def test_module_importable(self):
        from data_collector import DataCollector as DC
        assert DC is not None
        assert callable(DC), "DataCollector must be callable"

    def test_cli_capable(self):
        """Verify the module can be imported without side effects."""
        import data_collector as dc_mod
        assert hasattr(dc_mod, "BRAZIL_TIME"), "Must have BRAZIL_TIME function"
