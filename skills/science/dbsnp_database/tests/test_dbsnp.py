import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from dbsnp_client import DbSNPClient


class TestDbSNP:
    def setup_method(self):
        self.client = DbSNPClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_search_returns_dict(self):
        result = self.client.search("test", limit=5)
        assert isinstance(result, dict)

    def test_empty_query_handled(self):
        result = self.client.search("", limit=5)
        assert isinstance(result, dict)

    def test_get_variant_returns_dict(self):
        result = self.client.get_variant("rs334")
        assert isinstance(result, dict)

    def test_search_by_gene_returns_dict(self):
        result = self.client.search_by_gene("BRCA1", limit=5)
        assert isinstance(result, dict)
