import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from gtex_client import GTExClient


class TestGTEx:
    def setup_method(self):
        self.client = GTExClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)

    def test_search_returns_dict(self):
        result = self.client.search("test")
        assert isinstance(result, dict)

    def test_empty_query_handled(self):
        result = self.client.search("")
        assert isinstance(result, dict)

    def test_get_median_expression_returns_dict(self):
        result = self.client.get_median_expression("ENSG00000141510.17")
        assert isinstance(result, dict)

    def test_get_isoform_expression_returns_dict(self):
        result = self.client.get_isoform_expression("ENSG00000141510.17")
        assert isinstance(result, dict)
