import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from arxiv_client import ArxivClient


class TestArxivClient:
    def setup_method(self):
        self.client = ArxivClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_available_is_true(self):
        assert self.client.available is True

    def test_search_returns_dict(self):
        result = self.client.search("machine learning", limit=2)
        assert isinstance(result, dict)

    def test_search_has_status(self):
        result = self.client.search("machine learning", limit=2)
        assert "status" in result

    def test_empty_input(self):
        result = self.client.search("")
        assert isinstance(result, dict)

    def test_search_by_author_returns_dict(self):
        result = self.client.search_by_author("Hinton", limit=3)
        assert isinstance(result, dict)

    def test_search_by_author_has_status(self):
        result = self.client.search_by_author("Hinton", limit=3)
        assert "status" in result

    def test_search_by_category_returns_dict(self):
        result = self.client.search_by_category("cs.AI", limit=3)
        assert isinstance(result, dict)

    def test_search_by_category_has_status(self):
        result = self.client.search_by_category("cs.AI", limit=3)
        assert "status" in result

    def test_result_has_source(self):
        result = self.client.search("test")
        assert result.get("source") == "arXiv"
