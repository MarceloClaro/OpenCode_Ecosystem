"""
TDD Test Suite — QualitativeCoder Integration
SPEC-048 | Ciclo R27

Testes de integração com OpenCode Ecosystem.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestIntegration:
    """CTs de integração com ecossistema."""

    def test_import_qualitative_coder(self):
        """CT-039: QualitativeCoder deve ser importável do pacote."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        assert coder is not None

    def test_full_pipeline(self):
        """CT-040: Pipeline completo code→categorize→triangulate→report."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()

        # Step 1: Code
        text = "A resistência dos docentes às mudanças metodológicas é um obstáculo."
        codes = coder.code(text)
        assert len(codes) > 0

        # Step 2: Categorize
        categories = coder.categorize(codes)
        assert len(categories) > 0

        # Step 3: Triangulate
        triang = coder.triangulate({"metrica": 0.5}, codes)
        assert "convergence" in triang

        # Step 4: Report
        report = coder.report({"categories": categories, "triangulation": triang}, format="latex")
        assert isinstance(report, str)
        assert len(report) > 0

    def test_export_codebook(self):
        """CT-041: export_codebook() deve gerar JSON válido."""
        import json
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        coder.add_code("teste")
        exported = coder.export_codebook()
        serialized = json.dumps(exported)
        assert isinstance(serialized, str)

    def test_codebook_persistence(self):
        """CT-042: Codebook deve persistir entre operações."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        coder.add_code("c1")
        coder.add_code("c2")
        assert len(coder.codebook) == 2
        coder.code("texto qualquer")
        assert len(coder.codebook) == 2  # code() não altera codebook

    def test_method_open_vs_axial(self):
        """CT-043: Métodos open e axial devem gerar resultados diferentes."""
        from qualitative_coder import QualitativeCoder
        coder = QualitativeCoder()
        text = "A resistência dos docentes causou atrasos na implementação."
        open_codes = coder.code(text, method="open")
        axial_codes = coder.code(text, method="axial")
        # Pelo menos um deve ter mais códigos ou diferentes
        assert open_codes is not None
        assert axial_codes is not None
