import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from ncbi_fetch import (
    parse_fasta, translate_dna, _CODON_TABLE, efetch, esearch
)


class TestParseFasta:
    def test_parse_single_entry(self):
        text = ">P04637 test\nMEEPQSDPSV\n"
        entries = parse_fasta(text)
        assert len(entries) == 1
        assert entries[0][0] == ">P04637 test"
        assert entries[0][1] == "MEEPQSDPSV"

    def test_parse_multiple_entries(self):
        text = ">seq1\nAAAA\n>seq2\nCCCC\n"
        entries = parse_fasta(text)
        assert len(entries) == 2

    def test_parse_empty_returns_empty_list(self):
        assert parse_fasta(None) == []
        assert parse_fasta("") == []


class TestTranslateDna:
    def test_translate_simple_sequence(self):
        assert translate_dna("ATG") == "M"

    def test_translate_longer_sequence(self):
        seq = "ATGGCC"
        result = translate_dna(seq)
        assert len(result) == 2

    def test_translate_with_unknown_codon(self):
        result = translate_dna("ATGNNG")
        assert "X" in result

    def test_translate_short_sequence(self):
        result = translate_dna("ATG")
        assert result == "M"


class TestNcbiEfetch:
    def test_efetch_returns_fasta_or_none(self):
        try:
            result = efetch("protein", "P04637")
        except Exception:
            pytest.skip("Network unavailable")
        assert result is None or isinstance(result, str)

    def test_esearch_returns_tuple(self):
        try:
            ids, count = esearch("protein", "BRCA1[gene]", retmax=3)
        except Exception:
            pytest.skip("Network unavailable")
        assert isinstance(ids, list)
        assert isinstance(count, int)
