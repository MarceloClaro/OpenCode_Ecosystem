import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from mmseqs2_search import parse_a3m, FASTA_COLUMNS
from uniprot_blast import ALLOWED_DATABASES


class TestMMseqs2Parse:
    def setup_method(self):
        self.temp_dir = None

    def test_fasta_columns(self):
        assert "target" in FASTA_COLUMNS
        assert "e_value" in FASTA_COLUMNS
        assert "identity" in FASTA_COLUMNS
        assert len(FASTA_COLUMNS) == 10

    def test_parse_a3m_empty(self):
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=".a3m", mode="w", delete=False)
        tmp.write("")
        tmp.close()
        try:
            hits = parse_a3m(tmp.name, 100)
            assert isinstance(hits, list)
            assert len(hits) == 0
        finally:
            os.unlink(tmp.name)

    def test_parse_a3m_with_hits(self):
        import tempfile
        tmp = tempfile.NamedTemporaryFile(suffix=".a3m", mode="w", delete=False)
        tmp.write(
            ">P04637 500.0 0.95 0.0 1 393 393 1 393 393\n"
            "AAAA\n"
            ">P12345 300.0 0.80 1e-10 1 200 200 1 200 200\n"
            "CCCC\n"
        )
        tmp.close()
        try:
            hits = parse_a3m(tmp.name, 393)
            assert isinstance(hits, list)
            assert len(hits) >= 1
            hit = hits[0]
            assert "target_id" in hit
            assert "e_value" in hit
            assert "q_cov" in hit
        finally:
            os.unlink(tmp.name)


class TestBlastConstants:
    def test_allowed_databases(self):
        assert "uniprotkb" in ALLOWED_DATABASES
        assert "uniprotkb_swissprot" in ALLOWED_DATABASES
        assert "pdb" in ALLOWED_DATABASES

    def test_human_database_available(self):
        assert "uniprotkb_human" in ALLOWED_DATABASES
