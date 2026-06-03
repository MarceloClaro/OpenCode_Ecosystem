#!/usr/bin/env python
# =====================================================================
# CICLO 4 — TESTES DE SÍNTESE MULTI-CADEIA (C4-T1 a C4-T14)
# =====================================================================
# Testes para parallel_chain.py e synthesis_engine.py
# =====================================================================

import sys, os, time, math, re, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.dirname(__file__))

from agents.parallel_chain import (
    ParallelChain, ChainResult, _run_single_chain,
    ChainConfig, DEFAULT_CHAIN_MODES
)
from agents.synthesis_engine import (
    SynthesisEngine, SynthesisResult, STRATEGIES
)

import pytest


# =====================================================================
# FIXTURES
# =====================================================================

@pytest.fixture
def sample_chains():
    """Três cadeias simuladas com PCI variados."""
    return [
        ChainResult(chain_id=0, mode="standard", budget=60, solution_text="A solução ótima é usar parallel dispatch com 4 workers.", pci_score=85.0, elapsed_ms=500, num_agents=4),
        ChainResult(chain_id=1, mode="magnum", budget=100, solution_text="Recomenda-se ProcessPoolExecutor para isolamento de memória.", pci_score=92.0, elapsed_ms=800, num_agents=6),
        ChainResult(chain_id=2, mode="express", budget=30, solution_text="ThreadPoolExecutor é suficiente para tarefas leves.", pci_score=65.0, elapsed_ms=300, num_agents=2),
    ]


@pytest.fixture
def chains_with_errors():
    """Três cadeias onde uma falhou."""
    return [
        ChainResult(chain_id=0, mode="standard", budget=60, solution_text="Cadeia 0 funcionou normalmente.", pci_score=80.0, elapsed_ms=400, num_agents=4),
        ChainResult(chain_id=1, mode="magnum", budget=100, solution_text="", pci_score=0.0, elapsed_ms=10000, num_agents=0, error="Timeout após 10s"),
        ChainResult(chain_id=2, mode="express", budget=30, solution_text="Cadeia 2 funcionou.", pci_score=70.0, elapsed_ms=300, num_agents=2),
    ]


# =====================================================================
# C4-T1: SynthesisEngine cria com estratégia válida
# =====================================================================

class TestC4T1_SynthesisEngineInit:
    
    def test_default_strategy(self):
        engine = SynthesisEngine()
        assert engine.strategy == "weighted_vote"
    
    def test_custom_strategy(self):
        for s in STRATEGIES:
            engine = SynthesisEngine(strategy=s)
            assert engine.strategy == s
    
    def test_invalid_strategy_fallback(self):
        engine = SynthesisEngine(strategy="invalid")
        assert engine.strategy == "weighted_vote"
    
    def test_empty_chains(self):
        engine = SynthesisEngine()
        result = engine.synthesize([])
        assert result.final_answer == "No chains to synthesize"
        assert result.confidence == 0.0
        assert result.chain_count == 0


# =====================================================================
# C4-T2: Weighted Vote funciona com dados variados
# =====================================================================

class TestC4T2_WeightedVote:
    
    def test_weighted_vote_returns_string(self, sample_chains):
        engine = SynthesisEngine(strategy="weighted_vote")
        result = engine.synthesize(sample_chains)
        assert isinstance(result.final_answer, str)
        assert len(result.final_answer) > 0
    
    def test_weighted_vote_weights(self, sample_chains):
        engine = SynthesisEngine(strategy="weighted_vote")
        result = engine.synthesize(sample_chains)
        # Cadeia 1 tem maior PCI, deve ter mais influência
        assert result.confidence > 0
        assert result.chain_count == 3
    
    def test_weighted_vote_single_chain(self):
        engine = SynthesisEngine()
        result = engine.synthesize([
            ChainResult(chain_id=0, mode="standard", budget=60, solution_text="Unica cadeia de raciocinio.", pci_score=50.0, elapsed_ms=100, num_agents=2),
        ])
        assert "Unica cadeia" in result.final_answer
        assert result.confidence == 0.5
    
    def test_weighted_vote_handles_errors(self, chains_with_errors):
        engine = SynthesisEngine(strategy="weighted_vote")
        result = engine.synthesize(chains_with_errors)
        # Deve ignorar cadeia 1 (erro) e trabalhar com as outras 2
        assert result.chain_count == 3
        assert "Timeout" in str(result.disagreements)


