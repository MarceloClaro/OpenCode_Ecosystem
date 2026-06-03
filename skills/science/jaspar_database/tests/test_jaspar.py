import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestJASPARImports:
    def test_import_jaspar_api(self):
        import jaspar_api
        assert jaspar_api is not None

    def test_jaspar_url_defined(self):
        import jaspar_api
        assert jaspar_api.JASPAR_URL.startswith("https://")

    def test_client_instantiated(self):
        import jaspar_api
        assert jaspar_api._CLIENT is not None

    def test_valid_formats_defined(self):
        import jaspar_api
        assert isinstance(jaspar_api._VALID_FORMATS, tuple)
        assert "json" in jaspar_api._VALID_FORMATS

    def test_validate_matrix_id_valid(self):
        import jaspar_api
        assert jaspar_api.validate_matrix_id("MA0488.2") is None

    def test_validate_matrix_id_invalid_raises(self):
        import jaspar_api
        with pytest.raises(SystemExit):
            jaspar_api.validate_matrix_id("invalid")


class TestJASPARClient:
    """Thin wrapper tests around JASPAR API functions."""

    def setup_method(self):
        import jaspar_api
        self.api = jaspar_api

    def test_dict_to_yaml_returns_string(self):
        data = {"key": "value", "nested": {"inner": 1}}
        result = self.api.dict_to_yaml(data)
        assert isinstance(result, str)
        assert "key: value" in result
        assert "inner: 1" in result

    def test_dict_to_yaml_with_list(self):
        data = {"items": [1, 2, 3]}
        result = self.api.dict_to_yaml(data)
        assert "1, 2, 3" in result
