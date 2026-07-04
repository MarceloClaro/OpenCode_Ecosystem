#!/usr/bin/env python3
"""TDD — R45 Fase D: Pipeline Acadêmico Completo — 12 CTs"""

import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
NEXUS = REPO / "nexus"


def _import_pipeline():
    try:
        from nexus import academic_pipeline as ap
        return ap
    except (ImportError, ModuleNotFoundError):
        pytest.skip("nexus.academic_pipeline not implemented")


class TestFaseD_Academic:

    def test_D01_pipeline_imports(self):
        """D01: Orquestrador importa sem erros."""
        ap = _import_pipeline()
        assert hasattr(ap, "AcademicPipeline"), "AcademicPipeline missing"
        assert hasattr(ap, "SeekerSimulator"), "SeekerSimulator missing"
        assert hasattr(ap, "PeerReviewSimulator"), "PeerReviewSimulator missing"
        assert hasattr(ap, "TSACCorrector"), "TSACCorrector missing"
        assert hasattr(ap, "QualisA1Auditor"), "QualisA1Auditor missing"
        assert hasattr(ap, "ExportManager"), "ExportManager missing"
        assert hasattr(ap, "ManusEvolve"), "ManusEvolve missing"

    def test_D02_seeker_trigger(self):
        """D02: SEEKER e acionado."""
        ap = _import_pipeline()
        seeker = ap.SeekerSimulator()
        result = seeker.search(
            topic="Otimizacao de agentes cognitivos com multi-agente"
        )
        assert isinstance(result, dict)
        assert "papers" in result
        assert len(result["papers"]) >= 3
        for paper in result["papers"][:3]:
            assert "title" in paper
            assert "source" in paper
            assert "doi" in paper

    def test_D03_maswos_orchestration(self):
        """D03: MASWOS orquestrado."""
        ap = _import_pipeline()
        pipeline = ap.AcademicPipeline()
        result = pipeline.run_maswos(
            topic="Arquitetura multi-agente para eficiencia cognitiva"
        )
        assert isinstance(result, dict)
        assert "phases" in result
        assert len(result["phases"]) >= 3
        assert "draft" in result
        assert len(result["draft"]) > 100

    def test_D04_peer_review(self):
        """D04: Revisao simulada."""
        ap = _import_pipeline()
        review = ap.PeerReviewSimulator()
        draft = (
            "Este artigo propoe uma arquitetura multi-agente "
            "para otimizacao de agentes cognitivos. "
            "Os resultados mostram melhoria de 30% na eficiencia."
        )
        result = review.evaluate(draft)
        assert isinstance(result, dict)
        assert "reviewers" in result
        assert len(result["reviewers"]) >= 3
        for reviewer in result["reviewers"]:
            assert "name" in reviewer
            assert "score" in reviewer
            assert "comments" in reviewer
        assert "average_score" in result
        assert 0 <= result["average_score"] <= 100

    def test_D05_tsac_correction(self):
        """D05: Correcao TSAC aplicada."""
        ap = _import_pipeline()
        corrector = ap.TSACCorrector()
        text = (
            "Portanto, concluimos que a abordagem proposta e "
            "fundamental para o avanco da area."
        )
        result = corrector.correct(text)
        assert isinstance(result, dict)
        assert "original" in result
        assert "corrected" in result
        assert "changes" in result
        # Should detect and remove AI writing patterns
        assert result["original"] != result["corrected"]

    def test_D06_qualis_audit(self):
        """D06: Auditoria Qualis A1."""
        ap = _import_pipeline()
        auditor = ap.QualisA1Auditor()
        result = auditor.audit(
            title="Otimizacao Cognitiva Multi-Agente",
            abstract="Este estudo propoe uma nova arquitetura.",
            sections=["Intro", "Methods", "Results", "Discussion"],
            references=["doi:10.1000/test"],
        )
        assert isinstance(result, dict)
        assert "score" in result
        assert "criteria" in result
        assert 0 <= result["score"] <= 100

    def test_D07_export_latex(self):
        """D07: Exportacao LaTeX."""
        ap = _import_pipeline()
        export = ap.ExportManager()
        result = export.to_latex(
            title="Artigo Teste",
            author="Autor Teste",
            sections=[
                {"title": "Intro", "content": "Introducao."},
                {"title": "Conclusao", "content": "Conclusao."},
            ],
        )
        assert isinstance(result, str)
        assert r"\documentclass" in result
        assert r"\title{Artigo Teste}" in result
        assert r"\section{Intro}" in result

    def test_D08_export_pdf(self):
        """D08: Exportacao PDF."""
        ap = _import_pipeline()
        export = ap.ExportManager()
        result = export.verify_export_ready(
            sections=[
                {"title": "Intro", "content": "OK"},
                {"title": "Conclusao", "content": "OK"},
            ],
            references=["doi:10.1000/test"],
        )
        assert isinstance(result, dict)
        assert "ready" in result
        assert "issues" in result
        assert isinstance(result["ready"], bool)

    def test_D09_manus_evolve_learn(self):
        """D09: Aprendizado do ciclo."""
        ap = _import_pipeline()
        evolve = ap.ManusEvolve()
        cycle_data = {
            "topic": "Otimizacao de agentes",
            "score_initial": 75,
            "score_final": 92,
            "improvements": ["TSAC correction", "Peer review feedback"],
            "duration_seconds": 120,
        }
        insight = evolve.learn(cycle_data)
        assert isinstance(insight, dict)
        assert "pattern" in insight
        assert "recommendation" in insight
        assert len(insight["pattern"]) > 0

    def test_D10_full_pipeline_short(self):
        """D10: Pipeline completo (problema → rascunho)."""
        ap = _import_pipeline()
        pipeline = ap.AcademicPipeline()
        result = pipeline.run_full(
            topic="Impacto de arquiteturas multi-agente na eficiencia cognitiva",
        )
        assert isinstance(result, dict)
        assert "seeker" in result
        assert "maswos" in result
        assert "peer_review" in result
        assert "tsac" in result
        assert "qualis" in result
        assert "export" in result
        assert "evolve" in result
        # Final score
        assert "final_score" in result

    def test_D11_citation_validation(self):
        """D11: Validacao ABNT das citacoes."""
        ap = _import_pipeline()
        auditor = ap.QualisA1Auditor()
        result = auditor.validate_references([
            {"doi": "10.1000/test", "author": "Autor, A.", "year": 2023},
            {"doi": "10.2000/test2", "author": "Autor, B.", "year": 2024},
        ])
        assert isinstance(result, dict)
        assert "valid" in result
        assert "count" in result
        assert result["count"] >= 1

    def test_D12_reproducibility_check(self):
        """D12: Verificacao de reprodutibilidade."""
        ap = _import_pipeline()
        pipeline = ap.AcademicPipeline()
        result = pipeline.check_reproducibility(
            topic="Otimizacao cognitiva",
            params={"model": "gpt-4", "temperature": 0.7},
        )
        assert isinstance(result, dict)
        assert "reproducible" in result
        assert "factors" in result
        assert isinstance(result["reproducible"], bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
