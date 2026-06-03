import pytest, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from clinical_trials_client import ClinicalTrialsClient


class TestClinicalTrials:
    def setup_method(self):
        self.client = ClinicalTrialsClient()

    def test_available(self):
        assert isinstance(self.client.available, bool)
        assert self.client.available is True

    def test_search_returns_dict(self):
        result = self.client.search("test", page_size=5)
        assert isinstance(result, dict)

    def test_empty_query_handled(self):
        result = self.client.search("")
        assert isinstance(result, dict)

    def test_get_study_invalid_id(self):
        result = self.client.get_study("NCT_INVALID")
        assert isinstance(result, dict)

    def test_search_by_condition_returns_dict(self):
        result = self.client.search_by_condition("breast cancer", page_size=5)
        assert isinstance(result, dict)
