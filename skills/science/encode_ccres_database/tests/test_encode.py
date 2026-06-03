import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestEncodePortalImports:
    def test_import_encode_portal_api(self):
        import encode_portal_api
        assert encode_portal_api is not None

    def test_base_url_defined(self):
        import encode_portal_api
        assert encode_portal_api.BASE_URL.startswith("https://")

    def test_client_instantiated(self):
        import encode_portal_api
        assert encode_portal_api._CLIENT is not None

    def test_cmd_search_function_exists(self):
        import encode_portal_api
        assert callable(encode_portal_api.cmd_search)


class TestScreenAPIImports:
    def test_import_screen_api(self):
        import screen_api
        assert screen_api is not None

    def test_api_url_defined(self):
        import screen_api
        assert screen_api.API_URL.startswith("https://")

    def test_client_instantiated(self):
        import screen_api
        assert screen_api._CLIENT is not None

    def test_run_query_function_exists(self):
        import screen_api
        assert callable(screen_api.run_query)

    def test_cmd_search_function_exists(self):
        import screen_api
        assert callable(screen_api.cmd_search)

    def test_cmd_nearby_function_exists(self):
        import screen_api
        assert callable(screen_api.cmd_nearby)

    def test_cmd_biosamples_function_exists(self):
        import screen_api
        assert callable(screen_api.cmd_biosamples)

    def test_cmd_details_function_exists(self):
        import screen_api
        assert callable(screen_api.cmd_details)

    def test_cmd_orthologs_function_exists(self):
        import screen_api
        assert callable(screen_api.cmd_orthologs)

    def test_cmd_linked_function_exists(self):
        import screen_api
        assert callable(screen_api.cmd_linked)

    def test_cmd_entex_function_exists(self):
        import screen_api
        assert callable(screen_api.cmd_entex)

    def test_cmd_gene_expression_function_exists(self):
        import screen_api
        assert callable(screen_api.cmd_gene_expression)

    def test_cmd_gwas_function_exists(self):
        import screen_api
        assert callable(screen_api.cmd_gwas)
