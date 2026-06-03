import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from pubmed_api import (
    _env_params, _id_params, FUNCTIONS, search_pubmed,
    verify_medical_spelling
)


class TestPubMedFunctions:
    def test_functions_registry(self):
        assert "search_pubmed" in FUNCTIONS
        assert "fetch_article_abstracts" in FUNCTIONS
        assert "verify_medical_spelling" in FUNCTIONS
        assert "get_full_text_pmc" in FUNCTIONS

    def test_env_params_returns_dict(self):
        params = _env_params()
        assert isinstance(params, dict)

    def test_id_params_with_list(self):
        result = _id_params(["123", "456"], "", "")
        assert isinstance(result, dict)
        assert "id" in result
        assert result["id"] == "123,456"

    def test_id_params_with_webenv(self):
        result = _id_params([], "WEB123", "key1")
        assert result["WebEnv"] == "WEB123"
        assert result["query_key"] == "key1"


class TestPubMedSearch:
    def test_search_returns_list(self):
        try:
            result = search_pubmed("cancer", max_results=3)
        except Exception:
            pytest.skip("Network unavailable")
        assert isinstance(result, (list, dict))

    def test_verify_spelling_returns_dict(self):
        try:
            result = verify_medical_spelling("apoptosis")
        except Exception:
            pytest.skip("Network unavailable")
        assert isinstance(result, dict)
        assert "original" in result