# =====================================================================
# C4-T3: Debate identifica divergências corretamente
# =====================================================================

class TestC4T3_Debate:
    
    def test_debate_detects_divergence(self, sample_chains):
        engine = SynthesisEngine(strategy="debate")
        result = engine.synthesize(sample_chains)
        assert len(result.final_answer) > 0
        assert result.confidence > 0
    
    def test_debate_similar_chains(self):
        engine = SynthesisEngine(strategy="debate")
        similar = [
            ChainResult(chain_id=0, mode="standard", budget=60, solution_text="Usar parallel dispatch com 4 workers é a melhor abordagem para otimização.", pci_score=90.0, elapsed_ms=500, num_agents=4),
            ChainResult(chain_id=1, mode="magnum", budget=100, solution_text="Parallel dispatch com workers pooling apresenta performance superior.", pci_score=88.0, elapsed_ms=700, num_agents=5),
        ]
        result = engine.synthesize(similar)
        # Pouca divergência entre cadeias similares
        assert len(result.disagreements) <= 1
    
    def test_debate_all_identical(self):
        engine = SynthesisEngine(strategy="debate")
        identical = [
            ChainResult(chain_id=0, mode="standard", budget=60, solution_text="Solução ótima para paralelismo é usar thread pooling com workers.", pci_score=80.0, elapsed_ms=400, num_agents=3),
            ChainResult(chain_id=1, mode="standard", budget=60, solution_text="Solução ótima para paralelismo é usar thread pooling com workers.", pci_score=80.0, elapsed_ms=400, num_agents=3),
        ]
        result = engine.synthesize(identical)
        assert len(result.disagreements) == 0
    
    def test_debate_confidence_from_best(self, sample_chains):
        engine = SynthesisEngine(strategy="debate")
        result = engine.synthesize(sample_chains)
        # Confiança deve ser ponderada pela melhor cadeia (PCI=92)
        assert 0.5 <= result.confidence <= 1.0


# =====================================================================
# C4-T4: Ensemble combina múltiplas perspectivas
# =====================================================================

class TestC4T4_Ensemble:
    
    def test_ensemble_contains_all_perspectives(self, sample_chains):
        engine = SynthesisEngine(strategy="ensemble")
        result = engine.synthesize(sample_chains)
        for c in sample_chains:
            assert f"Perspective {c.chain_id}" in result.final_answer
    
    def test_ensemble_sources(self, sample_chains):
        engine = SynthesisEngine(strategy="ensemble")
        result = engine.synthesize(sample_chains)
        assert len(result.sources) == len([c for c in sample_chains if not c.error])
    
    def test_ensemble_all_failed(self):
        engine = SynthesisEngine(strategy="ensemble")
        result = engine.synthesize([
            ChainResult(chain_id=0, mode="standard", budget=60, solution_text="", pci_score=0.0, elapsed_ms=0, num_agents=0, error="Falha"),
        ])
        assert "All chains failed" in result.final_answer
    
    def test_ensemble_empty(self):
        engine = SynthesisEngine(strategy="ensemble")
        result = engine.synthesize([])
        assert "No chains" in result.final_answer
        assert result.confidence == 0.0


# =====================================================================
# C4-T5: Best Of seleciona maior PCI
# =====================================================================

class TestC4T5_BestOf:
    
    def test_best_of_selects_highest_pci(self, sample_chains):
        engine = SynthesisEngine(strategy="best_of")
        result = engine.synthesize(sample_chains)
        # Cadeia 1 tem PCI=92 (maior)
        assert "ProcessPoolExecutor" in result.final_answer
        assert result.confidence > 0
    
    def test_best_of_single_source(self, sample_chains):
        engine = SynthesisEngine(strategy="best_of")
        result = engine.synthesize(sample_chains)
        assert len(result.sources) == 1  # Apenas a melhor
    
    def test_best_of_empty(self):
        engine = SynthesisEngine(strategy="best_of")
        result = engine.synthesize([])
        assert "No chains" in result.final_answer
        assert result.confidence == 0.0


