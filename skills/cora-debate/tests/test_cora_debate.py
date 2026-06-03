"""Tests for cora-debate skill."""
import sys
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "servers"))

import pytest


class TestCoraVerifier:
    """CT-1: MCP handler verifiers work."""

    @pytest.fixture
    def handler(self):
        from cora_verifier import MCPHandler
        return MCPHandler()

    def test_health_check(self, handler):
        result = handler.handle_health({})
        assert result.get("server") == "running"

    def test_list_verifiers(self, handler):
        result = handler.handle_list({})
        assert result.get("count", 0) >= 7

    def test_v1_dimensional_analysis_pass(self, handler):
        result = handler.handle_v1({"equation": "F = m * a"})
        assert result.get("passed") is True

    def test_v1_dimensional_analysis_fail(self, handler):
        result = handler.handle_v1({"equation": "F = m"})
        assert result.get("passed") is False


class TestValidateModule:
    """CT-2: validate_cora.py imports and runs."""

    def test_validate_cora_exists(self):
        validate_path = SKILL_DIR / "validate_cora.py"
        assert validate_path.exists()

    def test_skill_md_structure(self):
        skill_md = SKILL_DIR / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8")
        assert "P19" in content
        assert "V1" in content or "V7" in content
        assert "Q-Score" in content

    def test_verifier_server_syntax(self):
        # Verify cora_verifier.py compiles
        import py_compile
        py_compile.compile(str(SKILL_DIR / "servers" / "cora_verifier.py"), doraise=True)
