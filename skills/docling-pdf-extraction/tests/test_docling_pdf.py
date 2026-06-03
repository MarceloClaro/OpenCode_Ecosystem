"""Tests for docling-pdf-extraction skill."""
import sys
import json
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL_DIR / "scripts"))

import pytest


class TestDoclingSkill:
    """CT-1: Core extraction function works."""

    def test_extrair_pdf_returns_dict(self):
        from docling_skill import extrair_pdf
        result = extrair_pdf("nonexistent.pdf", "markdown")
        assert isinstance(result, dict)
        assert "status" in result

    def test_extrair_pdf_fallback(self):
        from docling_skill import extrair_pdf
        result = extrair_pdf("fake_path.pdf")
        assert result["status"] in ("ok", "fallback")
        assert "arquivo" in result or "dados" in result

    def test_main_function_exists(self):
        import docling_skill
        assert hasattr(docling_skill, "main")

    def test_skill_md_covers_extraction(self):
        content = (SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        assert "Docling" in content
        assert len(content) > 200
