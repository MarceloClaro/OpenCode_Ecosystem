#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para as 4 novas research skills do R35.
Valida implementação, capacidades e integração com o ecossistema.
"""

import sys
import os
import json
import math

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "research", "game-theory"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "research", "temporal-population"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "research", "theoretical-empirical"))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "skills", "research", "logical-multiscale"))

# ─── Game Theory ─────────────────────────────────────────────────────

def test_game_theory_import():
    """CT-001: Import do módulo game_theory."""
    import game_theory
    assert hasattr(game_theory, "PayoffMatrix")
    assert hasattr(game_theory, "NashEquilibrium")
    assert hasattr(game_theory, "CLASSIC_GAMES")


def test_game_theory_payoff_matrix():
    """CT-002: Criação de matriz de payoff."""
    from game_theory import PayoffMatrix
    pm = PayoffMatrix(
        player1=["A", "B"],
        player2=["X", "Y"],
        payoffs={("A", "X"): (1, 2), ("A", "Y"): (3, 4),
                 ("B", "X"): (5, 6), ("B", "Y"): (7, 8)},
    )
    assert pm.get_payoff("A", "X") == (1, 2)
    assert pm.get_payoff("B", "Y") == (7, 8)


def test_game_theory_nash_pure():
    """CT-003: Equilíbrio de Nash em estratégias puras."""
    from game_theory import CLASSIC_GAMES, NashEquilibrium
    game = CLASSIC_GAMES["prisoners_dilemma"]
    ne = NashEquilibrium.find_pure_strategy(game)
    assert len(ne) == 1
    assert ne[0][0] == "trair"
    assert ne[0][1] == "trair"


def test_game_theory_battle_sexes():
    """CT-004: Batalha dos Sexos tem 2 equilíbrios de Nash."""
    from game_theory import CLASSIC_GAMES, NashEquilibrium
    game = CLASSIC_GAMES["battle_of_sexes"]
    ne = NashEquilibrium.find_pure_strategy(game)
    assert len(ne) == 2


def test_game_theory_pareto():
    """CT-005: Verificação de Pareto."""
    from game_theory import CLASSIC_GAMES, NashEquilibrium
    game = CLASSIC_GAMES["prisoners_dilemma"]
    is_po, _ = NashEquilibrium.is_pareto_optimal(game, "cooperar", "cooperar")
    assert is_po  # cooperar-cooperar é Pareto-ótimo


def test_game_theory_analyze():
    """CT-006: Análise completa de jogo."""
    from game_theory import analyze_game
    result = analyze_game("chicken")
    assert result["num_equilibria"] >= 1
    assert "nash_equilibria_pure" in result
    assert "pareto_analysis" in result


# ─── Temporal Population ─────────────────────────────────────────────

def test_temporal_import():
    """CT-007: Import do módulo temporal_population."""
    import temporal_population
    assert hasattr(temporal_population, "TimeSeriesAnalyzer")
    assert hasattr(temporal_population, "SampleSizeCalculator")


def test_temporal_moving_average():
    """CT-008: Média móvel."""
    from temporal_population import TimeSeriesAnalyzer
    ts = TimeSeriesAnalyzer()
    data = [1, 2, 3, 4, 5]
    ma = ts.moving_average(data, window=3)
    assert len(ma) == 3
    assert ma[0] == 2.0  # (1+2+3)/3


def test_temporal_trend():
    """CT-009: Direção de tendência."""
    from temporal_population import TimeSeriesAnalyzer
    ts = TimeSeriesAnalyzer()
    assert ts.trend_direction([1, 2, 3, 4, 5]) == "crescente_forte"
    assert ts.trend_direction([5, 4, 3, 2, 1]) == "decrescente_forte"
    assert ts.trend_direction([3, 3, 3, 3]) == "estavel"


def test_longitudinal_design():
    """CT-010: Caracterização de delineamento longitudinal."""
    from temporal_population import LongitudinalAnalyzer
    la = LongitudinalAnalyzer()
    design = la.characterize_design(waves=3, total_time_years=5, n_participants=350)
    assert design["design_type"] == "longitudinal_prospectivo"
    assert design["statistical_power"] == "adequado"


def test_sample_size_prevalence():
    """CT-011: Cálculo de tamanho amostral para prevalência."""
    from temporal_population import SampleSizeCalculator
    ssc = SampleSizeCalculator()
    result = ssc.for_prevalence(population=10000, expected_prevalence=0.5)
    assert result["sample_size"] > 0
    assert result["sample_size"] <= result["sample_size_infinite"]


def test_sample_size_clinical():
    """CT-012: Cálculo de tamanho amostral para ensaio clínico."""
    from temporal_population import SampleSizeCalculator
    ssc = SampleSizeCalculator()
    result = ssc.for_clinical_trial(effect_size=0.5, alpha=0.05, power=0.80)
    assert result["n_total"] > 0
    assert result["n_per_group"] > 0


def test_generalizability():
    """CT-013: Avaliação de generalização populacional."""
    from temporal_population import PopulationGeneralizer
    pg = PopulationGeneralizer()
    result = pg.assess_generalizability(
        sample_n=500, population_n=100000,
        coverage_regions=["sul", "sudeste"],
        age_range=(18, 65),
    )
    assert result["generalization_level"] in ("alta", "moderada", "limitada")


# ─── Theoretical Empirical ───────────────────────────────────────────

def test_theoretical_import():
    """CT-014: Import do módulo theoretical_empirical."""
    import theoretical_empirical
    assert hasattr(theoretical_empirical, "EpistemologicalClassifier")
    assert hasattr(theoretical_empirical, "ReliabilityAnalyzer")


def test_epistemological_classify():
    """CT-015: Classificação epistemológica."""
    from theoretical_empirical import EpistemologicalClassifier
    info = EpistemologicalClassifier.classify("positivista")
    assert info is not None
    assert info["natureza_conhecimento"] == "objetivo_verificavel"
    info2 = EpistemologicalClassifier.classify("desconhecida")
    assert info2 is None


def test_epistemological_compare():
    """CT-016: Comparação entre epistemologias."""
    from theoretical_empirical import EpistemologicalClassifier
    comp = EpistemologicalClassifier.compare("positivista", "interpretativista")
    assert "similarities" in comp
    assert "differences" in comp
    assert len(comp["differences"]) > 0


def test_cronbach_alpha():
    """CT-017: Alpha de Cronbach."""
    from theoretical_empirical import ReliabilityAnalyzer
    ra = ReliabilityAnalyzer()
    # Dados correlacionados positivamente (medem o mesmo construto)
    items = [
        [4, 5, 4, 5, 5, 4, 4, 5, 5, 4],
        [3, 4, 4, 4, 5, 3, 4, 4, 5, 4],
        [4, 5, 3, 5, 4, 4, 3, 5, 4, 3],
        [3, 4, 4, 5, 5, 3, 4, 4, 5, 4],
    ]
    alpha = ra.cronbach_alpha(items)
    assert 0 <= alpha <= 1
    assert alpha > 0.5  # Dados correlacionados → alpha bom


def test_cohens_d():
    """CT-018: Cálculo do d de Cohen."""
    from theoretical_empirical import EffectSizeCalculator
    esc = EffectSizeCalculator()
    result = esc.cohens_d(mean1=15, mean2=10, sd1=3, sd2=3, n1=30, n2=30)
    assert result["d"] > 0
    assert result["interpretation"] == "grande"  # d de Cohen > 0.8


def test_pearson_r_to_d():
    """CT-019: Conversão de Pearson r para d de Cohen."""
    from theoretical_empirical import EffectSizeCalculator
    esc = EffectSizeCalculator()
    d = esc.pearson_r_to_d(0.5)
    assert abs(d - 1.1547) < 0.01


# ─── Logical Multiscale ─────────────────────────────────────────────

def test_logical_import():
    """CT-020: Import do módulo logical_multiscale."""
    import logical_multiscale
    assert hasattr(logical_multiscale, "InferenceEngine")
    assert hasattr(logical_multiscale, "MultiScaleAnalyzer")


def test_deductive_valid():
    """CT-021: Dedução válida."""
    from logical_multiscale import InferenceEngine, Proposition
    ie = InferenceEngine()
    p1 = Proposition("Todos os humanos são mortais", True)
    p2 = Proposition("Sócrates é humano", True)
    result = ie.deductive([p1, p2], Proposition("Sócrates é mortal", True))
    assert result["valid"] == True


def test_inductive_strength():
    """CT-022: Força indutiva."""
    from logical_multiscale import InferenceEngine
    ie = InferenceEngine()
    observations = [{"id": i, "supports": True} for i in range(10)]
    result = ie.inductive(observations, "Padrão consistente")
    assert result["strength"] > 0.5
    assert result["assessment"] in ("forte", "moderada")


def test_abductive_reasoning():
    """CT-023: Raciocínio abdutivo."""
    from logical_multiscale import InferenceEngine
    ie = InferenceEngine()
    rules = [
        {"antecedent": "Choveu", "consequent": "chão molhado",
         "label": "chuva", "prior_probability": 0.8},
    ]
    result = ie.abductive("chão molhado", rules)
    assert result["n_possible_explanations"] >= 1
    assert result["best_explanations"][0]["explanation"] == "Choveu"


def test_fallacy_detection():
    """CT-024: Detecção de falácias."""
    from logical_multiscale import ArgumentationValidator
    av = ArgumentationValidator()
    fallacies = av.detect_fallacies("Todos os políticos são corruptos, sempre foi assim.")
    assert len(fallacies) >= 1
    assert any(f["fallacy"] == "hasty_generalization" for f in fallacies)


def test_multiscale_analysis():
    """CT-025: Análise multiescala."""
    from logical_multiscale import MultiScaleAnalyzer
    msa = MultiScaleAnalyzer()
    result = msa.analyze_phenomenon(
        "Fenômeno X",
        micro_indicators=["a", "b", "c"],
        meso_indicators=["d", "e", "f"],
        macro_indicators=["g"],
    )
    assert result["depth_score"] > 0
    assert "strong_levels" in result


def test_cross_level():
    """CT-026: Efeitos cross-level."""
    from logical_multiscale import MultiScaleAnalyzer
    msa = MultiScaleAnalyzer()
    result = msa.cross_level_effects(
        "estresse", "produtividade",
        "O impacto do estresse na produtividade"
    )
    assert "type" in result
    assert result["requires_multilevel_modeling"] == True
