import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from uniprot_tools import (
    _add_params_to_url, get_count, get_entry, search_proteins,
    UniProtError, BASE_URL
)


class TestUniProtUtils:
    def test_add_params_to_url_simple(self):
        url = "https://rest.uniprot.org/uniprotkb/search"
        params = {"query": "insulin", "size": 10}
        result = _add_params_to_url(url, params)
        assert "query=insulin" in result
        assert "size=10" in result

    def test_add_params_to_url_no_params(self):
        url = "https://rest.uniprot.org/uniprotkb/P04637"
        result = _add_params_to_url(url, None)
        assert result == url

    def test_add_params_to_url_already_has_params(self):
        url = "https://rest.uniprot.org/uniprotkb/search?existing=1"
        params = {"query": "test"}
        result = _add_params_to_url(url, params)
        assert result.startswith(url)
        assert "query=test" in result


class TestUniProtCount:
    def test_get_count_returns_int(self):
        try:
            result = get_count("insulin")
        except Exception:
            pytest.skip("Network unavailable")
        assert isinstance(result, int)
        assert result > 0


class TestUniProtEntry:
    def test_get_entry_returns_data(self):
        try:
            result = get_entry("P04637")
        except Exception:
            pytest.skip("Network unavailable")
        assert result is not None

    def test_search_proteins_yields_results(self):
        try:
            it = search_proteins("insulin", limit=3)
            first = next(it)
        except Exception:
            pytest.skip("Network unavailable")
        assert isinstance(first, dict)
        assert "results" in first
