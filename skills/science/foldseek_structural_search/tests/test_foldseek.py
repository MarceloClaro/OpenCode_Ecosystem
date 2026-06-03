import pytest
import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from search import build_multipart_payload, ALLOWED_DATABASES, MAX_ALIGNMENT_HITS


class TestFoldseekConstants:
    def test_allowed_databases_not_empty(self):
        assert isinstance(ALLOWED_DATABASES, list)
        assert len(ALLOWED_DATABASES) > 0
        assert "pdb100" in ALLOWED_DATABASES
        assert "afdb50" in ALLOWED_DATABASES

    def test_max_alignment_hits(self):
        assert MAX_ALIGNMENT_HITS == 300


class TestFoldseekPayload:
    def test_build_multipart_payload_returns_bytes(self):
        fields = {"mode": "3diaa", "database[]": ["pdb100"]}
        with tempfile.NamedTemporaryFile(
            suffix=".cif", mode="w", delete=False
        ) as f:
            f.write("data_test_structure\n")
            temp_path = f.name
        try:
            files = {"q": temp_path}
            boundary, body = build_multipart_payload(fields, files)
            assert isinstance(body, (bytes, bytearray))
            assert len(body) > 0
            assert boundary.encode() in body
        finally:
            os.unlink(temp_path)

    def test_build_multipart_missing_file(self):
        with pytest.raises(FileNotFoundError):
            build_multipart_payload({}, {"q": "/nonexistent/path.cif"})