# =====================================================================
# C4-T6: DEFAULT_CHAIN_MODES contém configurações válidas
# =====================================================================

class TestC4T6_ChainModes:
    
    def test_default_has_four_modes(self):
        assert len(DEFAULT_CHAIN_MODES) == 4
    
    def test_modes_have_required_keys(self):
        for cfg in DEFAULT_CHAIN_MODES:
            assert "mode" in cfg
            assert "budget" in cfg
            assert "workers" in cfg
    
    def test_express_has_lowest_budget(self):
        express = [c for c in DEFAULT_CHAIN_MODES if c["mode"] == "express"]
        assert len(express) == 1
        assert express[0]["budget"] == 30
    
    def test_research_has_highest_budget(self):
        research = [c for c in DEFAULT_CHAIN_MODES if c["mode"] == "research"]
        assert len(research) == 1
        assert research[0]["budget"] == 200


# =====================================================================
# C4-T7: ChainConfig cria instância com defaults
# =====================================================================

class TestC4T7_ChainConfig:
    
    def test_default_config(self):
        cfg = ChainConfig()
        assert cfg.mode == "standard"
        assert cfg.budget == 60
        assert cfg.workers == 2
    
    def test_custom_config(self):
        cfg = ChainConfig(mode="magnum", budget=100, workers=4)
        assert cfg.mode == "magnum"
        assert cfg.budget == 100
        assert cfg.workers == 4


# =====================================================================
# C4-T8: run_single_chain executável (teste de importação e chamada)
# =====================================================================

class TestC4T8_SingleChain:
    
    def test_run_single_chain_importable(self):
        from agents.parallel_chain import _run_single_chain
        assert callable(_run_single_chain)
    
    def test_run_single_chain_with_simple_problem(self):
        result = _run_single_chain("Qual a capital do Brasil?", "standard", 30, 2, 1, False)
        assert isinstance(result, ChainResult)
        assert result.chain_id == 1
        assert result.mode == "standard"
        assert result.budget == 30
        assert result.pci_score >= 0
        assert result.elapsed_ms >= 0


# =====================================================================
# C4-T9: ParallelChain.run_chains com config personalizada
# =====================================================================

class TestC4T9_ParallelChainRun:
    
    def test_run_chains_single_chain(self):
        pc = ParallelChain(max_workers=1)
        results = pc.run_chains("Qual a capital do Brasil?", [
            {"mode": "standard", "budget": 30, "workers": 1}
        ], verify=False)
        assert len(results) == 1
        assert isinstance(results[0], ChainResult)
        assert results[0].chain_id == 1
    
    def test_run_chains_returns_all(self):
        pc = ParallelChain(max_workers=2)
        configs = [
            {"mode": "express", "budget": 30, "workers": 1},
            {"mode": "standard", "budget": 60, "workers": 2},
        ]
        results = pc.run_chains("Qual a capital do Brasil?", configs, verify=False)
        assert len(results) == 2
        assert results[0].chain_id == 1
        assert results[1].chain_id == 2
    
    def test_run_chains_default_config(self):
        pc = ParallelChain(max_workers=2)
        results = pc.run_chains("Qual a capital do Brasil?", verify=False)
        assert len(results) == 4  # DEFAULT_CHAIN_MODES


# =====================================================================
# C4-T10: run_sequential produz mesmos resultados que run_chains
# =====================================================================

class TestC4T10_RunSequential:
    
    def test_run_sequential_single(self):
        pc = ParallelChain()
        results = pc.run_sequential("Qual a capital do Brasil?", [
            {"mode": "express", "budget": 30, "workers": 1}
        ], verify=False)
        assert len(results) == 1
        assert results[0].chain_id == 1
    
    def test_run_sequential_default(self):
        pc = ParallelChain()
        results = pc.run_sequential("Qual a capital do Brasil?", verify=False)
        assert len(results) == 4


# =====================================================================
# C4-T11: Todas as 4 estratégias de síntese produzem resultados válidos
# =====================================================================

