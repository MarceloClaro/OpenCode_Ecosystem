# -*- coding: utf-8 -*-
"""
test_metacognitive_search.py — SPEC-062: TDD Test Suite para Metacognitive Search Engine
========================================================================================
12 Casos de Teste (CT) para validar o motor de busca metacognitiva, o process verifier,
o monitor e o algoritmo de backtracking em tempo de inferência.

Uso:
    python -m pytest specs/test_metacognitive_search.py -v
"""

import sys
from pathlib import Path
import pytest

# Configurar path dos módulos
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
sys.path.insert(0, str(BASE_DIR / "nexus" / "scripts"))

from metacognitive_search import (
    ReasoningNode,
    ProcessVerifier,
    MetacognitiveMonitor,
    MetacognitiveSearchEngine,
    solve_with_metacognitive_search
)


class TestMetacognitiveSearch:

    def test_ct_062_001_node_creation(self):
        """CT-062-001: Validar criação e propriedades de inicialização do ReasoningNode."""
        node = ReasoningNode(node_id=1, parent_id=None, step_content="Inicio", depth=0)
        assert node.node_id == 1
        assert node.parent_id is None
        assert node.score == 1.0
        assert node.depth == 0
        assert len(node.children) == 0

    def test_ct_062_002_verifier_short_step(self):
        """CT-062-002: Validar que passos de raciocínio muito curtos/superficiais são penalizados."""
        score, flaws = ProcessVerifier.evaluate_step("Erro", "Resolver equacao polinomial de grau dois", [])
        assert score < 0.8
        assert any("curto" in f for f in flaws)

    def test_ct_062_003_verifier_contradiction(self):
        """CT-062-003: Validar penalização de contradições óbvias de auto-correção."""
        score, flaws = ProcessVerifier.evaluate_step(
            "Análise concluída porém, não conseguimos demonstrar o teorema pois é inconsistente.",
            "Resolver equacao polinomial de grau dois",
            []
        )
        assert score < 1.0
        assert any("termo" in f for f in flaws)

    def test_ct_062_004_verifier_relevance(self):
        """CT-062-004: Validar penalização por falta de relevância dos termos com a pergunta."""
        score, flaws = ProcessVerifier.evaluate_step(
            "Vamos cantar uma música bonita para distrair os jogadores.",
            "Calcular o maior divisor comum do conjunto de numeros inteiros",
            []
        )
        assert score < 1.0
        assert any("relevância" in f for f in flaws)

    def test_ct_062_005_verifier_loop_detection(self):
        """CT-062-005: Validar que redundâncias e repetições de ideias geram baixos scores."""
        previous = ["Analisando o divisor comum sob a perspectiva de primos."]
        score, flaws = ProcessVerifier.evaluate_step(
            "Analisando o divisor comum sob a perspectiva de primos.",
            "Calcular o maior divisor comum",
            previous
        )
        assert score < 0.6
        assert any("redundante" in f for f in flaws)

    def test_ct_062_006_verifier_perfect_step(self):
        """CT-062-006: Validar que um passo de raciocínio de qualidade recebe pontuação alta."""
        score, flaws = ProcessVerifier.evaluate_step(
            "Decompomos o maior divisor comum utilizando o algoritmo euclidiano classico para inteiros.",
            "Calcular o maior divisor comum",
            []
        )
        assert score >= 0.9
        assert len(flaws) == 0

    def test_ct_062_007_monitor_no_backtrack(self):
        """CT-062-007: Validar que nós com score acima do threshold não sofrem backtracking."""
        monitor = MetacognitiveMonitor(threshold=0.6)
        node = ReasoningNode(node_id=1, parent_id=None, step_content="Passo longo", depth=1, score=0.8)
        assert not monitor.should_backtrack(node)

    def test_ct_062_008_monitor_should_backtrack(self):
        """CT-062-008: Validar que nós com score abaixo do threshold sofrem backtracking/poda."""
        monitor = MetacognitiveMonitor(threshold=0.6)
        node = ReasoningNode(node_id=1, parent_id=None, step_content="Passo curto", depth=1, score=0.5)
        assert monitor.should_backtrack(node)

    def test_ct_062_009_monitor_loop_backtrack(self):
        """CT-062-009: Validar que detecção de loop no estado metacognitivo aciona backtracking."""
        monitor = MetacognitiveMonitor(threshold=0.6)
        node = ReasoningNode(
            node_id=1,
            parent_id=None,
            step_content="Loop",
            depth=1,
            score=0.9,
            metacognitive_state={"loop_detected": True}
        )
        assert monitor.should_backtrack(node)

    def test_ct_062_010_search_engine_success(self):
        """CT-062-010: Validar a execução completa do motor de busca obtendo uma trajetória."""
        engine = MetacognitiveSearchEngine(max_depth=3, branch_factor=2)
        
        def generator(ctx, k):
            import hashlib
            sentences = [
                "Decompomos o maior divisor comum utilizando o algoritmo euclidiano classico para inteiros.",
                "Aplicamos a identidade de Bezout para garantir a existencia de coeficientes inteiros.",
                "Provamos que a relacao de divisibilidade e reflexiva e transitiva no conjunto.",
                "Obtemos a forma fatorada unica de cada termo pelo teorema fundamental da aritmetica."
            ]
            idx = int(hashlib.md5(ctx.encode("utf-8")).hexdigest(), 16)
            return [sentences[(idx + i) % len(sentences)] for i in range(k)]
            
        res = engine.search("Calcular o maior divisor comum", generator)
        assert res["status"] == "sucesso"
        assert len(res["best_path_nodes"]) == 4
        assert res["best_score"] > 0.8

    def test_ct_062_011_search_budget_easy(self):
        """CT-062-011: Validar que o orçamento de busca para nível fácil possui profundidade reduzida."""
        res = solve_with_metacognitive_search("Calcular divisor comum", difficulty="easy")
        assert res["status"] == "sucesso"
        assert len(res["best_path_nodes"]) == 4

    def test_ct_062_012_search_budget_hard(self):
        """CT-062-012: Validar que a busca com dificuldade padrão atinge profundidade maior."""
        res = solve_with_metacognitive_search("Calcular divisor comum", difficulty="medium")
        assert res["status"] == "sucesso"
        assert len(res["best_path_nodes"]) == 6
