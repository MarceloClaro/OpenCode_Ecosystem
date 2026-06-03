import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from pubchem_client import PubChemClient


class TestPubChem:
    def setup_method(self):
        self.client = PubChemClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_search_returns_dict(self):
        result = self.client.search("aspirin", limit=5)
        assert isinstance(result, dict)

    def test_empty_query_handled(self):
        result = self.client.search("", limit=5)
        assert isinstance(result, dict)

    def test_search_by_cid_returns_dict(self):
        result = self.client.search_by_cid(2244)
        assert isinstance(result, dict)

    def test_search_bioactivities_returns_dict(self):
        result = self.client.search_bioactivities("aspirin", limit=5)
        assert isinstance(result, dict)
