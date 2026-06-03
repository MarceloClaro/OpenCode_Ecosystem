import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from openalex_cli import (
    _is_valid_entity_id, _build_url_with_api_key, ENTITY_TYPES,
    BASE_URL
)


class TestOpenAlexValidation:
    def test_valid_short_id(self):
        assert _is_valid_entity_id("W2741809807") is True
        assert _is_valid_entity_id("A5023888391") is True

    def test_valid_openalex_url(self):
        assert _is_valid_entity_id("https://openalex.org/W2741809807") is True

    def test_valid_doi_url(self):
        assert _is_valid_entity_id("https://doi.org/10.1234/example") is True

    def test_invalid_entity_id(self):
        assert _is_valid_entity_id("just_a_name") is False
        assert _is_valid_entity_id("") is False


class TestOpenAlexUtils:
    def test_build_url_without_api_key(self):
        url = "https://api.openalex.org/works"
        result = _build_url_with_api_key(url, None)
        assert result == url
        assert "api_key" not in result

    def test_build_url_with_api_key(self):
        url = "https://api.openalex.org/works"
        result = _build_url_with_api_key(url, "secret_key")
        assert "api_key=secret_key" in result


class TestOpenAlexConstants:
    def test_entity_types(self):
        assert "works" in ENTITY_TYPES
        assert "authors" in ENTITY_TYPES
        assert "institutions" in ENTITY_TYPES

    def test_base_url(self):
        assert BASE_URL == "https://api.openalex.org"
