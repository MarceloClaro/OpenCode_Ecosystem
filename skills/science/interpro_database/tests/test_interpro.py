import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from interpro_client import InterProClient


class TestInterPro:
    def setup_method(self):
        self.client = InterProClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_search_returns_dict(self):
        result = self.client.search("kinase", limit=5)
        assert isinstance(result, dict)

    def test_empty_query_handled(self):
        result = self.client.search("", limit=5)
        assert isinstance(result, dict)

    def test_search_by_accession_returns_dict(self):
        result = self.client.search_by_accession("IPR020422")
        assert isinstance(result, dict)

    def test_search_by_protein_returns_dict(self):
        result = self.client.search_by_protein("P04637")
        assert isinstance(result, dict)
