import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from chembl_api import (
    _build_url, _normalize_activity, UNIT_CONVERSION_TO_NM,
    SEARCHABLE_ENDPOINTS, ENDPOINT_MAP, BASE_URL
)


class TestChemblBuild:
    def setup_method(self):
        pass

    def test_build_url_molecule_search(self):
        url = _build_url("molecule", search="aspirin", limit=5)
        assert BASE_URL in url
        assert "molecule" in url
        assert "search" in url
        assert "q=aspirin" in url

    def test_build_url_with_resource_id(self):
        url = _build_url("molecule", resource_id="CHEMBL25")
        assert "CHEMBL25" in url


class TestChemblNormalize:
    def test_normalize_activity_valid_nm(self):
        record = {"standard_value": 100, "standard_units": "nM"}
        result = _normalize_activity(record)
        assert result["normalized_value_nM"] == 100.0

    def test_normalize_activity_converts_um(self):
        record = {"standard_value": 1.0, "standard_units": "uM"}
        result = _normalize_activity(record)
        assert result["normalized_value_nM"] == pytest.approx(1000.0)


class TestChemblConstants:
    def test_unit_conversion_table(self):
        assert UNIT_CONVERSION_TO_NM["nm"] == 1.0
        assert UNIT_CONVERSION_TO_NM["um"] == 1000.0

    def test_molecule_is_searchable(self):
        assert "molecule" in SEARCHABLE_ENDPOINTS
        assert "activity" in SEARCHABLE_ENDPOINTS

    def test_endpoint_map_entries(self):
        assert ENDPOINT_MAP["molecule"] == "molecule"
        assert ENDPOINT_MAP["activity"] == "activity"
