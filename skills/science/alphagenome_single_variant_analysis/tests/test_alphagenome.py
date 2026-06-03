import pytest, sys, os, json, tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from analyze_ism import _reverse_complement
from resolve_ontology_terms import normalize_and_split, search_ontology


class TestReverseComplement:
    def test_standard_bases(self):
        assert _reverse_complement("ACGT") == "ACGT"

    def test_mixed_case(self):
        assert _reverse_complement("aCgT") == "AcGt"

    def test_empty_string(self):
        assert _reverse_complement("") == ""


class TestNormalizeAndSplit:
    def test_simple_text(self):
        result = normalize_and_split("Liver Tissue")
        assert "liver" in result
        assert "tissue" in result

    def test_special_characters(self):
        result = normalize_and_split("UBERON:0002107")
        assert "uberon" in result
        assert "0002107" in result

    def test_short_words_filtered(self):
        result = normalize_and_split("a bc def gh")
        assert "def" in result
        assert "bc" not in result
        assert "a" not in result


class TestSearchOntology:
    def setup_method(self):
        self.mapping = {
            "UBERON:0002107": {
                "biosample": {"name": "liver", "type": "tissue"},
                "assays": {"RNA-seq": {"tracks": ["RNA_SEQ"]}},
            },
            "EFO:0001187": {
                "biosample": {"name": "HepG2 cell line", "type": "cell_line"},
                "assays": {"DNASE": {"tracks": ["DNASE"]}},
            },
        }

    def test_exact_match(self):
        results = search_ontology("liver", self.mapping, limit=5)
        assert len(results) > 0
        assert results[0]["curie"] == "UBERON:0002107"

    def test_no_match(self):
        results = search_ontology("zzz_nonexistent", self.mapping, limit=5)
        assert results == []

    def test_empty_query(self):
        results = search_ontology("", self.mapping, limit=5)
        assert isinstance(results, list)
        assert len(results) == 0
