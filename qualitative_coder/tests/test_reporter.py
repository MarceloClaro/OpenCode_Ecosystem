"""
TDD Test Suite — QualitativeCoder Reporter
SPEC-048 | Ciclo R27

Testes de geração de relatórios.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestReporter:
    """CTs do módulo de relatórios."""

    def test_import_reporter(self):
        """CT-033: Reporter deve ser importável."""
        from qualitative_coder.core.reporter import Reporter
        assert Reporter is not None

    def test_reporter_init(self):
        """CT-034: Reporter deve inicializar corretamente."""
        from qualitative_coder.core.reporter import Reporter
        rep = Reporter()
        assert rep is not None

    def test_report_latex(self):
        """CT-035: report() com format=latex deve retornar string LaTeX."""
        from qualitative_coder.core.reporter import Reporter
        rep = Reporter()
        data = {
            "categories": [{"category": "teste", "codes": ["c1"], "frequency": 5}],
            "triangulation": {"convergence": 0.73, "divergence": [], "gaps": []},
        }
        result = rep.report(data, format="latex")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_report_markdown(self):
        """CT-036: report() com format=markdown deve retornar string MD."""
        from qualitative_coder.core.reporter import Reporter
        rep = Reporter()
        data = {
            "categories": [{"category": "teste", "codes": ["c1"], "frequency": 5}],
            "triangulation": {"convergence": 0.73, "divergence": [], "gaps": []},
        }
        result = rep.report(data, format="markdown")
        assert isinstance(result, str)
        assert "#" in result

    def test_report_json(self):
        """CT-037: report() com format=json deve retornar dict."""
        from qualitative_coder.core.reporter import Reporter
        rep = Reporter()
        data = {
            "categories": [{"category": "teste", "codes": ["c1"], "frequency": 5}],
            "triangulation": {"convergence": 0.73, "divergence": [], "gaps": []},
        }
        result = rep.report(data, format="json")
        assert isinstance(result, dict)

    def test_report_empty_data(self):
        """CT-038: Dados vazios devem gerar relatório mínimo."""
        from qualitative_coder.core.reporter import Reporter
        rep = Reporter()
        result = rep.report({"categories": [], "triangulation": {}}, format="latex")
        assert isinstance(result, str)
        assert len(result) > 0
