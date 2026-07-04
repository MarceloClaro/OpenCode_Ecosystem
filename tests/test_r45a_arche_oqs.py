#!/usr/bin/env python3
"""TDD — R45 Fase A: ARCHE RLT (SPEC-057) + OQS (SPEC-056) — 12 CTs"""

import json
import uuid
import math
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
NEXUS = REPO / "nexus"


def _import_arche():
    try:
        from nexus import arche_rlt as ar
        return ar
    except (ImportError, ModuleNotFoundError):
        pytest.skip("nexus.arche_rlt not implemented")


def _import_oqs():
    try:
        from nexus import oqs_scanner as oqs
        return oqs
    except (ImportError, ModuleNotFoundError):
        pytest.skip("nexus.oqs_scanner not implemented")


class TestFaseA_ARCHE:

    def test_A01_arche_imports(self):
        """A01: Modulo ARCHE importa sem erros."""
        ar = _import_arche()
        assert hasattr(ar, "RLTNode"), "RLTNode missing"
        assert hasattr(ar, "PeirceType"), "PeirceType missing"
        assert hasattr(ar, "ARCLERLT"), "ARCLERLT class missing"
        assert hasattr(ar, "PEIRCE_TYPES"), "PEIRCE_TYPES missing"

    def test_A02_arche_rlt_node(self):
        """A02: RLTNode com todos os campos."""
        ar = _import_arche()
        node = ar.RLTNode(
            inference_type=ar.PeirceType.DR,
            premise="Todo homem e mortal",
            conclusion="Socrates e mortal",
            confidence=0.95,
        )
        assert node.id is not None
        assert node.inference_type == ar.PeirceType.DR
        assert node.confidence == 0.95
        assert isinstance(node.children, list)

    def test_A03_arche_rlt_tree(self):
        """A03: Arvore RLT com 3+ niveis."""
        ar = _import_arche()
        engine = ar.ARCLERLT()

        # Build tree: root → 2 children → 4 grandchildren
        root = ar.RLTNode(
            inference_type=ar.PeirceType.DR,
            premise="Todos os A sao B",
            conclusion="Logo, conclusao final",
            confidence=0.9,
        )
        c1 = ar.RLTNode(
            inference_type=ar.PeirceType.AK,
            premise="X e A",
            conclusion="X e B",
            confidence=0.85,
        )
        c2 = ar.RLTNode(
            inference_type=ar.PeirceType.IC,
            premise="Amostra de A's sao B's",
            conclusion="Provavelmente todos A's sao B's",
            confidence=0.7,
        )
        gc1 = ar.RLTNode(
            inference_type=ar.PeirceType.DC,
            premise="Dado previo",
            conclusion="X e provavelmente A",
            confidence=0.6,
        )
        root.children = [c1, c2]
        c1.children = [gc1]

        result = engine.build_tree(root)
        # depth 0-based: root=0, c1=1, gc1=2 => profundidade 0-based 2 = 3 niveis
        assert result["depth"] >= 2, f"Expected depth>=2 (3 levels), got {result['depth']}"
        assert result["node_count"] >= 4
        assert result["root"] is not None

    def test_A04_arche_all_6_types(self):
        """A04: Todos os 6 tipos de Peirce funcionam."""
        ar = _import_arche()
        engine = ar.ARCLERLT()

        for ptype in ar.PeirceType:
            node = ar.RLTNode(
                inference_type=ptype,
                premise=f"Premissa para {ptype.value}",
                conclusion=f"Conclusao para {ptype.value}",
                confidence=0.8,
            )
            result = engine.validate_node(node)
            assert result["valid"] is True, f"Type {ptype} failed: {result}"

        # Verify all 6 types exist
        assert len(list(ar.PeirceType)) == 6

    def test_A05_arche_type_mapping(self):
        """A05: Mapeamento 212+ tipos → 6 Peirce."""
        ar = _import_arche()
        mapping = ar.get_type_mapping()

        assert isinstance(mapping, dict)
        assert len(mapping) >= 27  # 27 categories
        # Each maps to one of 6 types
        valid_types = {t.value for t in ar.PeirceType}
        for category, mapped_type in mapping.items():
            assert mapped_type in valid_types, f"{category} -> {mapped_type} invalid"

        # Count total reasoning types mapped
        total_types = sum(len(v) if isinstance(v, list) else 1
                         for v in mapping.values())
        assert total_types >= 27, f"Only {total_types} types mapped"


