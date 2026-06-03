import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from string_client import StringClient


class TestStringClient:
    def setup_method(self):
        self.client = StringClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_available_is_true(self):
        assert self.client.available is True

    def test_search_returns_dict(self):
        result = self.client.search("TP53", limit=3)
        assert isinstance(result, dict)

    def test_search_has_status(self):
        result = self.client.search("TP53", limit=3)
        assert "status" in result

    def test_empty_input(self):
        result = self.client.search("")
        assert isinstance(result, dict)

    def test_empty_input_error(self):
        result = self.client.search("")
        assert result.get("status") == "error"

    def test_search_interactions_returns_dict(self):
        result = self.client.search_interactions("TP53", limit=5)
        assert isinstance(result, dict)

    def test_search_interactions_has_status(self):
        result = self.client.search_interactions("TP53", limit=5)
        assert "status" in result

    def test_result_has_source(self):
        result = self.client.search("TP53")
        assert result.get("source") == "STRING"
