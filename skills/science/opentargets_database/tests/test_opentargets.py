import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from opentargets_client import OpenTargetsClient


class TestOpenTargets:
    def setup_method(self):
        self.client = OpenTargetsClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_search_returns_dict(self):
        result = self.client.search("BRAF", limit=5)
        assert isinstance(result, dict)

    def test_empty_query_handled(self):
        result = self.client.search("", limit=5)
        assert isinstance(result, dict)

    def test_search_by_disease_returns_dict(self):
        result = self.client.search_by_disease("asthma", limit=5)
        assert isinstance(result, dict)

    def test_search_results_has_status(self):
        result = self.client.search("BRAF", limit=2)
        assert "status" in result
        assert result["status"] in ("ok", "error")
