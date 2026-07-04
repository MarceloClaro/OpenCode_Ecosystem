#!/usr/bin/env python3
"""TDD — R45 Fase B: ASDE Pipeline (SPEC-058) — 12 CTs"""

import json
from pathlib import Path
from datetime import datetime

import pytest

REPO = Path(__file__).resolve().parent.parent
NEXUS = REPO / "nexus"


def _import_asde():
    try:
        from nexus import asde_pipeline as asde
        return asde
    except (ImportError, ModuleNotFoundError):
        pytest.skip("nexus.asde_pipeline not implemented")


class TestFaseB_ASDE:

    def test_B01_asde_imports(self):
        """B01: Modulo ASDE importa sem erros."""
        asde = _import_asde()
        assert hasattr(asde, "IdeaGenerator"), "IdeaGenerator missing"
        assert hasattr(asde, "OntologyGraph"), "OntologyGraph missing"
        assert hasattr(asde, "MultiAgentCritic"), "MultiAgentCritic missing"
        assert hasattr(asde, "ExperimentPlanner"), "ExperimentPlanner missing"
        assert hasattr(asde, "ResultSynthesizer"), "ResultSynthesizer missing"
        assert hasattr(asde, "ASDEPipeline"), "ASDEPipeline missing"

    def test_B02_idea_generator(self):
        """B02: IdeaGenerator gera ideias a partir de problema."""
        asde = _import_asde()
        gen = asde.IdeaGenerator()
        ideas = gen.generate(
            problem="Como reduzir custo computacional em agentes LLM?"
        )
        assert isinstance(ideas, list)
        assert len(ideas) >= 3, f"Expected >=3 ideas, got {len(ideas)}"
        for idea in ideas:
            assert "title" in idea
            assert "description" in idea
            assert "score" in idea
            assert 0 <= idea["score"] <= 1

    def test_B03_ontology_graph(self):
        """B03: OntologyGraph cria nos e conexoes."""
        asde = _import_asde()
        graph = asde.OntologyGraph()
        graph.add_node("LLM", {"domain": "AI"})
        graph.add_node("raciocinio", {"domain": "cognicao"})
        graph.add_node("eficiencia", {"domain": "engenharia"})
        graph.add_edge("LLM", "raciocinio", relation="requer")
        graph.add_edge("raciocinio", "eficiencia", relation="impacta")

        nodes = graph.get_nodes()
        edges = graph.get_edges()
        assert len(nodes) >= 3
        assert len(edges) >= 2
        # Find paths
        paths = graph.find_paths("LLM", "eficiencia", max_hops=3)
        assert len(paths) >= 1

    def test_B04_multi_agent_critic(self):
        """B04: MultiAgentCritic avalia hipotese."""
        asde = _import_asde()
        critic = asde.MultiAgentCritic()
        hypothesis = "Agentes LLM podem ser otimizados com poda seletiva de atencao."
        result = critic.review(hypothesis)
        assert isinstance(result, dict)
        assert "scientist1" in result
        assert "scientist2" in result
        assert "critic" in result
        assert "planner" in result
        # Each agent provides a review
        for agent in ["scientist1", "scientist2", "critic", "planner"]:
            assert "review" in result[agent]
            assert "sentiment" in result[agent]
            assert result[agent]["sentiment"] in ["positive", "negative", "neutral"]

    def test_B05_experiment_planner(self):
        """B05: ExperimentPlanner cria plano."""
        asde = _import_asde()
        planner = asde.ExperimentPlanner()
        plan = planner.plan(
            hypothesis="Poda seletiva reduz custo em 30% sem perda de acuracia."
        )
        assert isinstance(plan, dict)
        assert "scope" in plan
        assert "steps" in plan
        assert "metrics" in plan
        assert "resources" in plan
        assert len(plan["steps"]) >= 1
        assert len(plan["metrics"]) >= 1

    def test_B06_result_synthesizer(self):
        """B06: ResultSynthesizer gera relatorio IMRaD."""
        asde = _import_asde()
        synth = asde.ResultSynthesizer()
        report = synth.synthesize(
            title="Otimizacao de Agentes LLM",
            hypothesis="Poda seletiva reduz custo em 30%.",
            results={"custo_reducao": 0.32, "acuracia": 0.97},
        )
        assert isinstance(report, dict)
        assert report.get("title") == "Otimizacao de Agentes LLM"
        sections = report.get("sections", [])
        section_titles = [s["title"] for s in sections]
        for required in ["Introduction", "Methods", "Results", "Discussion"]:
            assert required in section_titles, f"Missing IMRaD section: {required}"

    def test_B07_asde_full_pipeline(self):
        """B07: Pipeline completo executa."""
        asde = _import_asde()
        pipeline = asde.ASDEPipeline()
        result = pipeline.run(
            problem="Como reduzir custo computacional de agentes LLM?",
        )
        assert isinstance(result, dict)
        assert "ideas" in result
        assert "ontology" in result
        assert "critique" in result
        assert "plan" in result
        assert "report" in result
        assert len(result["ideas"]) >= 3

    def test_B08_asde_report_structure(self):
        """B08: Relatorio tem secoes ABNT completas."""
        asde = _import_asde()
        synth = asde.ResultSynthesizer()
        report = synth.synthesize(
            title="Teste Estrutura ABNT",
            hypothesis="Hipotese de teste.",
            results={"resultado": 0.95},
        )
        sections = report.get("sections", [])
        # Verify section depth and structure
        for section in sections:
            assert "title" in section
            assert "content" in section
            assert len(section["content"]) > 0

    def test_B09_asde_ontology_persistence(self):
        """B09: Ontologia persiste dados corretamente."""
        asde = _import_asde()
        graph = asde.OntologyGraph()
        graph.add_node("A", {"tipo": "conceito"})
        graph.add_node("B", {"tipo": "metodo"})
        graph.add_node("C", {"tipo": "teoria"})
        graph.add_edge("A", "B", relation="usa")
        graph.add_edge("B", "C", relation="implementa")

        snapshot = graph.snapshot()
        assert isinstance(snapshot, dict)
        assert "nodes" in snapshot
        assert "edges" in snapshot
        assert len(snapshot["nodes"]) >= 3
        assert len(snapshot["edges"]) >= 2

    def test_B10_asde_idea_scoring(self):
        """B10: Ideias tem score replicavel."""
        asde = _import_asde()
        gen = asde.IdeaGenerator()
        ideas1 = gen.generate("Problema de teste para reproducibilidade.")
        ideas2 = gen.generate("Problema de teste para reproducibilidade.")
        # Same problem should generate same number of ideas
        assert len(ideas1) == len(ideas2)
        # Scores should be deterministic
        for i1, i2 in zip(ideas1, ideas2):
            assert i1["score"] == i2["score"], f"Scores differ: {i1['score']} vs {i2['score']}"

    def test_B11_asde_critic_diversity(self):
        """B11: Criticas de agentes diferentes."""
        asde = _import_asde()
        critic = asde.MultiAgentCritic()
        hypothesis = "Agentes multi-nivel superam agentes single-nivel em tarefas complexas."
        result = critic.review(hypothesis)

        # Scientists should have different perspectives
        s1_sentiment = result["scientist1"]["sentiment"]
        s2_sentiment = result["scientist2"]["sentiment"]
        # They should not both be 'neutral'
        assert not (s1_sentiment == "neutral" and s2_sentiment == "neutral")

        # Critic should evaluate both sides
        assert "synthesis" in result["critic"]
        assert len(result["critic"]["synthesis"]) > 0

    def test_B12_asde_end_to_end(self):
        """B12: Problema → Relatorio completo."""
        asde = _import_asde()
        pipeline = asde.ASDEPipeline()
        result = pipeline.run(
            problem="Qual o impacto da arquitetura multi-agente na eficiencia cognitiva?",
        )
        # Full report
        report = result["report"]
        assert "title" in report
        assert "sections" in report

        # All IMRaD sections present
        section_titles = [s["title"] for s in report["sections"]]
        for required in ["Introduction", "Methods", "Results", "Discussion"]:
            assert required in section_titles

        # Ideas linked to report
        assert len(result["ideas"]) >= 3
        # Ontology has content
        assert len(result["ontology"]["nodes"]) >= 3
        # Critique completed
        assert "critique" in result
        # Plan generated
        assert len(result["plan"]["steps"]) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
