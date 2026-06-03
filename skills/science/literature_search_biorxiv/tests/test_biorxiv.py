import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from biorxiv_client import BiorxivClient


class TestBiorxivClient:
    def setup_method(self):
        self.client = BiorxivClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_available_is_true(self):
        assert self.client.available is True

    def test_search_returns_dict(self):
        result = self.client.search("CRISPR", limit=2)
        assert isinstance(result, dict)

    def test_search_has_status(self):
        result = self.client.search("CRISPR", limit=2)
        assert "status" in result

    def test_empty_input(self):
        result = self.client.search("")
        assert isinstance(result, dict)

    def test_search_by_doi_returns_dict(self):
        result = self.client.search_by_doi("10.1101/2020.01.01.000000")
        assert isinstance(result, dict)

    def test_search_by_doi_has_status(self):
        result = self.client.search_by_doi("10.1101/2020.01.01.000000")
        assert "status" in result

    def test_search_by_date_returns_dict(self):
        result = self.client.search_by_date("2024-01-01", "2024-01-31", limit=5)
        assert isinstance(result, dict)

    def test_search_by_date_has_status(self):
        result = self.client.search_by_date("2024-01-01", "2024-01-31", limit=5)
        assert "status" in result

    def test_result_has_source(self):
        result = self.client.search("test")
        assert result.get("source") == "bioRxiv"
