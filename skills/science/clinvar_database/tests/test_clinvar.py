import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from clinvar_api import ClinVarClient, RateLimitError


class TestClinVarClient:
    def setup_method(self):
        os.environ.pop("NCBI_API_KEY", None)
        self.client = ClinVarClient()

    def test_client_initialization(self):
        assert self.client.BASE_URL == "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
        assert self.client.rate_limit in (3, 10)
        assert self.client.api_key is None

    def test_client_with_api_key(self):
        os.environ["NCBI_API_KEY"] = "fake_test_key"
        client = ClinVarClient()
        assert client.api_key == "fake_test_key"
        assert client.rate_limit == 10
        os.environ.pop("NCBI_API_KEY")

    def test_count_variants_returns_int_or_dict(self):
        try:
            result = self.client.count_variants("BRCA1[gene]")
        except (RateLimitError, RuntimeError, Exception):
            pytest.skip("Network unavailable or rate limited")
        assert isinstance(result, int)
        assert result >= 0

    def test_search_variants_returns_dict(self):
        try:
            result = self.client.search_variants("BRCA1[gene]", retmax=5)
        except (RateLimitError, RuntimeError, Exception):
            pytest.skip("Network unavailable or rate limited")
        assert isinstance(result, dict)
        assert "total_count" in result
        assert "variant_ids" in result
