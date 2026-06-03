import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestUniBindImports:
    def test_import_unibind_api(self):
        import unibind_api
        assert unibind_api is not None

    def test_api_prefix_defined(self):
        import unibind_api
        assert len(unibind_api.UNIBIND_API_PREFIX) > 0

    def test_client_instantiated(self):
        import unibind_api
        assert unibind_api.CLIENT is not None

    def test_make_request_function_exists(self):
        import unibind_api
        assert callable(unibind_api.make_request)

    def test_write_output_function_exists(self):
        import unibind_api
        assert callable(unibind_api.write_output)


class TestUniBindClient:
    def setup_method(self):
        import unibind_api
        self.api = unibind_api

    def test_make_request_returns_data(self):
        result = self.api.make_request("api/v1/species/")
        assert isinstance(result, dict)

    def test_make_request_has_results(self):
        result = self.api.make_request("api/v1/species/")
        assert "results" in result

    def test_list_species_returns_dict(self):
        result = self.api.make_request("api/v1/species/")
        assert "count" in result or "results" in result

    def test_list_collections_returns_dict(self):
        result = self.api.make_request("api/v1/collections/")
        assert isinstance(result, dict)

    def test_list_tfs_returns_dict(self):
        result = self.api.make_request("api/v1/tfs/?page_size=5")
        assert isinstance(result, dict)

    def test_get_dataset_returns_dict(self):
        result = self.api.make_request(
            "api/v1/datasets/ENCSR000BQI.A549.CEBPB/"
        )
        assert isinstance(result, dict)

    def test_bad_endpoint_returns_error(self):
        result = self.api.make_request("api/v1/datasets/NONEXISTENT12345/")
        assert isinstance(result, dict)
