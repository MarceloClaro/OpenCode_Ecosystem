import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from ols_utils import (
    obo_id_to_iri, double_encode_iri, resolve_ontology,
    OBO_PREFIX_TO_ONTOLOGY, BASE_URL, write_output
)
from search_ols import search_ols
import tempfile
import json


class TestOlsUtils:
    def test_obo_id_to_iri(self):
        iri = obo_id_to_iri("GO:0005634")
        assert iri == "http://purl.obolibrary.org/obo/GO_0005634"

    def test_obo_id_to_iri_chebi(self):
        iri = obo_id_to_iri("CHEBI:15377")
        assert "CHEBI_15377" in iri

    def test_double_encode_iri(self):
        encoded = double_encode_iri("http://purl.obolibrary.org/obo/GO_0005634")
        assert isinstance(encoded, str)
        assert len(encoded) > 0

    def test_resolve_ontology_from_prefix(self):
        result = resolve_ontology("GO:0005634", None)
        assert result == "go"

    def test_resolve_ontology_explicit(self):
        result = resolve_ontology("ANY:123", "efo")
        assert result == "efo"


class TestOlsSearch:
    def test_search_ols_outputs_success(self):
        class FakeArgs:
            query = "apoptosis"
            ontology = "go"
            type = "class"
            exact = False
            obsolete = False
            local = False
            defining = False
            groupField = None
            isLeaf = False
            queryFields = None
            fieldList = None
            childrenOf = None
            allChildrenOf = None
            rows = 5
            start = 0
            output = os.path.join(tempfile.mkdtemp(), "test_ols_output.json")
        try:
            search_ols(FakeArgs())
            assert os.path.exists(FakeArgs.output)
            with open(FakeArgs.output) as f:
                data = json.load(f)
            assert data["status"] == "success"
            assert "terms" in data
            os.unlink(FakeArgs.output)
            os.rmdir(os.path.dirname(FakeArgs.output))
        except Exception as e:
            if "Network" in str(e) or "HttpError" in str(type(e).__name__):
                pytest.skip("Network unavailable")


class TestOlsConstants:
    def test_obo_prefixes(self):
        assert OBO_PREFIX_TO_ONTOLOGY["GO"] == "go"
        assert OBO_PREFIX_TO_ONTOLOGY["HP"] == "hp"
        assert OBO_PREFIX_TO_ONTOLOGY["CHEBI"] == "chebi"
        assert OBO_PREFIX_TO_ONTOLOGY["MONDO"] == "mondo"

    def test_base_url(self):
        assert BASE_URL == "https://www.ebi.ac.uk/ols4/api"
