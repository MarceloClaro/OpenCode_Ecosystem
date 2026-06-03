import pytest
import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from msa_align import _prepare_payload


class TestMSAPayload:
    def test_prepare_payload_returns_bytes(self):
        payload = _prepare_payload(
            "user@example.com",
            "Test MSA",
            ">seq1\nAAAA\n>seq2\nCCCC\n",
        )
        assert isinstance(payload, bytes)
        assert len(payload) > 0

    def test_prepare_payload_contains_email(self):
        payload = _prepare_payload(
            "user@example.com",
            "Test MSA",
            ">seq1\nAAAA\n>seq2\nCCCC\n",
        )
        assert b"user%40example.com" in payload

    def test_prepare_payload_contains_sequences(self):
        payload = _prepare_payload(
            "user@example.com",
            "Test MSA",
            ">seq1\nAAAA\n>seq2\nCCCC\n",
        )
        assert b"AAAA" in payload or b"seq1" in payload


class TestMSAConstants:
    def test_importable(self):
        from msa_align import _POLLING_TIMEOUT_SECS
        assert _POLLING_TIMEOUT_SECS == 15 * 60
