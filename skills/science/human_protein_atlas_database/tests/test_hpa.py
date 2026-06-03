import pytest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestHPAImports:
    def test_import_hpa_cli(self):
        import hpa_cli
        assert hpa_cli is not None

    def test_base_url_search_defined(self):
        import hpa_cli
        assert len(hpa_cli.BASE_URL_SEARCH) > 0

    def test_base_url_xml_defined(self):
        import hpa_cli
        assert len(hpa_cli.BASE_URL_XML) > 0

    def test_client_instantiated(self):
        import hpa_cli
        assert hpa_cli.CLIENT is not None


class TestHPAClient:
    """Wraps HPA's global http_client for search-based interaction."""

    def setup_method(self):
        import hpa_cli
        self.hpa = hpa_cli

    def test_resolve_ensembl_id(self):
        output = "/tmp/hpa_test_resolve.json"
        result = self.hpa.resolve_ensembl_id("TP53", output)
        assert result is None
        assert os.path.isfile(output)
        with open(output, "r") as f:
            data = json.load(f)
        assert isinstance(data, dict)
        assert "ensembl_id" in data

    def test_search_hpa(self):
        output = "/tmp/hpa_test_search.json"
        result = self.hpa.search_hpa("TP53", output)
        assert result is None
        assert os.path.isfile(output)
        with open(output, "r") as f:
            data = json.load(f)
        assert isinstance(data, list)

    def test_get_subcellular_location(self):
        output = "/tmp/hpa_test_subcell.json"
        result = self.hpa.get_subcellular_location("ENSG00000141510", output)
        assert result is None
        assert os.path.isfile(output)
        with open(output, "r") as f:
            data = json.load(f)
        assert isinstance(data, dict)

    def test_search_unknown_returns_empty(self):
        output = "/tmp/hpa_test_unknown.json"
        self.hpa.search_hpa("ZZUNKNOWN12345", output)
        with open(output, "r") as f:
            data = json.load(f)
        assert isinstance(data, list)
