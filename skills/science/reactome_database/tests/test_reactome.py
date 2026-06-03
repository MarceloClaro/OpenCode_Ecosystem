import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from reactome_client import ReactomeClient


class TestReactome:
    def setup_method(self):
        self.client = ReactomeClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_search_returns_dict(self):
        result = self.client.search("apoptosis", limit=5)
        assert isinstance(result, dict)

    def test_empty_query_handled(self):
        result = self.client.search("", limit=5)
        assert isinstance(result, dict)

    def test_search_by_gene_returns_dict(self):
        result = self.client.search_by_gene("TP53")
        assert isinstance(result, dict)

    def test_get_pathway_details_returns_dict(self):
        result = self.client.get_pathway_details("R-HSA-109581")
        assert isinstance(result, dict)
