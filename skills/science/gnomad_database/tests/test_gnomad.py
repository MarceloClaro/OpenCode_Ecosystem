import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from gnomad_client import GnomADClient


class TestGnomAD:
    def setup_method(self):
        self.client = GnomADClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_search_returns_dict(self):
        result = self.client.search("test", limit=5)
        assert isinstance(result, dict)

    def test_empty_query_handled(self):
        result = self.client.search("", limit=5)
        assert isinstance(result, dict)

    def test_search_by_gene_returns_dict(self):
        result = self.client.search_by_gene("BRCA2", limit=5)
        assert isinstance(result, dict)

    def test_search_by_rsid_returns_dict(self):
        result = self.client.search_by_rsid("rs334", limit=1)
        assert isinstance(result, dict)
