#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RupturePotentialIndex v1.0 — Índice de Potencial de Ruptura
================================================================
SPEC-055 — 2026-06-25 — Rupture Potential Index

Conceito original: Interlocutor Externo (HiddenGapTheory)
Implementacao: Marcelo Claro Laranjeira

Métrica complementar ao Epistemic Potential Score (EPS) para capturar
oportunidades de pesquisa com potencial assimétrico de risco-recompensa.

Fórmula:
    RPI = (DE × α₁ + FT × α₂ + RR × α₃ - CO × α₄) × 100

    DE = Distância Epistemológica (quão diferente do mainstream)
    FT = Fertilidade Teórica (quantas teorias conecta)
    RR = Risco-Recompensa (impacto × (1 - incerteza))
    CO = Custo de Oportunidade (penalidade por ignorar)

Matriz EPS × RPI:
    - Ruptura Segura:        EPS >= 60, RPI >= 60
    - Ruptura Especulativa:  EPS < 60,  RPI >= 60
    - Melhoria Incremental:  EPS >= 60, RPI < 60
    - Rotina:                EPS < 60,  RPI < 60
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


# ═══════════════════════════════════════════════════════════════════════
# CONSTANTES
# ═══════════════════════════════════════════════════════════════════════

DEFAULT_WEIGHTS: dict[str, float] = {
    "de": 0.30,   # Distância Epistemológica
    "ft": 0.25,   # Fertilidade Teórica
    "rr": 0.25,   # Risco-Recompensa
    "co": 0.20,   # Custo de Oportunidade (penalidade)
}

EPS_THRESHOLD: float = 60.0   # EPS >= 60 = viável
RPI_THRESHOLD: float = 60.0   # RPI >= 60 = ruptura

RPI_CLASSIFICATIONS: list[tuple[float, str]] = [
    (80, "rupture"),        # Pode redefinir o campo
    (60, "transformation"), # Muda significativamente
    (40, "expansion"),      # Preenche lacuna importante
    (0,  "increment"),      # Melhoria marginal
]


class DecisionQuadrant(Enum):
    """Quadrantes da matriz EPS × RPI."""
    RUPTURA_SEGURA = "ruptura_segura"
    RUPTURA_ESPECULATIVA = "ruptura_especulativa"
    MELHORIA_INCREMENTAL = "melhoria_incremental"
    ROTINA = "rotina"


# ═══════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class ResearchOpportunity:
    """Oportunidade de pesquisa com métricas de potencial."""
    opportunity_id: str
    label: str
    epistemic_distance: float      # DE [0, 1]
    fertility: float               # FT [0, 1]
    risk_reward: float             # RR [0, 1]
    cost_opportunity: float        # CO [0, 1] (penalidade)
    eps_score: float               # EPS [0, 100] (do PotentialityEstimator v2)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        # Validar ranges
        for attr in ["epistemic_distance", "fertility", "risk_reward", "cost_opportunity"]:
            val = getattr(self, attr)
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"{attr}={val} fora do intervalo [0, 1]")
        if not (0.0 <= self.eps_score <= 100.0):
            raise ValueError(f"eps_score={self.eps_score} fora do intervalo [0, 100]")


@dataclass
class RPIResult:
    """Resultado completo do cálculo de RPI."""
    opportunity_id: str
    rpi_score: float
    quadrant: DecisionQuadrant
    components: dict[str, float]
    classification: str
    recommendation: str


# ═══════════════════════════════════════════════════════════════════════
# RPI PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════

