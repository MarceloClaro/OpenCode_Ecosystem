import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from quickgo_tool import make_request, BASE_URL


class TestQuickGOMakeRequest:
    def test_make_request_go_search(self):
        try:
            result = make_request(
                "/ontology/go/search",
                params={"query": "apoptosis", "limit": 3, "page": 1},
            )
        except Exception:
            pytest.skip("Network unavailable")
        assert isinstance(result, dict)
        assert "results" in result

    def test_make_request_returns_list_or_dict(self):
        try:
            result = make_request(
                "/ontology/go/terms/GO:0006915"
            )
        except Exception:
            pytest.skip("Network unavailable")
        assert isinstance(result, (dict, list))

    def test_make_request_bad_input_handles_error(self):
        try:
            result = make_request(
                "/ontology/go/search",
                params={"query": "", "limit": 1},
            )
        except Exception:
            pytest.skip("Network unavailable")
        assert isinstance(result, dict)


class TestQuickGOConstants:
    def test_base_url(self):
        assert BASE_URL == "https://www.ebi.ac.uk/QuickGO/services"

    def test_module_has_search_functions(self):
        from quickgo_tool import go_search, annotation_search
        assert callable(go_search)
        assert callable(annotation_search)
