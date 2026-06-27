"""
TDD Test Suite — QualitativeCoder Core
SPEC-048 | Ciclo R27 | Autor: Marcelo Claro

Estes testes são escritos ANTES da implementação (Red Phase).
Cada CT valida um requisito específico da especificação.
"""
import pytest
import sys
import os

# Adicionar caminho do módulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestQualitativeCoderInit:
    """CTs de inicialização do QualitativeCoder."""

    def test_import_exists(self):
        """CT-001: Módulo qualitative_coder deve ser importável."""
        from qualitative_coder import QualitativeCoder
        assert QualitativeCoder is not None

    def test_init_default_language(self):
        """CT-002: Idioma padrão deve ser 'pt-br'."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        assert coder.language == "pt-br"

    def test_init_custom_language(self):
        """CT-003: Deve aceitar idioma customizado."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder(language="en")
        assert coder.language == "en"

    def test_init_creates_empty_codebook(self):
        """CT-004: Codebook deve iniciar vazio."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        assert coder.codebook == {}

    def test_init_creates_empty_categories(self):
        """CT-005: Categorias devem iniciar vazias."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        assert coder.categories == []


class TestQualitativeCoderCode:
    """CTs de codificação qualitativa."""

    def test_code_returns_list(self):
        """CT-006: code() deve retornar lista de códigos."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        result = coder.code("A resistência dos docentes é um problema.")
        assert isinstance(result, list)

    def test_code_returns_dicts(self):
        """CT-007: Cada código deve ser dict com code, span, confidence."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        result = coder.code("A resistência dos docentes é um problema.")
        assert len(result) > 0
        for item in result:
            assert "code" in item
            assert "span" in item
            assert "confidence" in item

    def test_code_confidence_range(self):
        """CT-008: Confidence deve estar entre 0.0 e 1.0."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        result = coder.code("A resistência dos docentes é um problema.")
        for item in result:
            assert 0.0 <= item["confidence"] <= 1.0

    def test_code_span_valid(self):
        """CT-009: Span deve ser tupla (start, end) dentro do texto."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        text = "A resistência dos docentes é um problema."
        result = coder.code(text)
        for item in result:
            start, end = item["span"]
            assert 0 <= start < end <= len(text)

    def test_code_axial_method(self):
        """CT-010: Método axial deve gerar códigos relacionais."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        result = coder.code("A resistência dos docentes causou atrasos.", method="axial")
        assert len(result) >= 1
        # Axial deve identificar relação causal
        codes_str = " ".join([r["code"] for r in result])
        assert any(kw in codes_str for kw in ["resistencia", "causa", "atraso", "relacao"])

    def test_code_open_method(self):
        """CT-011: Método open deve gerar códigos emergentes (sem compostos)."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        result = coder.code("A mudança metodológica é uma inovação.", method="open")
        # Open não deve gerar códigos compostos (com _)
        for r in result:
            assert "_" not in r["code"]
        assert len(result) >= 1

    def test_code_empty_text(self):
        """CT-012: Texto vazio deve retornar lista vazia."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        result = coder.code("")
        assert result == []


class TestQualitativeCoderCodebook:
    """CTs de gerenciamento de codebook."""

    def test_add_code(self):
        """CT-013: add_code deve adicionar código ao codebook."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        coder.add_code("resistencia_mudanca", description="Resistência a mudanças pedagógicas")
        assert "resistencia_mudanca" in coder.codebook

    def test_add_code_with_parent(self):
        """CT-014: add_code deve aceitar código pai (hierarquia)."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        coder.add_code("barreiras", description="Barreiras gerais")
        coder.add_code("resistencia", parent="barreiras", description="Resistência")
        assert coder.codebook["resistencia"]["parent"] == "barreiras"

    def test_codebook_export(self):
        """CT-015: export_codebook deve retornar dict serializável."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        coder.add_code("teste")
        exported = coder.export_codebook()
        assert isinstance(exported, dict)
        assert "teste" in exported
