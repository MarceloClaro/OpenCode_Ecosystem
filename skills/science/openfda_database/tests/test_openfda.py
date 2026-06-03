import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from openfda_client import OpenFDAClient


class TestOpenFDA:
    def setup_method(self):
        self.client = OpenFDAClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_search_returns_dict(self):
        result = self.client.search("aspirin", limit=5)
        assert isinstance(result, dict)

    def test_empty_query_handled(self):
        result = self.client.search("", limit=5)
        assert isinstance(result, dict)

    def test_search_labels_returns_dict(self):
        result = self.client.search_labels("aspirin", limit=5)
        assert isinstance(result, dict)

    def test_search_recalls_returns_dict(self):
        result = self.client.search_recalls("ibuprofen", limit=5)
        assert isinstance(result, dict)
