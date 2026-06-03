import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from europepmc_client import EuropePMCClient


class TestEuropePMCClient:
    def setup_method(self):
        self.client = EuropePMCClient(qps=3.0)

    def test_client_instantiated(self):
        assert self.client is not None

    def test_base_url_set(self):
        assert len(self.client.BASE_URL) > 0

    def test_search_returns_dict(self):
        result = self.client.search("CRISPR", page_size=3)
        assert isinstance(result, dict)

    def test_search_has_hit_count(self):
        result = self.client.search("CRISPR", page_size=3)
        assert "hitCount" in result

    def test_empty_input_handled(self):
        result = self.client.search("")
        assert isinstance(result, dict)

    def test_fetch_article_returns_dict(self):
        result = self.client.fetch_article("MED", "123456")
        assert isinstance(result, dict)

    def test_fetch_references_returns_dict(self):
        result = self.client.fetch_references("MED", "123456", page_size=5)
        assert isinstance(result, dict)

    def test_fetch_citations_returns_dict(self):
        result = self.client.fetch_citations("MED", "123456", page_size=5)
        assert isinstance(result, dict)

    def test_fetch_grants_returns_dict(self):
        result = self.client.fetch_grants("MR/R000001/1")
        assert isinstance(result, dict)

    def test_search_result_type_core(self):
        result = self.client.search("cancer", result_type="core", page_size=5)
        assert isinstance(result, dict)