class RupturePotentialIndex:
    """
    Calcula o Índice de Potencial de Ruptura (RPI) para oportunidades
    de pesquisa, complementar ao EPS.

    Combina 4 dimensões (DE, FT, RR, CO) em score único e posiciona
    a oportunidade em uma matriz de decisão EPS × RPI.
    """

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = {**DEFAULT_WEIGHTS, **(weights or {})}
        self._opportunities: dict[str, ResearchOpportunity] = {}
        self._results: dict[str, RPIResult] = {}

    # ─── Propriedades ────────────────────────────────────────────────────

    @property
    def eps_threshold(self) -> float:
        return EPS_THRESHOLD

    @property
    def rpi_threshold(self) -> float:
        return RPI_THRESHOLD

    # ─── Registro de oportunidades ────────────────────────────────────────

    def register_opportunity(self, opportunity: ResearchOpportunity) -> None:
        """Registra uma oportunidade de pesquisa."""
        self._opportunities[opportunity.opportunity_id] = opportunity

    def opportunity_count(self) -> int:
        """Retorna o número de oportunidades registradas."""
        return len(self._opportunities)

    def get_opportunity(self, opp_id: str) -> ResearchOpportunity | None:
        """Retorna uma oportunidade pelo ID."""
        return self._opportunities.get(opp_id)

    def get_all_opportunities(self) -> list[ResearchOpportunity]:
        """Retorna todas as oportunidades."""
        return list(self._opportunities.values())

    def clear(self) -> None:
        """Limpa oportunidades e resultados."""
        self._opportunities.clear()
        self._results.clear()

    # ─── Cálculo do RPI ──────────────────────────────────────────────────

    def compute(self, opportunity_id: str) -> dict[str, Any]:
        """
        Calcula o RPI para uma oportunidade específica.

        Args:
            opportunity_id: ID da oportunidade registrada

        Returns:
            dict com rpi_score, quadrant, components, classification, recommendation
        """
        opp = self._opportunities.get(opportunity_id)
        if not opp:
            return {"error": f"Oportunidade {opportunity_id} nao encontrada"}

        # Componentes do RPI
        de_contribution = opp.epistemic_distance * self.weights.get("de", 0.30)
        ft_contribution = opp.fertility * self.weights.get("ft", 0.25)
        rr_contribution = opp.risk_reward * self.weights.get("rr", 0.25)
        co_contribution = opp.cost_opportunity * self.weights.get("co", 0.20)

        # RPI = (DE * α₁ + FT * α₂ + RR * α₃ - CO * α₄) * 100
        raw = (de_contribution + ft_contribution + rr_contribution - co_contribution)
        rpi_score = max(0.0, min(100.0, raw * 100))

        # Classificação qualitativa
        classification = self._classify_rpi(rpi_score)

        # Quadrante da matriz EPS × RPI
        quadrant = self._determine_quadrant(opp.eps_score, rpi_score)

        # Recomendação
        recommendation = self._generate_recommendation(quadrant, rpi_score)

        # Montar resultado completo
        components = {
            "de_contribution": round(de_contribution, 4),
            "ft_contribution": round(ft_contribution, 4),
            "rr_contribution": round(rr_contribution, 4),
            "co_contribution": round(co_contribution, 4),
            "epistemic_distance": opp.epistemic_distance,
            "fertility": opp.fertility,
            "risk_reward": opp.risk_reward,
            "cost_opportunity": opp.cost_opportunity,
            "eps_score": opp.eps_score,
        }

        result = {
            "opportunity_id": opportunity_id,
            "label": opp.label,
            "rpi_score": round(rpi_score, 2),
            "classification": classification,
            "quadrant": quadrant.value,
            "components": components,
            "recommendation": recommendation,
        }

        self._results[opportunity_id] = RPIResult(
            opportunity_id=opportunity_id,
            rpi_score=rpi_score,
            quadrant=quadrant,
            components=components,
            classification=classification,
            recommendation=recommendation,
        )

        return result

    def _classify_rpi(self, rpi_score: float) -> str:
        """Classifica o RPI qualitativamente."""
        for threshold, label in RPI_CLASSIFICATIONS:
            if rpi_score >= threshold:
                return label
        return "increment"

    def _determine_quadrant(self, eps: float, rpi: float) -> DecisionQuadrant:
        """Determina o quadrante na matriz EPS × RPI."""
        if eps >= EPS_THRESHOLD and rpi >= RPI_THRESHOLD:
            return DecisionQuadrant.RUPTURA_SEGURA
        elif eps < EPS_THRESHOLD and rpi >= RPI_THRESHOLD:
            return DecisionQuadrant.RUPTURA_ESPECULATIVA
        elif eps >= EPS_THRESHOLD and rpi < RPI_THRESHOLD:
            return DecisionQuadrant.MELHORIA_INCREMENTAL
        else:
            return DecisionQuadrant.ROTINA

    def _generate_recommendation(self, quadrant: DecisionQuadrant,
                                 rpi_score: float) -> str:
        """Gera recomendação textual baseada no quadrante."""
        recs = {
            DecisionQuadrant.RUPTURA_SEGURA: (
                f"EXECUTAR IMEDIATO: Oportunidade com alto potencial de ruptura (RPI={rpi_score:.1f}) "
                f"e viabilidade confirmada (EPS >= {EPS_THRESHOLD}). Alocar recursos prioritários."
            ),
            DecisionQuadrant.RUPTURA_ESPECULATIVA: (
                f"RESEARCH GRANT: Potencial de ruptura alto (RPI={rpi_score:.1f}) mas viabilidade "
                f"baixa (EPS < {EPS_THRESHOLD}). Recomendado: projeto exploratório com funding externo."
            ),
            DecisionQuadrant.MELHORIA_INCREMENTAL: (
                f"EXECUTAR CONDICIONAL: Viável (EPS >= {EPS_THRESHOLD}) mas baixo potencial de ruptura "
                f"(RPI={rpi_score:.1f}). Executar apenas se alinhado a roadmap de curto prazo."
            ),
            DecisionQuadrant.ROTINA: (
                f"BAIXA PRIORIDADE: Potencial de ruptura (RPI={rpi_score:.1f}) e viabilidade "
                f"(EPS < {EPS_THRESHOLD}) ambos baixos. Reavaliar em próximo ciclo."
            ),
        }
        return recs.get(quadrant, "Classificacao nao disponivel.")

    # ─── Portfolio ───────────────────────────────────────────────────────

    def compute_portfolio(self) -> dict[str, Any]:
        """
        Calcula RPI para todas as oportunidades registradas e gera
        portfólio diversificado.

        Returns:
            dict com lista de oportunidades, distribuição por quadrante
            e recomendações estratégicas
        """
        if not self._opportunities:
            return {"opportunities": [], "quadrant_distribution": {}, "error": "Nenhuma oportunidade"}

        results = []
        for opp_id in self._opportunities:
            result = self.compute(opp_id)
            if "error" not in result:
                results.append(result)

        # Distribuição por quadrante
        quadrant_dist: dict[str, int] = {}
        for r in results:
            q = r.get("quadrant", "unknown")
            quadrant_dist[q] = quadrant_dist.get(q, 0) + 1

        # Estratégia de portfólio
        strategy = self._generate_portfolio_strategy(quadrant_dist, results)

        return {
            "opportunities": sorted(results, key=lambda x: x.get("rpi_score", 0), reverse=True),
            "quadrant_distribution": quadrant_dist,
            "n_opportunities": len(results),
            "portfolio_strategy": strategy,
            "config": {
                "weights": dict(self.weights),
                "eps_threshold": EPS_THRESHOLD,
                "rpi_threshold": RPI_THRESHOLD,
            },
        }

    def _generate_portfolio_strategy(self, distribution: dict[str, int],
                                     results: list[dict]) -> str:
        """Gera recomendação estratégica para o portfólio."""
        n = len(results)
        if n == 0:
            return "Nenhuma oportunidade no portfólio."

        segura = distribution.get(DecisionQuadrant.RUPTURA_SEGURA.value, 0)
        especulativa = distribution.get(DecisionQuadrant.RUPTURA_ESPECULATIVA.value, 0)
        incremental = distribution.get(DecisionQuadrant.MELHORIA_INCREMENTAL.value, 0)
        rotina = distribution.get(DecisionQuadrant.ROTINA.value, 0)

        lines = [
            f"Portfolio de {n} oportunidades de pesquisa.",
            f"  - Ruptura Segura: {segura} ({segura * 100 // max(n, 1)}%)",
            f"  - Ruptura Especulativa: {especulativa} ({especulativa * 100 // max(n, 1)}%)",
            f"  - Melhoria Incremental: {incremental} ({incremental * 100 // max(n, 1)}%)",
            f"  - Rotina: {rotina} ({rotina * 100 // max(n, 1)}%)",
        ]

        # Recomendação de balanceamento
        if segura == 0 and especulativa == 0:
            lines.append("ALERTA: Nenhuma oportunidade de ruptura no portfólio. "
                        "Considere explorar alvos mais arriscados.")
        if especulativa > segura * 2:
            lines.append("CUIDADO: Portfolio com viés especulativo. "
                        "Balancear com oportunidades de EPS alto.")
        if incremental > segura * 3:
            lines.append("CUIDADO: Portfolio com viés incremental. "
                        "Buscar oportunidades de maior potencial de ruptura.")

        return "\n".join(lines)

    # ─── Export ───────────────────────────────────────────────────────────

    def to_json(self, indent: int = 2) -> str:
        """Exporta resultados para JSON."""
        export = {
            "weights": self.weights,
            "n_opportunities": len(self._opportunities),
            "results": {
                opp_id: {
                    "rpi_score": round(res.rpi_score, 2) if hasattr(res, 'rpi_score') else None,
                    "quadrant": res.quadrant.value if hasattr(res, 'quadrant') else None,
                }
                for opp_id, res in self._results.items()
            },
        }
        return json.dumps(export, indent=indent, default=str, ensure_ascii=False)

    def __repr__(self) -> str:
        return (f"RupturePotentialIndex("
                f"opportunities={len(self._opportunities)}, "
                f"results={len(self._results)})")
