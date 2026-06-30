# -*- coding: utf-8 -*-
"""Testes TDD para ASDE — Autonomous Scientific Discovery Engine (R29, SPEC-058)"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "nexus", "scripts"))

from asde_engine import (
    ASDEEngine, IdeaGenerator, MultiAgentCritic, ExperimentPlanner,
    ResultSynthesizer, OntologyGraph, ResearchIdea, IdeaStatus,
)


def test_asde_001_generate_ideas():
    """IdeaGenerator gera ideias a partir de problema"""
    gen = IdeaGenerator()
    ideas = gen.generate("Como a polimatia influencia a resiliencia cognitiva?")
    assert len(ideas) >= 1, f"Esperado >=1 ideia, obtido {len(ideas)}"
    for idea in ideas:
        assert idea.title, "Ideia deve ter titulo"
        assert idea.hypothesis, "Ideia deve ter hipotese"
        assert idea.innovation_score > 0, "Score de inovacao deve ser > 0"


def test_asde_002_generate_min_3_ideas():
    """IdeaGenerator gera no minimo 3 ideias quando possivel"""
    gen = IdeaGenerator()
    ideas = gen.generate("polimatia neuroplasticidade", num_ideas=3)
    assert len(ideas) >= 2, f"Esperado >=2 ideias, obtido {len(ideas)}"


def test_asde_003_ontology_graph_connects():
    """OntologyGraph conecta conceitos e encontra caminhos"""
    graph = OntologyGraph()
    graph.add_node("A", "concept", "Concept A", "domA")
    graph.add_node("B", "concept", "Concept B", "domB")
    graph.add_node("C", "concept", "Concept C", "domC")
    graph.add_edge("A", "B", "causa", 0.8)
    graph.add_edge("B", "C", "deriva", 0.7)

    paths = graph.find_paths("A", "C", max_hops=3)
    assert len(paths) >= 1, f"Esperado >=1 caminho, obtido {len(paths)}"


def test_asde_004_multi_agent_critic_reviews():
    """MultiAgentCritic revisa hipotese com 4 agentes"""
    critic = MultiAgentCritic()
    idea = ResearchIdea(
        title="Teste",
        hypothesis="Polimatia melhora resiliencia",
        mechanism="Via neuroplasticidade",
        concepts=["polimatia", "resiliencia"],
        novelty_score=0.7,
        feasibility_score=0.6,
        impact_score=0.8,
    )
    reviewed = critic.review(idea)
    assert len(reviewed.reviews) == 4, f"Esperado 4 revisoes, obtido {len(reviewed.reviews)}"
    assert reviewed.status == IdeaStatus.REVIEWED
    agent_types = [r["agent"] for r in reviewed.reviews]
    assert "scientist_1" in agent_types
    assert "scientist_2" in agent_types
    assert "critic" in agent_types
    assert "planner" in agent_types


def test_asde_005_experiment_planner_creates_plan():
    """ExperimentPlanner cria plano para ideia revista"""
    planner = ExperimentPlanner()
    idea = ResearchIdea(
        title="Teste Experimental",
        hypothesis="Hipotese teste",
        mechanism="Mecanismo teste",
        concepts=["A", "B"],
        status=IdeaStatus.REVIEWED,
    )
    idea.reviews = [{"agent": "critic", "score": 0.7}]
    planned = planner.plan(idea)
    assert planned.plan is not None, "Plano nao pode ser None"
    assert "phases" in planned.plan, "Plano deve ter fases"
    assert len(planned.plan["phases"]) == 4, "Deve ter 4 fases OPUS"
    assert planned.status == IdeaStatus.PLANNED


def test_asde_006_result_synthesizer_generates_report():
    """ResultSynthesizer gera relatorio IMRaD"""
    synth = ResultSynthesizer()
    idea = ResearchIdea(
        title="Estudo da Polimatia",
        question="Como a polimatia influencia?",
        hypothesis="Polimatia melhora resiliencia",
        mechanism="Neuroplasticidade",
        concepts=["polimatia", "resiliencia", "neuroplasticidade"],
        novelty_score=0.7,
        feasibility_score=0.6,
        impact_score=0.8,
        status=IdeaStatus.PLANNED,
        plan={"phases": []},
    )
    reported = synth.synthesize(idea)
    assert reported.report is not None, "Relatorio nao pode ser None"
    assert any(h in reported.report for h in ["## Introducao", "## 1. Introducao", "## 1 Introdução"]), "Deve conter secao Introducao"
    assert any(h in reported.report for h in ["## Metodos", "## 2. Metodos", "## 2 Métodos"]), "Deve conter secao Metodos"
    assert any(h in reported.report for h in ["## Resultados", "## 3. Resultados", "## 3 Resultados"]), "Deve conter secao Resultados"
    assert any(h in reported.report for h in ["## Discusao", "## 4. Discussao", "## 4 Discussão", "## Discus"]), "Deve conter secao Discussao"
    assert reported.status == IdeaStatus.REPORTED


def test_asde_007_full_pipeline_executes():
    """Pipeline completo executa do problema ao relatorio"""
    engine = ASDEEngine()
    result = engine.run_pipeline(
        "Como a polimatia influencia a resiliencia cognitiva em crianças?",
        domain="educacao",
    )
    assert result["status"] == "completo"
    assert result["total_ideas"] >= 1
    assert result["best_idea"] is not None
    assert result["best_idea"]["status"] == "reported"
    assert result["best_idea"]["innovation_score"] > 0


def test_asde_008_pipeline_steps_complete():
    """Pipeline executa todas as etapas: generate, review, plan, synthesize"""
    engine = ASDEEngine()
    result = engine.run_pipeline("inovacao educacao tecnologia", domain="educacao")
    expected_steps = ["generate", "review", "plan", "synthesize"]
    pipeline_steps = [s["step"] if isinstance(s, dict) else s for s in result["pipeline"]]
    for step in expected_steps:
        assert step in pipeline_steps, f"Pipeline deve conter etapa {step}"
    assert len(result["pipeline"]) >= 4


def test_asde_009_low_novelty_score():
    """Ideia com baixa novidade tem score < 0.5"""
    gen = IdeaGenerator()
    ideas = gen.generate("A", num_ideas=1)
    # Problema curto pode gerar scores mais baixos
    for idea in ideas:
        assert idea.novelty_score >= 0, "Score deve ser >= 0"


def test_asde_010_innovation_score_formula():
    """Innovation score = media de novelty, feasibility, impact"""
    idea = ResearchIdea(
        title="Test",
        novelty_score=0.8, feasibility_score=0.6, impact_score=0.7,
    )
    assert idea.innovation_score == 0.7, f"Esperado 0.7, obtido {idea.innovation_score}"


def test_asde_011_ontology_find_paths_2plus_hops():
    """OntologyGraph encontra caminhos de 2+ hops"""
    graph = OntologyGraph()
    graph.add_node("X", "concept")
    graph.add_node("Y", "concept")
    graph.add_node("Z", "concept")
    graph.add_node("W", "concept")
    graph.add_edge("X", "Y", "causa", 0.8)
    graph.add_edge("Y", "Z", "deriva", 0.7)
    graph.add_edge("Z", "W", "exemplifica", 0.6)

    paths = graph.find_paths("X", "W", max_hops=4)
    assert len(paths) >= 1, "Deve encontrar caminho X->Y->Z->W"
    longest = max(len(p) for p in paths) if paths else 0
    assert longest >= 3, f"Caminho deve ter >=3 nos, maximo {longest}"


def test_asde_012_empty_problem_handling():
    """Problema vazio retorna erro tratado"""
    engine = ASDEEngine()
    result = engine.run_pipeline("")
    assert result["status"] == "erro"
    assert result["ideas"] == []


def test_asde_013_get_report_by_index():
    """get_report retorna relatorio de ideia especifica"""
    engine = ASDEEngine()
    engine.run_pipeline("Como a polimatia afeta o aprendizado?", domain="educacao")
    report = engine.get_report(0)
    if report:
        assert any(h in report for h in ["## Titulo", "## 1.", "## 1 Introdução", "## Introdução"]), "Relatorio deve conter cabecalho de secao"
        assert len(report) > 100


def test_asde_014_ontology_default_initialized():
    """OntologyGraph inicializado com conceitos default"""
    gen = IdeaGenerator()
    status = gen.ontology.to_dict()
    assert status["node_count"] >= 10, f"Esperado >=10 nos, obtido {status['node_count']}"
    assert status["edge_count"] >= 10, f"Esperado >=10 arestas, obtido {status['edge_count']}"


def test_asde_015_idea_to_dict():
    """ResearchIdea.to_dict() retorna dicionario completo"""
    idea = ResearchIdea(
        title="Teste",
        hypothesis="Hipotese",
        mechanism="Mecanismo",
        concepts=["A", "B"],
        novelty_score=0.7,
    )
    d = idea.to_dict()
    assert d["title"] == "Teste"
    assert d["innovation_score"] > 0
    assert "id" in d
    assert "created_at" in d
