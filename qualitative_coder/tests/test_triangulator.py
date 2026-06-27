"""
TDD Test Suite — QualitativeCoder Triangulator
SPEC-048 | Ciclo R27

Testes de triangulação de métodos e fontes.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestTriangulator:
    """CTs do módulo de triangulação."""

    def test_import_triangulator(self):
        """CT-025: Triangulator deve ser importável."""
        from qualitative_coder.core.triangulator import Triangulator
        assert Triangulator is not None

    def test_triangulator_init(self):
        """CT-026: Triangulator deve inicializar corretamente."""
        from qualitative_coder.core.triangulator import Triangulator
        tri = Triangulator()
        assert tri is not None

    def test_triangulate_returns_dict(self):
        """CT-027: triangulate() deve retornar dict com convergence, divergence, gaps."""
        from qualitative_coder.core.triangulator import Triangulator
        tri = Triangulator()
        data_quant = {"metrica1": 0.8, "metrica2": 0.6}
        data_qual = [
            {"code": "qual1", "confidence": 0.9},
            {"code": "qual2", "confidence": 0.7},
        ]
        result = tri.triangulate(data_quant, data_qual)
        assert isinstance(result, dict)
        assert "convergence" in result
        assert "divergence" in result
        assert "gaps" in result

    def test_convergence_range(self):
        """CT-028: convergence deve estar entre 0.0 e 1.0."""
        from qualitative_coder.core.triangulator import Triangulator
        tri = Triangulator()
        result = tri.triangulate({"m1": 0.5}, [{"code": "c1", "confidence": 0.8}])
        assert 0.0 <= result["convergence"] <= 1.0

    def test_divergence_is_list(self):
        """CT-029: divergence deve ser lista de pontos de divergência."""
        from qualitative_coder.core.triangulator import Triangulator
        tri = Triangulator()
        result = tri.triangulate({"m1": 0.2}, [{"code": "c1", "confidence": 0.9}])
        assert isinstance(result["divergence"], list)

    def test_gaps_is_list(self):
        """CT-030: gaps deve ser lista de lacunas identificadas."""
        from qualitative_coder.core.triangulator import Triangulator
        tri = Triangulator()
        result = tri.triangulate({}, [])
        assert isinstance(result["gaps"], list)

    def test_triangulate_with_methods(self):
        """CT-031: Deve aceitar múltiplos métodos de triangulação."""
        from qualitative_coder.core.triangulator import Triangulator
        tri = Triangulator()
        result = tri.triangulate(
            {"m1": 0.5},
            [{"code": "c1", "confidence": 0.8}],
            method="convergence"
        )
        assert result["convergence"] >= 0.0

    def test_triangulate_empty_data(self):
        """CT-032: Dados vazios devem retornar gaps preenchidos."""
        from qualitative_coder.core.triangulator import Triangulator
        tri = Triangulator()
        result = tri.triangulate({}, [])
        assert len(result["gaps"]) > 0
