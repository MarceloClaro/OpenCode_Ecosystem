import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from ensembl_client import EnsemblClient


class TestEnsembl:
    def setup_method(self):
        self.client = EnsemblClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_search_returns_dict(self):
        result = self.client.search("test", limit=5)
        assert isinstance(result, dict)

    def test_empty_query_handled(self):
        result = self.client.search("", limit=5)
        assert isinstance(result, dict)

    def test_get_gene_returns_dict(self):
        result = self.client.get_gene("ENSG00000139618")
        assert isinstance(result, dict)

    def test_get_variant_returns_dict(self):
        result = self.client.get_variant("rs699")
        assert isinstance(result, dict)