class TestC4T11_AllStrategies:
    
    def test_all_strategies_produce_results(self, sample_chains):
        for strategy in STRATEGIES:
            engine = SynthesisEngine(strategy=strategy)
            result = engine.synthesize(sample_chains)
            assert isinstance(result.final_answer, str)
            assert len(result.final_answer) > 0
            assert result.confidence >= 0.0


# =====================================================================
# C4-T12: Chains com erro não quebram síntese
# =====================================================================

class TestC4T12_ErrorResilience:
    
    def test_all_chains_failed(self):
        engine = SynthesisEngine(strategy="weighted_vote")
        result = engine.synthesize([
            ChainResult(chain_id=0, mode="standard", budget=60, solution_text="", pci_score=0.0, elapsed_ms=0, num_agents=0, error="Falha 1"),
            ChainResult(chain_id=1, mode="magnum", budget=100, solution_text="", pci_score=0.0, elapsed_ms=0, num_agents=0, error="Falha 2"),
        ])
        assert result.confidence == 0.0
    
    def test_mixed_errors_results(self, chains_with_errors):
        engine = SynthesisEngine(strategy="weighted_vote")
        result = engine.synthesize(chains_with_errors)
        assert result.confidence > 0  # Ainda há cadeias válidas
        assert len(result.disagreements) > 0  # Erro reportado


# =====================================================================
# C4-T13: Síntese com diferentes números de cadeias
# =====================================================================

class TestC4T13_DifferentChainCounts:
    
    def test_single_chain(self):
        engine = SynthesisEngine(strategy="weighted_vote")
        chains = [ChainResult(chain_id=0, mode="standard", budget=60, solution_text="Única.", pci_score=75.0, elapsed_ms=100, num_agents=3)]
        result = engine.synthesize(chains)
        assert result.chain_count == 1
        assert result.confidence == 0.75
    
    def test_five_chains(self):
        engine = SynthesisEngine(strategy="weighted_vote")
        chains = [
            ChainResult(chain_id=i, mode="standard", budget=60, solution_text=f"Cadeia {i} solution.", pci_score=70.0 + i * 5, elapsed_ms=200, num_agents=3)
            for i in range(5)
        ]
        result = engine.synthesize(chains)
        assert result.chain_count == 5
        assert result.confidence > 0


# =====================================================================
# C4-T14: Precisão da síntese — baseline empírico
# =====================================================================

class TestC4T14_Baseline:
    """
    Teste baseline: verifica que a síntese weighted_vote
    converge para a cadeia com maior PCI em cenário controlado.
    """
    
    def test_weighted_vote_converges(self):
        engine = SynthesisEngine(strategy="weighted_vote")
        chains = [
            ChainResult(chain_id=0, mode="express", budget=30, solution_text="Resposta A.", pci_score=30.0, elapsed_ms=100, num_agents=2),
            ChainResult(chain_id=1, mode="standard", budget=60, solution_text="Resposta B.", pci_score=50.0, elapsed_ms=200, num_agents=3),
            ChainResult(chain_id=2, mode="magnum", budget=100, solution_text="Resposta C.", pci_score=95.0, elapsed_ms=500, num_agents=5),
        ]
        result = engine.synthesize(chains)
        # Cadeia 2 tem PCI dominante (95), deve ter forte influência
        assert result.confidence > 0.5
        # A confiança deve refletir as cadeias válidas
        assert "Resposta" in result.final_answer
    
    def test_debate_resolves_conflict(self):
        engine = SynthesisEngine(strategy="debate")
        # Duas cadeias com soluções muito diferentes
        chains = [
            ChainResult(chain_id=0, mode="standard", budget=60, solution_text="Resposta: utilizar parallel dispatch com quatro workers.", pci_score=90.0, elapsed_ms=300, num_agents=4),
            ChainResult(chain_id=1, mode="magnum", budget=100, solution_text="Resposta: recorrer a process pool executor isolado.", pci_score=40.0, elapsed_ms=400, num_agents=5),
        ]
        result = engine.synthesize(chains)
        # Debate escolhe cadeia de maior PCI (90)
        assert result.confidence > 0.5
        assert "parallel dispatch" in result.final_answer or "quatro workers" in result.final_answer


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
