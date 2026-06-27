"""
TDD Test Suite — QualitativeCoder Categorizer
SPEC-048 | Ciclo R27

Testes de categorização temática e clustering.
"""
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestCategorizer:
    """CTs do módulo de categorização temática."""

    def test_import_categorizer(self):
        """CT-016: Categorizer deve ser importável."""
        from qualitative_coder.core.categorizer import Categorizer
        assert Categorizer is not None

    def test_categorizer_init(self):
        """CT-017: Categorizer deve inicializar com método padrão."""
        from qualitative_coder.core.categorizer import Categorizer
        cat = Categorizer()
        assert cat.method == "tfidf"

    def test_categorize_returns_list(self):
        """CT-018: categorize() deve retornar lista de categorias."""
        from qualitative_coder.core.categorizer import Categorizer
        cat = Categorizer()
        codes = [
            {"code": "resistencia", "span": (0, 10), "confidence": 0.9},
            {"code": "mudanca", "span": (11, 17), "confidence": 0.85},
            {"code": "resistencia", "span": (30, 40), "confidence": 0.92},
        ]
        result = cat.categorize(codes)
        assert isinstance(result, list)
        assert len(result) > 0

    def test_categorize_returns_dicts(self):
        """CT-019: Categoria deve conter category, codes, frequency."""
        from qualitative_coder.core.categorizer import Categorizer
        cat = Categorizer()
        codes = [
            {"code": "resistencia", "span": (0, 10), "confidence": 0.9},
            {"code": "resistencia", "span": (30, 40), "confidence": 0.92},
            {"code": "mudanca", "span": (11, 17), "confidence": 0.85},
        ]
        result = cat.categorize(codes)
        for item in result:
            assert "category" in item
            assert "codes" in item
            assert "frequency" in item

    def test_categorize_frequency_count(self):
        """CT-020: Frequency deve contar ocorrências por categoria."""
        from qualitative_coder.core.categorizer import Categorizer
        cat = Categorizer()
        codes = [
            {"code": "resistencia", "span": (0, 10), "confidence": 0.9},
            {"code": "resistencia", "span": (30, 40), "confidence": 0.92},
            {"code": "resistencia", "span": (60, 70), "confidence": 0.88},
            {"code": "mudanca", "span": (11, 17), "confidence": 0.85},
        ]
        result = cat.categorize(codes)
        resistencia_cat = [c for c in result if "resistencia" in c["category"].lower()]
        assert len(resistencia_cat) == 1
        assert resistencia_cat[0]["frequency"] >= 3

    def test_categorize_empty_codes(self):
        """CT-021: Lista vazia de códigos deve retornar categorias vazias."""
        from qualitative_coder.core.categorizer import Categorizer
        cat = Categorizer()
        result = cat.categorize([])
        assert result == []

    def test_categorize_thematic_method(self):
        """CT-022: Método thematic deve usar BERTopic-like."""
        from qualitative_coder.core.categorizer import Categorizer
        cat = Categorizer(method="thematic")
        assert cat.method == "thematic"

    def test_cluster_documents(self):
        """CT-023: cluster() deve agrupar documentos similares."""
        from qualitative_coder.core.categorizer import Categorizer
        cat = Categorizer()
        docs = [
            "A resistência dos docentes é um problema.",
            "Os professores resistem às mudanças.",
            "O clima organizacional é bom.",
        ]
        result = cat.cluster(docs, n_clusters=2)
        assert isinstance(result, list)
        assert len(result) == len(docs)

    def test_get_top_themes(self):
        """CT-024: get_top_themes() deve retornar temas ordenados."""
        from qualitative_coder.core.categorizer import Categorizer
        cat = Categorizer()
        codes = [
            {"code": "resistencia", "span": (0, 10), "confidence": 0.9},
            {"code": "resistencia", "span": (30, 40), "confidence": 0.92},
            {"code": "mudanca", "span": (11, 17), "confidence": 0.85},
        ]
        cat.categorize(codes)
        themes = cat.get_top_themes(n=5)
        assert isinstance(themes, list)
        assert len(themes) <= 5