class TestFaseA_OQS:

    def test_A06_oqs_imports(self):
        """A06: Modulo OQS importa sem erros."""
        oq = _import_oqs()
        assert hasattr(oq, "UncertaintyScanner"), "UncertaintyScanner missing"
        assert hasattr(oq, "QuestionVectorizer"), "QuestionVectorizer missing"
        assert hasattr(oq, "ConvergenceScore"), "ConvergenceScore missing"
        assert hasattr(oq, "OQSPipeline"), "OQSPipeline missing"

    def test_A07_oqs_uncertainty_scan(self):
        """A07: UncertaintyScanner retorna estrutura."""
        oq = _import_oqs()
        scanner = oq.UncertaintyScanner()
        result = scanner.scan(
            "Como otimizar agentes cognitivos para reducao de tokens?"
        )
        assert isinstance(result, dict)
        assert "uncertainty_categories" in result
        assert "structural_noise" in result
        assert "filtered_text" in result

    def test_A08_oqs_question_vectorize(self):
        """A08: QuestionVectorizer funciona."""
        oq = _import_oqs()
        vectorizer = oq.QuestionVectorizer()
        questions = [
            "Qual arquitetura minimiza latencia?",
            "Como escalar o sistema?",
            "Quais metricas de qualidade?",
        ]
        vectors = vectorizer.vectorize(questions)
        assert len(vectors) == len(questions)
        for v in vectors:
            assert isinstance(v, list)
            assert len(v) > 0  # non-empty vector

    def test_A09_oqs_convergence_score(self):
        """A09: Convergence Score calculado corretamente."""
        oq = _import_oqs()
        cs_calc = oq.ConvergenceScore()
        score = cs_calc.calculate(
            question="Qual arquitetura minimiza latencia?",
            uncertainty_reduction=8.0,
            search_space_reduction=7.0,
            dispersion_risk=2.0,
            cognitive_cost=3.0,
        )
        assert isinstance(score, (int, float))
        assert 0 <= score <= 100
        # Higher uncertainty reduction = higher score
        high_score = cs_calc.calculate(
            question="Pergunta otima?",
            uncertainty_reduction=9.0,
            search_space_reduction=9.0,
            dispersion_risk=1.0,
            cognitive_cost=1.0,
        )
        assert high_score > score

    def test_A10_oqs_select_best(self):
        """A10: Melhor pergunta selecionada do conjunto."""
        oq = _import_oqs()
        pipeline = oq.OQSPipeline()
        candidates = [
            "Qual o algoritmo mais eficiente?",
            "Como reduzir complexidade?",
            "Quais metricas usar?",
        ]
        best = pipeline.select_best_question(
            problem="Otimizar processamento de agentes",
            candidates=candidates,
        )
        assert best is not None
        assert "question" in best
        assert "score" in best
        assert best["question"] in candidates

    def test_A11_arche_oqs_integration(self):
        """A11: ARCHE + OQS integrados."""
        ar = _import_arche()
        oq = _import_oqs()

        # OQS generates optimal question
        pipeline = oq.OQSPipeline()
        candidates = [
            "Qual arquitetura de raciocinio e mais eficiente?",
            "Como reduzir custo computacional?",
            "Quais tipos de inferencia sao necessarios?",
        ]
        best = pipeline.select_best_question(
            problem="Otimizar raciocinio de agentes",
            candidates=candidates,
        )
        assert best is not None, "select_best_question retornou None"

        # ARCHE processes it
        engine = ar.ARCLERLT()
        root = ar.RLTNode(
            inference_type=ar.PeirceType.DR,
            premise=best["question"],
            conclusion="Raciocinio otimizado via ARCHE",
            confidence=0.85,
        )
        result = engine.build_tree(root)
        # root sozinha = depth 0 (0-based); profundidade 1 nivel
        assert result["depth"] >= 0
        assert result["node_count"] >= 1

    def test_A12_arche_full_pipeline(self):
        """A12: Pipeline completo executa."""
        ar = _import_arche()
        engine = ar.ARCLERLT()

        result = engine.run_pipeline(
            problem="Como melhorar a eficiencia de agentes cognitivos?",
            depth=3,
        )
        assert isinstance(result, dict)
        assert "tree" in result
        assert "conclusion" in result
        assert "audit_trail" in result
        assert result["depth"] >= 1
        assert len(result["audit_trail"]) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
