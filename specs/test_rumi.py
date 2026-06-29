# -*- coding: utf-8 -*-
"""Testes TDD para RUMI Causal Discovery Pipeline (R28)"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "nexus", "scripts"))

from rumi_causal_discovery import (
    RUMIEngine, CausalGenerator, CausalTester,
    CausalHypothesis, HypothesisStatus, AdversarialReviewer,
)


def test_rumi_001_generate_from_variables():
    """Gerador cria hipoteses a partir de variaveis"""
    gen = CausalGenerator()
    hypotheses = gen.generate_from_variables(["A", "B", "C"])
    assert len(hypotheses) == 6  # 3 * 2 direcoes
    assert all(h.cause in ["A", "B", "C"] for h in hypotheses)


def test_rumi_002_test_hypothesis_confirmed():
    """Hipotese com alta correlacao e confirmada"""
    tester = CausalTester()
    h = CausalHypothesis(cause="Estudo", effect="Nota", confidence=0.8)
    test_data = {"Estudo->Nota": 0.85, "temporal:Estudo>Nota": 0.9, "consistency": 0.85}
    result = tester.test_hypothesis(h, test_data)
    assert result.status == HypothesisStatus.CONFIRMED
    assert result.score >= 0.7


def test_rumi_003_test_hypothesis_refuted():
    """Hipotese com baixa correlacao e refutada"""
    tester = CausalTester()
    h = CausalHypothesis(cause="Chuva", effect="Nota", confidence=0.2)
    test_data = {"Chuva->Nota": 0.1, "temporal:Chuva>Nota": 0.2, "consistency": 0.3}
    result = tester.test_hypothesis(h, test_data)
    assert result.status == HypothesisStatus.REFUTED


def test_rumi_004_tournament_selects_top():
    """Torneio seleciona as melhores hipoteses"""
    tester = CausalTester()
    proposals = [
        CausalHypothesis(cause="A", effect="B", confidence=0.9, score=0.85,
                         status=HypothesisStatus.CONFIRMED),
        CausalHypothesis(cause="B", effect="C", confidence=0.3, score=0.25,
                         status=HypothesisStatus.REFUTED),
        CausalHypothesis(cause="C", effect="A", confidence=0.7, score=0.65,
                         status=HypothesisStatus.CONFIRMED),
    ]
    winners = tester.tournament(proposals, top_k=2)
    assert len(winners) == 2
    assert winners[0].cause == "A"  # Melhor score


def test_rumi_005_adversarial_review():
    """Revisao adversarial aponta problemas"""
    reviewer = AdversarialReviewer()
    h = CausalHypothesis(cause="X", effect="Y", confidence=0.3, score=0.4)
    review = reviewer.review(h)
    assert review["passed"] is False
    assert review["total_issues"] >= 1


def test_rumi_006_adversarial_review_passes():
    """Hipotese forte passa na revisao"""
    reviewer = AdversarialReviewer()
    h = CausalHypothesis(
        cause="Exercicio",
        effect="Saude",
        confidence=0.85,
        score=0.82,
        evidence=["Estudo 1: correlacao 0.8", "Estudo 2: correlacao 0.75",
                  "Estudo 3: metanalise confirma"],
        mechanism="Exercicio regular melhora saude cardiovascular e mental",
        status=HypothesisStatus.CONFIRMED,
    )
    review = reviewer.review(h)
    assert review["passed"] is True


def test_rumi_007_full_discovery_pipeline():
    """Pipeline completo de descoberta causal funciona"""
    engine = RUMIEngine()
    result = engine.discover(
        variables=["Educacao", "Renda", "Saude", "Longevidade"],
        test_data={
            "Educacao->Renda": 0.75,
            "Renda->Saude": 0.65,
            "Saude->Longevidade": 0.85,
            "temporal:Educacao>Renda": 0.8,
            "temporal:Renda>Saude": 0.7,
            "temporal:Saude>Longevidade": 0.9,
            "consistency": 0.8,
        },
        top_k=3,
    )
    assert result["total_hypotheses_generated"] == 12  # 4 * 3
    assert result["confirmed"] >= 1
    assert len(result["top_hypotheses"]) == 3
    assert "causal_graph" in result
    assert len(result["causal_graph"]["edges"]) >= 1


def test_rumi_008_analyze_causal_claim():
    """Analise de reivindicacao causal especifica"""
    engine = RUMIEngine()
    result = engine.analyze_causal_claim(
        cause="Polimatia",
        effect="Resiliencia Cognitiva",
        mechanism="Exposicao a multiplos dominios fortalece conexoes neurais",
        confidence=0.8,
    )
    assert "hypothesis" in result
    assert "review" in result
    assert result["recommendation"] in ("Aceitar", "Rejeitar", "Requer mais evidencias")


def test_rumi_009_generate_with_mechanism():
    """Geracao com mecanismo explicito"""
    gen = CausalGenerator()
    h = gen.generate_with_mechanism(
        cause="Leitura", effect="Vocabulario",
        mechanism="Exposicao a novas palavras expande lexico",
        confidence=0.85,
    )
    assert h.cause == "Leitura"
    assert h.effect == "Vocabulario"
    assert "palavras" in h.mechanism


def test_rumi_010_causal_graph_build():
    """Grafo causal e construido corretamente a partir de hipoteses"""
    engine = RUMIEngine()
    result = engine.discover(
        variables=["A", "B"],
        test_data={"A->B": 0.9, "temporal:A>B": 0.85, "consistency": 0.8},
        top_k=5,
    )
    graph = result["causal_graph"]
    assert len(graph["nodes"]) >= 2
    # Pode ter 0 arestas se hipoteses foram refutadas
    assert "nodes" in graph
    assert "edges" in graph


def test_rumi_011_empty_variables_handling():
    """Lista vazia de variaveis retorna resultado vazio"""
    engine = RUMIEngine()
    result = engine.discover([], top_k=3)
    assert result["total_hypotheses_generated"] == 0
    assert len(result["top_hypotheses"]) == 0


def test_rumi_012_adversarial_high_severity():
    """Multiplos problemas geram severidade alta"""
    reviewer = AdversarialReviewer()
    h = CausalHypothesis(
        cause="A", effect="B",
        confidence=0.1, score=0.2,
        mechanism="", evidence=[]
    )
    review = reviewer.review(h)
    assert review["severity"] == "high"
