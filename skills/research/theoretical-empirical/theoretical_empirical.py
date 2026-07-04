#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
theoretical_empirical.py — Framework Teórico e Validação Empírica
=================================================================
Implementa classificação ontológica/epistemológica, métricas de
validação empírica e síntese de literatura.

Capabilities:
  - theoretical_framework: Construção de marcos teóricos, conceituais e epistemológicos
  - empirical_validation: Validação empírica e experimental de constructos
"""

from __future__ import annotations
import math
import statistics
from typing import Dict, List, Optional, Tuple


# ─── Theoretical Framework ──────────────────────────────────────────

class EpistemologicalClassifier:
    """Classificador de posições epistemológicas e ontológicas."""

    EPISTEMOLOGIES = {
        "positivista": {
            "natureza_conhecimento": "objetivo_verificavel",
            "metodo_preferido": "quantitativo_experimental",
            "criteria_validacao": "falsificacao_confirmacao",
            "relacao_sujeito_objeto": "separacao_rigida",
        },
        "interpretativista": {
            "natureza_conhecimento": "subjetivo_construido",
            "metodo_preferido": "qualitativo_interpretativo",
            "criteria_validacao": "credibilidade_transferibilidade",
            "relacao_sujeito_objeto": "interacao_dialetica",
        },
        "pragmatista": {
            "natureza_conhecimento": "instrumental_utilidade",
            "metodo_preferido": "metodos_mistos",
            "criteria_validacao": "aplicabilidade_pratica",
            "relacao_sujeito_objeto": "relacao_contextual",
        },
        "critico": {
            "natureza_conhecimento": "emancipatorio_transformador",
            "metodo_preferido": "pesquisa_acao_critica",
            "criteria_validacao": "conscientizacao_mudanca",
            "relacao_sujeito_objeto": "engajamento_transformador",
        },
        "complexo": {
            "natureza_conhecimento": "multidimensional_sistemico",
            "metodo_preferido": "abordagem_multirreferencial",
            "criteria_validacao": "coerencia_emergencia",
            "relacao_sujeito_objeto": "inclusao_observador",
        },
    }

    @classmethod
    def classify(cls, epistemology: str) -> Optional[Dict[str, str]]:
        """Classifica uma posição epistemológica."""
        key = epistemology.lower().strip()
        if key in cls.EPISTEMOLOGIES:
            result = cls.EPISTEMOLOGIES[key].copy()
            result["nome"] = epistemology
            return result
        return None

    @classmethod
    def compare(cls, ep1: str, ep2: str) -> Dict[str, List[str]]:
        """Compara duas epistemologias."""
        c1 = cls.classify(ep1)
        c2 = cls.classify(ep2)
        if not c1 or not c2:
            return {"error": ["Epistemologia não reconhecida"]}

        similarities = []
        differences = []
        for key in c1:
            if key == "nome":
                continue
            if c1[key] == c2[key]:
                similarities.append(f"{key}: {c1[key]}")
            else:
                differences.append(f"{key}: {c1[key]} vs {c2[key]}")

        return {
            "ep1": ep1,
            "ep2": ep2,
            "similarities": similarities,
            "differences": differences,
            "compatibility": "alta" if len(similarities) > len(differences) else "moderada",
        }


class TheoreticalFrameworkBuilder:
    """Construtor de marcos teóricos."""

    @staticmethod
    def build_framework(
        phenomenon: str,
        epistemology: str,
        key_concepts: List[str],
        references: List[Dict[str, str]],
    ) -> Dict:
        """Constrói estrutura de marco teórico."""
        ep_info = EpistemologicalClassifier.classify(epistemology) or {}

        return {
            "phenomenon": phenomenon,
            "epistemology": {
                "name": epistemology,
                "characteristics": ep_info,
            },
            "conceptual_network": {
                "central_concepts": key_concepts,
                "n_concepts": len(key_concepts),
            },
            "references": [
                {
                    "author": ref.get("author", ""),
                    "year": ref.get("year", ""),
                    "contribution": ref.get("contribution", ""),
                }
                for ref in references
            ],
            "coherence_score": _calculate_coherence(
                epistemology, key_concepts
            ),
        }


def _calculate_coherence(epistemology: str, concepts: List[str]) -> float:
    """Calcula coerência teórica (0-1)."""
    if not concepts:
        return 0.0
    # Quanto mais conceitos, maior a densidade teórica (diminishing returns)
    density = min(1.0, len(concepts) / 7.0)
    # Epistemologias bem definidas ganham bônus
    ep_bonus = 0.2 if epistemology.lower() in EpistemologicalClassifier.EPISTEMOLOGIES else 0.0
    return min(1.0, density * 0.8 + ep_bonus)


# ─── Empirical Validation ───────────────────────────────────────────

class ReliabilityAnalyzer:
    """Analisador de confiabilidade/consistência interna."""

    @staticmethod
    def cronbach_alpha(items: List[List[float]]) -> float:
        """Calcula o Alpha de Cronbach para consistência interna."""
        if len(items) < 2 or len(items[0]) < 2:
            return 0.0

        n_items = len(items)
        n_subjects = len(items[0])

        # Variância de cada item
        item_vars = [statistics.variance(items[i]) for i in range(n_items)]

        # Variância do total
        totals = [sum(items[i][j] for i in range(n_items)) for j in range(n_subjects)]
        total_var = statistics.variance(totals)

        sum_item_vars = sum(item_vars)

        if total_var <= 0:
            return 0.0

        alpha = (n_items / (n_items - 1)) * (1 - sum_item_vars / total_var)
        # Alpha negativo = itens não medem o mesmo construto → clampa a 0
        return max(0.0, min(1.0, alpha))

    @staticmethod
    def interpret_alpha(alpha: float) -> str:
        """Interpreta o valor do Alpha de Cronbach."""
        if alpha >= 0.90:
            return "excelente"
        elif alpha >= 0.80:
            return "bom"
        elif alpha >= 0.70:
            return "aceitavel"
        elif alpha >= 0.60:
            return "questionavel"
        else:
            return "inaceitavel"


class EffectSizeCalculator:
    """Calculadora de tamanho de efeito."""

    @staticmethod
    def cohens_d(
        mean1: float, mean2: float,
        sd1: float, sd2: float,
        n1: Optional[int] = None, n2: Optional[int] = None,
    ) -> Dict[str, float]:
        """Calcula o d de Cohen."""
        if sd1 < 0 or sd2 < 0:
            raise ValueError("Desvios padrão não podem ser negativos")

        # Pooled standard deviation
        if n1 and n2:
            pooled_sd = math.sqrt(((n1 - 1) * sd1**2 + (n2 - 1) * sd2**2) / (n1 + n2 - 2))
        else:
            pooled_sd = math.sqrt((sd1**2 + sd2**2) / 2)

        if pooled_sd == 0:
            return {"d": 0.0, "interpretation": "sem_efeito"}

        d = (mean1 - mean2) / pooled_sd

        # Interpretação
        ad = abs(d)
        if ad < 0.2:
            interp = "sem_efeito"
        elif ad < 0.5:
            interp = "pequeno"
        elif ad < 0.8:
            interp = "medio"
        else:
            interp = "grande"

        return {"d": round(d, 4), "interpretation": interp}

    @staticmethod
    def pearson_r_to_d(r: float) -> float:
        """Converte correlação de Pearson para d de Cohen."""
        r = max(-0.999, min(0.999, r))
        return 2 * r / math.sqrt(1 - r**2)


def validate_empirical(
    data: Dict,
) -> Dict:
    """Pipeline de validação empírica."""
    results = {}

    if "reliability_items" in data:
        ra = ReliabilityAnalyzer()
        alpha = ra.cronbach_alpha(data["reliability_items"])
        results["cronbach_alpha"] = round(alpha, 4)
        results["reliability"] = ra.interpret_alpha(alpha)

    if "effect_size" in data:
        es = data["effect_size"]
        esc = EffectSizeCalculator()
        d_result = esc.cohens_d(
            es.get("mean1", 0), es.get("mean2", 0),
            es.get("sd1", 1), es.get("sd2", 1),
            es.get("n1"), es.get("n2"),
        )
        results["cohens_d"] = d_result

        if "r" in es:
            d_from_r = esc.pearson_r_to_d(es["r"])
            results["d_from_pearson_r"] = round(d_from_r, 4)

    return results


def main():
    """Demonstra análise teórico-empírica."""

    # Classificação epistemológica
    ec = EpistemologicalClassifier()
    for ep in ["positivista", "interpretativista", "pragmatista"]:
        info = ec.classify(ep)
        print(f"{ep}: {info['natureza_conhecimento'] if info else 'desconhecido'}")

    # Comparação
    comp = ec.compare("positivista", "interpretativista")
    print(f"\nSimilaridades: {comp['similarities']}")
    print(f"Diferenças: {comp['differences']}")

    # Alpha de Cronbach
    ra = ReliabilityAnalyzer()
    items = [
        [4, 5, 3, 4, 5, 4, 3, 4, 5, 4],  # item 1
        [3, 4, 4, 3, 5, 4, 4, 3, 4, 5],  # item 2
        [4, 4, 5, 4, 3, 4, 5, 4, 4, 3],  # item 3
        [5, 4, 3, 5, 4, 3, 4, 5, 3, 4],  # item 4
    ]
    alpha = ra.cronbach_alpha(items)
    print(f"\nAlpha de Cronbach: {alpha:.4f} → {ra.interpret_alpha(alpha)}")

    # Tamanho de efeito
    esc = EffectSizeCalculator()
    d = esc.cohens_d(mean1=15.2, mean2=12.8, sd1=3.5, sd2=4.1, n1=30, n2=30)
    print(f"d de Cohen: {d['d']} → {d['interpretation']}")


if __name__ == "__main__":
    main()
