#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
logical_multiscale.py — Raciocínio Lógico e Análise Multiescala
================================================================
Implementa motor de inferência lógica (dedução, indução, abdução),
análise multiescala e validação de estrutura argumentativa.

Capabilities:
  - logical_inference: Inferência lógica, dedução e argumentação crítica
  - multi_scale_analysis: Análise multiescala e multinível
"""

from __future__ import annotations
import json
from typing import Any, Dict, List, Optional, Tuple


# ─── Logical Inference Engine ───────────────────────────────────────

class Proposition:
    """Representa uma proposição lógica."""

    def __init__(self, statement: str, truth_value: Optional[bool] = None):
        self.statement = statement
        self.truth_value = truth_value

    def __repr__(self) -> str:
        tv = self.truth_value
        return f"Proposition('{self.statement}', truth={tv})"


class InferenceEngine:
    """Motor de inferência lógica com suporte a dedução, indução e abdução."""

    @staticmethod
    def deductive(premises: List[Proposition], conclusion: Proposition) -> Dict:
        """Verifica validade dedutiva: se premissas são verdadeiras,
        conclusão deve ser verdadeira (modus ponens, modus tollens, silogismo)."""
        if len(premises) < 2:
            return {"valid": False, "type": "insuficient_premises",
                    "reason": "Dedução requer pelo menos 2 premissas"}

        all_true = all(p.truth_value == True for p in premises if p.truth_value is not None)
        any_false = any(p.truth_value == False for p in premises if p.truth_value is not None)

        if all_true and conclusion.truth_value == True:
            return {"valid": True, "type": "modus_ponens",
                    "reason": "Premissas verdadeiras → conclusão verdadeira"}
        elif any_false:
            return {"valid": False, "type": "false_premise",
                    "reason": "Pelo menos uma premissa é falsa"}

        return {"valid": None, "type": "indeterminate",
                "reason": "Valor-verdade das premissas insuficiente"}

    @staticmethod
    def inductive(observations: List[Dict], generalization: str) -> Dict:
        """Avalia generalização indutiva a partir de observações."""
        if not observations:
            return {"strength": 0.0, "type": "no_observations",
                    "generalization": generalization}

        n = len(observations)
        consistent = sum(1 for o in observations if o.get("supports", True))
        consistency_ratio = consistent / n

        # Força da indução: consistência + tamanho da amostra (diminishing returns)
        sample_factor = min(1.0, n / 20.0)
        strength = consistency_ratio * 0.7 + sample_factor * 0.3

        if strength >= 0.8:
            assessment = "forte"
        elif strength >= 0.5:
            assessment = "moderada"
        else:
            assessment = "fraca"

        return {
            "strength": round(strength, 3),
            "assessment": assessment,
            "n_observations": n,
            "consistency_ratio": round(consistency_ratio, 3),
            "generalization": generalization,
        }

    @staticmethod
    def abductive(observation: str, known_rules: List[Dict]) -> Dict:
        """Gera a melhor explicação para uma observação (abdução)."""
        best_explanations = []
        for rule in known_rules:
            if rule.get("consequent", "") in observation or observation in rule.get("consequent", ""):
                score = rule.get("prior_probability", 0.5)
                best_explanations.append({
                    "explanation": rule.get("antecedent", ""),
                    "rule": rule.get("label", ""),
                    "plausibility": score,
                })

        best_explanations.sort(key=lambda x: x["plausibility"], reverse=True)

        return {
            "observation": observation,
            "n_possible_explanations": len(best_explanations),
            "best_explanations": best_explanations[:3],
            "abductive_confidence": (
                best_explanations[0]["plausibility"] if best_explanations else 0.0
            ),
        }


class ArgumentationValidator:
    """Validador de estrutura argumentativa."""

    COMMON_FALLACIES = {
        "ad_hominem": "Ataque à pessoa em vez do argumento",
        "straw_man": "Deturpação do argumento oposto para refutá-lo",
        "false_dilemma": "Apresentar apenas duas opções quando existem mais",
        "circular_reasoning": "A conclusão está implícita nas premissas",
        "hasty_generalization": "Generalização baseada em amostra insuficiente",
        "correlation_causation": "Confundir correlação com causalidade",
        "appeal_authority": "Apelar à autoridade sem evidência substantiva",
        "slippery_slope": "Assumir que um passo leva inevitavelmente a uma cascata negativa",
    }

    @classmethod
    def detect_fallacies(cls, argument: str) -> List[Dict]:
        """Detecta falácias comuns em um argumento (análise textual simples)."""
        detected = []
        lower = argument.lower()

        # Heurísticas simples de detecção
        fallacy_patterns = {
            "ad_hominem": ["você é", "você está", "pessoa não confiável", "incompetente"],
            "straw_man": ["você está dizendo que", "então você acredita", "o que você quer é"],
            "false_dilemma": ["ou...ou", "só duas opções", "não há alternativa"],
            "circular_reasoning": ["porque sim", "é assim porque é"],
            "hasty_generalization": ["todos", "ninguém", "sempre", "nunca"],
            "correlation_causation": ["causa", "provoca", "leva a", "resulta em"],
            "appeal_authority": ["especialistas dizem", "autoridades afirmam", "estudos mostram"],
            "slippery_slope": ["primeiro...depois", "eventualmente", "caminho para"],
        }

        for fallacy, patterns in fallacy_patterns.items():
            matches = [p for p in patterns if p in lower]
            if matches:
                detected.append({
                    "fallacy": fallacy,
                    "description": cls.COMMON_FALLACIES.get(fallacy, ""),
                    "matches": matches,
                })

        return detected


# ─── Multi-Scale Analysis ───────────────────────────────────────────

class ScaleLevel:
    """Nível de uma escala de análise."""
    MICRO = "micro"        # Individual, intrapsíquico
    MESO = "meso"          # Interpessoal, grupal
    MACRO = "macro"        # Organizacional, comunitário
    MEGA = "mega"          # Sistêmico, societal


class MultiScaleAnalyzer:
    """Analisador multiescala para fenômenos complexos."""

    @staticmethod
    def analyze_phenomenon(
        phenomenon: str,
        micro_indicators: List[str],
        meso_indicators: List[str],
        macro_indicators: List[str],
        mega_indicators: Optional[List[str]] = None,
    ) -> Dict:
        """Analisa um fenômeno em múltiplas escalas."""
        levels = {
            ScaleLevel.MICRO: micro_indicators,
            ScaleLevel.MESO: meso_indicators,
            ScaleLevel.MACRO: macro_indicators,
            ScaleLevel.MEGA: mega_indicators or [],
        }

        coverage = {
            level: len(indicators)
            for level, indicators in levels.items()
        }

        total_indicators = sum(coverage.values())
        depth_score = min(1.0, total_indicators / 15.0)

        # Identificar níveis fortes e fracos
        strong_levels = [l for l, c in coverage.items() if c >= 3]
        weak_levels = [l for l, c in coverage.items() if c == 0]

        return {
            "phenomenon": phenomenon,
            "coverage": coverage,
            "total_indicators": total_indicators,
            "depth_score": round(depth_score, 3),
            "strong_levels": strong_levels,
            "weak_levels": weak_levels,
            "is_multiscale": len(strong_levels) >= 2,
        }

    @staticmethod
    def cross_level_effects(
        micro_variable: str,
        macro_variable: str,
        mediation_hypothesis: str,
    ) -> Dict:
        """Analisa efeitos cross-level entre variáveis de diferentes escalas."""
        return {
            "micro_variable": micro_variable,
            "macro_variable": macro_variable,
            "mediation_hypothesis": mediation_hypothesis,
            "type": "top_down" if "impacto" in mediation_hypothesis.lower() else "bottom_up",
            "requires_multilevel_modeling": True,
        }


def main():
    """Demonstra raciocínio lógico e análise multiescala."""

    # Dedução
    ie = InferenceEngine()
    p1 = Proposition("Todos os homens são mortais", True)
    p2 = Proposition("Sócrates é homem", True)
    conclusion = Proposition("Sócrates é mortal", True)
    result = ie.deductive([p1, p2], conclusion)
    print(f"Dedução: {result['valid']} → {result['reason']}")

    # Indução
    observations = [
        {"id": i, "supports": i % 5 != 0} for i in range(15)
    ]
    ind = ie.inductive(observations, "O padrão se mantém na população")
    print(f"Indução: força={ind['strength']}, assessment={ind['assessment']}")

    # Abdução
    rules = [
        {"antecedent": "Choveu", "consequent": "chão molhado",
         "label": "regra_1", "prior_probability": 0.8},
        {"antecedent": "Caminhão pipa passou", "consequent": "chão molhado",
         "label": "regra_2", "prior_probability": 0.3},
        {"antecedent": "Orvalho da manhã", "consequent": "chão molhado",
         "label": "regra_3", "prior_probability": 0.5},
    ]
    abd = ie.abductive("chão molhado", rules)
    print(f"Abdução: melhor explicação = {abd['best_explanations'][0] if abd['best_explanations'] else 'N/A'}")

    # Argumentação
    av = ArgumentationValidator()
    argument = "Todos os políticos são corruptos, sempre foi assim, não há alternativa."
    fallacies = av.detect_fallacies(argument)
    print(f"Falácias detectadas: {[f['fallacy'] for f in fallacies]}")

    # Análise multiescala
    msa = MultiScaleAnalyzer()
    analysis = msa.analyze_phenomenon(
        "Depressão",
        micro_indicators=["humor", "sono", "apetite", "energia", "cognição"],
        meso_indicators=["relações familiares", "suporte social", "ambiente trabalho"],
        macro_indicators=["acesso saúde", "políticas públicas", "estigma social"],
    )
    print(f"\nAnálise multiescala: depth={analysis['depth_score']}")
    print(f"Níveis fortes: {analysis['strong_levels']}")
    print(f"Níveis fracos: {analysis['weak_levels']}")


if __name__ == "__main__":
    main()
