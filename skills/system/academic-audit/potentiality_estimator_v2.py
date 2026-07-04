#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PotentialityEstimatorV2.0 — Epistemic Opportunity Ranker (SPEC-045)
====================================================================
Evolucao: ERRO -> AUSENCIA -> OPORTUNIDADE -> POTENCIAL (v4)

Consolida entradas de 5 scanners:
  1. NoologicalScanner (SPEC-028) — ausencias
  2. TeleologicalReverseScanner (SPEC-029) — gaps teleologicos
  3. EvolutionaryScannerPipeline (SPEC-030) — dependencias + analogias
  4. PotentialityScanner (SPEC-043) — DNA estrutural
  5. SocialImpactScanner (SPEC-044) — relevancia social

Formula EPS v2 (6 dimensoes):
  EPS = (CDI×0.25 + TF×0.20 + GTV×0.15 + TA×0.20 + CI×0.10 + SI×0.10) × 100

Output: Ranking priorizado de oportunidades com viabilidade e roadmap.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BRAZIL_TZ = timezone.utc


# ═══════════════════════════════════════════════════════════════════════
# DATA CLASSES
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class EpistemicOpportunity:
    """Uma oportunidade de pesquisa priorizada por potencial epistemico."""
    dimension: str
    category: str
    eps: float               # Epistemological Potential Score (0-100)
    grade: str               # Discovery | Promising | Exploratory | Marginal
    cross_domain_impact: float   # 0-10
    theoretical_fertility: float # 0-10
    game_theoretic_value: float  # 0-10
    teleological_alignment: float  # 0-10 (NOVO v2)
    cascade_impact: float        # 0-10 (NOVO v2)
    social_impact: float         # 0-10 (NOVO v2)
    feasibility: str = "unknown"  # viable | needs_development | unviable
    rationale: str = ""
    suggested_method: str = ""
    expected_contribution: str = ""
    source_scanners: list[str] = field(default_factory=list)


@dataclass
class FeasibilityResult:
    """Resultado da validacao de viabilidade de uma oportunidade."""
    opportunity_category: str
    feasible: bool
    status: str  # viable | needs_development | unviable
    dna_match: bool = False
    capabilities_present: list[str] = field(default_factory=list)
    capabilities_missing: list[str] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class ResearchRoadmap:
    """Roadmap de pesquisa com rotas priorizadas."""
    title: str
    routes: list[RoadmapRoute] = field(default_factory=list)
    total_opportunities: int = 0
    discovery_count: int = 0
    promising_count: int = 0
    generated_at: str = ""


@dataclass
class RoadmapRoute:
    """Uma rota no roadmap de pesquisa."""
    name: str
    description: str
    opportunities: list[EpistemicOpportunity] = field(default_factory=list)
    estimated_impact: float = 0.0
    estimated_effort: str = ""  # low | medium | high


# ═══════════════════════════════════════════════════════════════════════
# DIMENSION MATRICES (EPS v2)
# ═══════════════════════════════════════════════════════════════════════

CROSS_DOMAIN_IMPACT: dict[str, int] = {
    "teoria_jogos": 8,
    "paradigmas": 7,
    "metodos": 6,
    "dominios": 6,
    "raciocinio": 5,
    "dados": 5,
    "niveis_analise": 4,
    "temporalidade": 3,
    "populacao": 3,
    "teorias": 2,
}

THEORETICAL_FERTILITY: dict[str, dict[str, int]] = {
    "teoria_jogos": {"default": 8},
    "paradigmas": {"default": 7},
    "dominios": {"default": 7},
    "metodos": {"default": 6},
    "raciocinio": {"default": 6},
    "dados": {"default": 5},
    "default": {"default": 4},
}

GAME_THEORETIC_VALUE: dict[str, int] = {
    "teoria_jogos": 10,
    "paradigmas": 7,
    "dominios": 8,
    "metodos": 6,
    "raciocinio": 5,
    "default": 4,
}


# ═══════════════════════════════════════════════════════════════════════
# ESTIMATOR V2
# ═══════════════════════════════════════════════════════════════════════

class PotentialityEstimatorV2:
    """Estimador de potencial epistemico v2.0 — 6 dimensoes.

    Consolida entradas de 5 scanners para calcular o EPS v2
    e gerar ranking priorizado com validacao de viabilidade.

    Uso:
        estimator = PotentialityEstimatorV2()
        result = estimator.scan(
            noological_results=...,
            teleological_results=...,
            evolutionary_results=...,
            dna_results=...,
            social_impact_results=...,
        )
        print(result["summary"])
    """

    WEIGHTS = {
        "cross_domain": 0.25,
        "theoretical_fertility": 0.20,
        "game_theoretic": 0.15,
        "teleological_alignment": 0.20,
        "cascade_impact": 0.10,
        "social_impact": 0.10,
    }

    def estimate(
        self,
        noological_results: dict[str, Any] | None = None,
        teleological_results: dict[str, Any] | None = None,
        evolutionary_results: dict[str, Any] | None = None,
        dna_results: dict[str, Any] | None = None,
        social_impact_results: dict[str, Any] | None = None,
        cds_results: dict[str, Any] | None = None,
        etm_results: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Alias para scan() para manter compatibilidade com a API legada (v1)."""
        return self.scan(
            noological_results=noological_results,
            teleological_results=teleological_results,
            evolutionary_results=evolutionary_results,
            dna_results=dna_results,
            social_impact_results=social_impact_results,
            cds_results=cds_results,
            etm_results=etm_results
        )

    def scan(
        self,
        noological_results: dict[str, Any] | None = None,
        teleological_results: dict[str, Any] | None = None,
        evolutionary_results: dict[str, Any] | None = None,
        dna_results: dict[str, Any] | None = None,
        social_impact_results: dict[str, Any] | None = None,
        cds_results: dict[str, Any] | None = None,
        etm_results: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Executa scan completo de potencial epistemico.

        Agora com integracao SPEC-053 (CDS) e SPEC-054 (ETM)
        para enriquecer o calculo com diversidade cognitiva e topologia.

        Returns:
            Dict com opportunities, summary, feasibility, roadmap, rpi_portfolio
        """
        noological_results = noological_results or {}
        teleological_results = teleological_results or {}
        evolutionary_results = evolutionary_results or {}
        dna_results = dna_results or {}
        social_impact_results = social_impact_results or {}
        cds_results = cds_results or {}
        etm_results = etm_results or {}

        # F1: Consolidar ausencias
        absences = self._consolidate_absences(
            noological_results, teleological_results, evolutionary_results
        )

        # F2: Calcular EPS v2 para cada ausencia
        opportunities = []
        for absence in absences:
            opp = self._estimate_epv2(
                absence, teleological_results, evolutionary_results,
                social_impact_results
            )
            opportunities.append(opp)

        # F3: Validar viabilidade
        feasibility = {}
        for opp in opportunities:
            feas = self._check_feasibility(opp, dna_results)
            opp.feasibility = feas.status
            feasibility[opp.category] = feas

        # Ordenar por EPS decrescente
        opportunities.sort(key=lambda x: x.eps, reverse=True)

        # F4 + F5: Gerar roadmap
        roadmap = self._generate_roadmap(opportunities)

        # ═══ NOVO: RPI (SPEC-055) como métrica complementar ═══
        rpi_portfolio = self._compute_rpi_portfolio(
            opportunities, cds_results, etm_results
        )

        # Summary
        summary = self._build_summary(opportunities, feasibility)

        # Enriquecer summary com RPI
        rpi_summary = rpi_portfolio.get("quadrant_distribution", {})
        summary["rpi_distribution"] = rpi_summary
        summary["rupture_segura"] = rpi_summary.get("ruptura_segura", 0)
        summary["rupture_especulativa"] = rpi_summary.get("ruptura_especulativa", 0)

        return {
            "opportunities": opportunities,
            "summary": summary,
            "feasibility": feasibility,
            "roadmap": roadmap,
            "rpi_portfolio": rpi_portfolio,
        }

    def _compute_rpi_portfolio(
        self,
        opportunities: list[EpistemicOpportunity],
        cds_results: dict[str, Any],
        etm_results: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Calcula portfólio RPI (SPEC-055) a partir das oportunidades EPS.
        Usa diversidade cognitiva (CDS) e topologia (ETM) para estimar
        parâmetros DE, FT, RR, CO.
        """
        from rupture_potential_index import RupturePotentialIndex, ResearchOpportunity

        rpi = RupturePotentialIndex()
        n_opps = len(opportunities)

        # HI global para ajuste fino
        global_hi = cds_results.get("global_hi", 0.5)

        # Fator de diversidade: clusters isolados = maior DE
        n_islands = len(etm_results.get("islands", []))
        n_holes = len(etm_results.get("holes", []))

        for i, opp in enumerate(opportunities[:30]):  # max 30 para performance
            # DE: baseado em cross_domain_impact + fator de isolamento
            de = min(1.0, opp.cross_domain_impact / 10.0 + n_islands * 0.02)

            # FT: theoretical_fertility + ajuste de diversidade
            ft = min(1.0, opp.theoretical_fertility / 10.0 * (1.0 + (1.0 - global_hi) * 0.2))

            # RR: game_theoretic_value + cascade_impact
            rr = min(1.0, (opp.game_theoretic_value + opp.cascade_impact) / 20.0)

            # CO: teleological_alignment inverso + fator de buracos
            co = min(1.0, max(0.0, 1.0 - opp.teleological_alignment / 10.0 + n_holes * 0.01))

            rpi_opp = ResearchOpportunity(
                opportunity_id=f"eps_rpi_{i}",
                label=f"{opp.dimension}: {opp.category}",
                epistemic_distance=round(de, 3),
                fertility=round(ft, 3),
                risk_reward=round(rr, 3),
                cost_opportunity=round(co, 3),
                eps_score=opp.eps,
            )
            rpi.register_opportunity(rpi_opp)

        portfolio = rpi.compute_portfolio()

        # Anotar oportunidades originais com RPI (usando setattr, EpistemicOpportunity nao tem metadata)
        rpi_results = portfolio.get("opportunities", [])
        for i, opp in enumerate(opportunities[:len(rpi_results)]):
            if i < len(rpi_results):
                rpi_data = rpi_results[i]
                setattr(opp, "rpi_score", rpi_data.get("rpi_score", 0))
                setattr(opp, "rpi_quadrant", rpi_data.get("quadrant", "unknown"))

        return portfolio

    def _consolidate_absences(
        self,
        noological: dict[str, Any],
        teleological: dict[str, Any],
        evolutionary: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """F1: Consolida ausencias de multiplos scanners."""
        absences = []

        # Do NoologicalScanner
        for dim_key, dim_data in noological.get("dimensions", {}).items():
            for category in dim_data.get("absent", []):
                absences.append({
                    "dimension": dim_key,
                    "category": category,
                    "density": dim_data.get("density", 0),
                    "source": "noological",
                })

        # Do TeleologicalScanner (gaps)
        for gap in teleological.get("gaps", []):
            absences.append({
                "dimension": gap.get("dimension", "unknown"),
                "category": gap.get("category", "unknown"),
                "density": 0.0,
                "source": "teleological",
                "severity": gap.get("severity", "medium"),
            })

        # Do EvolutionaryPipeline (bottlenecks como ausencias)
        for bottleneck in evolutionary.get("bottlenecks", []):
            absences.append({
                "dimension": bottleneck.get("dimension", "unknown"),
                "category": bottleneck.get("category", "unknown"),
                "density": 0.0,
                "source": "evolutionary",
                "cascade_impact": bottleneck.get("cascade_impact", 0),
            })

        # Deduplicar por (dimension, category)
        seen = set()
        unique = []
        for a in absences:
            key = (a["dimension"], a["category"])
            if key not in seen:
                seen.add(key)
                unique.append(a)

        return unique

    def _estimate_epv2(
        self,
        absence: dict[str, Any],
        teleological: dict[str, Any],
        evolutionary: dict[str, Any],
        social_impact: dict[str, Any],
    ) -> EpistemicOpportunity:
        """F2: Calcula EPS v2 com 6 dimensoes."""
        dim = absence["dimension"]
        cat = absence["category"]

        # 1. Cross-Domain Impact (0-10)
        cdi = float(min(10, CROSS_DOMAIN_IMPACT.get(dim, 3)))

        # 2. Theoretical Fertility (0-10)
        tf_map = THEORETICAL_FERTILITY.get(dim, THEORETICAL_FERTILITY["default"])
        tf = float(tf_map.get("default", 4))

        # 3. Game-Theoretic Value (0-10)
        gtv = float(GAME_THEORETIC_VALUE.get(dim, GAME_THEORETIC_VALUE["default"]))

        # 4. Teleological Alignment (0-10) — NOVO v2
        ta = self._calc_teleological_alignment(dim, cat, teleological)

        # 5. Cascade Impact (0-10) — NOVO v2
        ci = self._calc_cascade_impact(dim, cat, evolutionary)

        # 6. Social Impact (0-10) — NOVO v2
        si = self._calc_social_impact(dim, cat, social_impact)

        # EPS v2
        eps = (
            cdi * self.WEIGHTS["cross_domain"] +
            tf * self.WEIGHTS["theoretical_fertility"] +
            gtv * self.WEIGHTS["game_theoretic"] +
            ta * self.WEIGHTS["teleological_alignment"] +
            ci * self.WEIGHTS["cascade_impact"] +
            si * self.WEIGHTS["social_impact"]
        ) * 10  # escala 0-100

        eps = round(min(100, max(0, eps)), 1)

        # Grade
        if eps >= 80:
            grade = "Discovery"
        elif eps >= 60:
            grade = "Promising"
        elif eps >= 40:
            grade = "Exploratory"
        else:
            grade = "Marginal"

        # Fontes
        sources = list({absence.get("source", "noological")})

        return EpistemicOpportunity(
            dimension=dim,
            category=cat,
            eps=eps,
            grade=grade,
            cross_domain_impact=cdi,
            theoretical_fertility=tf,
            game_theoretic_value=gtv,
            teleological_alignment=ta,
            cascade_impact=ci,
            social_impact=si,
            rationale=self._generate_rationale(dim, cat, cdi, tf, gtv, ta, ci, si),
            suggested_method=self._suggest_method(dim, cat),
            expected_contribution=self._expected_contribution(eps),
            source_scanners=sources,
        )

    def _calc_teleological_alignment(
        self, dim: str, cat: str, teleological: dict[str, Any]
    ) -> float:
        """Calcula alinhamento teleologico (0-10)."""
        goals = teleological.get("goals", [])
        if not goals:
            return 5.0  # neutro se sem dados teleologicos

        # Verificar se a dimensao/categoria se conecta a algum objetivo
        alignment = 0.0
        for goal in goals:
            goal_dims = goal.get("required_dimensions", [])
            if dim in goal_dims:
                alignment = max(alignment, 8.0)
            elif any(kw in cat.lower() for kw in goal.get("keywords", [])):
                alignment = max(alignment, 6.0)

        return max(3.0, alignment) if alignment > 0 else 5.0

    def _calc_cascade_impact(
        self, dim: str, cat: str, evolutionary: dict[str, Any]
    ) -> float:
        """Calcula impacto cascata (0-10)."""
        bottlenecks = evolutionary.get("bottlenecks", [])
        for bn in bottlenecks:
            if bn.get("dimension") == dim and bn.get("category") == cat:
                return float(min(10, bn.get("cascade_impact", 3)))

        # Heuristica: dimensoes com mais conexoes tem maior cascade
        base = CROSS_DOMAIN_IMPACT.get(dim, 3)
        return float(min(10, base * 0.8))

    def _calc_social_impact(
        self, dim: str, cat: str, social_impact: dict[str, Any]
    ) -> float:
        """Calcula impacto social (0-10)."""
        score = social_impact.get("consolidated_score", 0)
        if score >= 80:
            return 9.0
        elif score >= 60:
            return 7.0
        elif score >= 40:
            return 5.0
        elif score > 0:
            return 3.0

        # Heuristica: temas com relevancia social direta
        social_keywords = [
            "saude", "educacao", "pobreza", "desigualdade", "genero",
            "clima", "agua", "energia", "trabalho", "comunidade",
        ]
        if any(kw in cat.lower() for kw in social_keywords):
            return 7.0
        return 4.0  # neutro

    def _check_feasibility(
        self, opp: EpistemicOpportunity, dna_results: dict[str, Any]
    ) -> FeasibilityResult:
        """F3: Valida viabilidade estrutural."""
        cap_map = dna_results.get("capability_map", {})

        # Construir set de todas as capabilities presentes (cap_map tem skills como keys,
        # capabilities como values — precisamos verificar nos values, não nas keys)
        present_capabilities: set[str] = set()
        for caps_list in cap_map.values():
            if isinstance(caps_list, list):
                present_capabilities.update(caps_list)
            elif isinstance(caps_list, str):
                present_capabilities.add(caps_list)

        # Verificar se capacidades relacionadas existem
        present = []
        missing = []

        related_caps = self._get_related_capabilities(opp.dimension)
        for cap in related_caps:
            if cap in present_capabilities:
                present.append(cap)
            else:
                missing.append(cap)

        if not related_caps:
            # Sem mapeamento = needs_development
            return FeasibilityResult(
                opportunity_category=opp.category,
                feasible=False,
                status="needs_development",
                reasoning="Sem capacidades mapeadas para esta dimensao",
            )

        match_ratio = len(present) / len(related_caps) if related_caps else 0

        if match_ratio >= 0.7:
            status = "viable"
            feasible = True
        elif match_ratio >= 0.3:
            status = "needs_development"
            feasible = False
        else:
            status = "unviable"
            feasible = False

        return FeasibilityResult(
            opportunity_category=opp.category,
            feasible=feasible,
            status=status,
            dna_match=match_ratio > 0,
            capabilities_present=present,
            capabilities_missing=missing,
            reasoning=f"{len(present)}/{len(related_caps)} capacidades presentes",
        )

    def _get_related_capabilities(self, dimension: str) -> list[str]:
        """Mapeia dimensao para capacidades relacionadas no DNA."""
        mapping = {
            "teoria_jogos": ["game_theory_modeling", "equilibrium_analysis"],
            "paradigmas": ["paradigm_analysis", "theoretical_framework"],
            "metodos": ["methodology_design", "empirical_validation"],
            "dominios": ["interdisciplinary_synthesis", "cross_domain_mapping"],
            "raciocinio": ["reasoning_engine", "logical_inference"],
            "dados": ["data_collection", "statistical_analysis"],
            "niveis_analise": ["multi_scale_analysis", "hierarchical_modeling"],
            "temporalidade": ["temporal_modeling", "longitudinal_analysis"],
            "populacao": ["population_generalization", "sampling_design"],
            "teorias": ["theoretical_integration", "literature_synthesis"],
        }
        return mapping.get(dimension, [])

    def _generate_rationale(
        self, dim: str, cat: str, cdi: float, tf: float, gtv: float,
        ta: float, ci: float, si: float
    ) -> str:
        """Gera justificativa para a pontuacao."""
        parts = []
        if cdi >= 7:
            parts.append(f"Alto impacto interdisciplinar ({cdi}/10)")
        if tf >= 7:
            parts.append(f"Alta fertilidade teorica ({tf}/10)")
        if gtv >= 7:
            parts.append("Potencial de mudanca estrategica")
        if ta >= 7:
            parts.append(f"Forte alinhamento teleologico ({ta}/10)")
        if ci >= 7:
            parts.append(f"Alto impacto cascata ({ci}/10)")
        if si >= 7:
            parts.append(f"Alto impacto social ({si}/10)")
        if not parts:
            parts.append("Oportunidade de pesquisa incremental")
        return ". ".join(parts)

    def _suggest_method(self, dim: str, cat: str) -> str:
        """Sugere metodo de investigacao."""
        method_map = {
            "teoria_jogos": "Modelagem formal + simulacao computacional",
            "paradigmas": "Ensaio teorico + analise comparativa",
            "metodos": "Estudo metodologico com validacao empirica",
            "dominios": "Revisao sistematica interdisciplinar",
            "dados": "Coleta e analise de dados primarios",
            "raciocinio": "Estudo de caso com multiplos frameworks",
        }
        return method_map.get(dim, "Estudo exploratorio com triangulacao")

    def _expected_contribution(self, eps: float) -> str:
        """Estima a contribuicao esperada."""
        if eps >= 80:
            return "Potencial de abrir nova linha de pesquisa"
        if eps >= 60:
            return "Contribuicao significativa para a area"
        if eps >= 40:
            return "Complementacao relevante ao campo"
        return "Refinamento incremental"

    def _generate_roadmap(
        self, opportunities: list[EpistemicOpportunity]
    ) -> ResearchRoadmap:
        """F5: Gera roadmap de pesquisa."""
        routes = []

        # Rota 1: Descobertas (Discovery)
        discoveries = [o for o in opportunities if o.grade == "Discovery"]
        if discoveries:
            routes.append(RoadmapRoute(
                name="Linha de Descoberta",
                description="Oportunidades com maior potencial de abertura de nova pesquisa",
                opportunities=discoveries,
                estimated_impact=sum(o.eps for o in discoveries) / len(discoveries),
                estimated_effort="high",
            ))

        # Rota 2: Promissoras (Promising)
        promising = [o for o in opportunities if o.grade == "Promising"]
        if promising:
            routes.append(RoadmapRoute(
                name="Linha Promissora",
                description="Oportunidades com potencial significativo de contribuicao",
                opportunities=promising,
                estimated_impact=sum(o.eps for o in promising) / len(promising),
                estimated_effort="medium",
            ))

        # Rota 3: Exploratoria (Exploratory)
        exploratory = [o for o in opportunities if o.grade == "Exploratory"]
        if exploratory:
            routes.append(RoadmapRoute(
                name="Linha Exploratoria",
                description="Oportunidades de complementacao ao campo",
                opportunities=exploratory,
                estimated_impact=sum(o.eps for o in exploratory) / len(exploratory),
                estimated_effort="low",
            ))

        return ResearchRoadmap(
            title="Roadmap de Pesquisa Epistemica",
            routes=routes,
            total_opportunities=len(opportunities),
            discovery_count=len(discoveries),
            promising_count=len(promising),
            generated_at=datetime.now(BRAZIL_TZ).isoformat(),
        )

    def _build_summary(
        self,
        opportunities: list[EpistemicOpportunity],
        feasibility: dict[str, FeasibilityResult],
    ) -> dict[str, Any]:
        """Constroi resumo executivo."""
        viable = sum(1 for f in feasibility.values() if f.status == "viable")
        needs_dev = sum(1 for f in feasibility.values() if f.status == "needs_development")
        unviable = sum(1 for f in feasibility.values() if f.status == "unviable")

        return {
            "total_opportunities": len(opportunities),
            "discovery": sum(1 for o in opportunities if o.grade == "Discovery"),
            "promising": sum(1 for o in opportunities if o.grade == "Promising"),
            "exploratory": sum(1 for o in opportunities if o.grade == "Exploratory"),
            "marginal": sum(1 for o in opportunities if o.grade == "Marginal"),
            "feasibility": {
                "viable": viable,
                "needs_development": needs_dev,
                "unviable": unviable,
            },
            "avg_eps": round(
                sum(o.eps for o in opportunities) / len(opportunities), 1
            ) if opportunities else 0,
            "top_opportunity": {
                "dimension": opportunities[0].dimension,
                "category": opportunities[0].category,
                "eps": opportunities[0].eps,
            } if opportunities else None,
        }

    # ═══════════════════════════════════════════════════════════════════
    # REPORT GENERATION
    # ═══════════════════════════════════════════════════════════════════

    def generate_report(self, result: dict[str, Any]) -> str:
        """Gera relatorio Markdown completo."""
        opps = result["opportunities"]
        summary = result["summary"]
        roadmap = result["roadmap"]

        lines = [
            "# Relatorio de Potencial Epistemico v2.0",
            "",
            f"**Data**: {datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M')}",
            f"**Especificacao**: SPEC-045",
            f"**Total de oportunidades**: {summary['total_opportunities']}",
            "",
            "---",
            "",
            "## Resumo Executivo",
            "",
            f"| Metrica | Valor |",
            f"|---------|-------|",
            f"| Discovery | {summary['discovery']} |",
            f"| Promising | {summary['promising']} |",
            f"| Exploratory | {summary['exploratory']} |",
            f"| Marginal | {summary['marginal']} |",
            f"| EPS Medio | {summary['avg_eps']} |",
            f"| Viaveis | {summary['feasibility']['viable']} |",
            f"| Em desenvolvimento | {summary['feasibility']['needs_development']} |",
            f"| Inviaveis | {summary['feasibility']['unviable']} |",
            "",
            "---",
            "",
            "## Ranking de Oportunidades (EPS v2)",
            "",
            "| # | EPS | Grade | Dimensao | Categoria | CDI | TF | GTV | TA | CI | SI | Viabilidade |",
            "|:--:|:---:|:-----:|----------|-----------|:---:|:--:|:---:|:--:|:--:|:--:|:-----------:|",
        ]

        for i, opp in enumerate(opps[:20], 1):
            grade_icon = {
                "Discovery": "D",
                "Promising": "P",
                "Exploratory": "E",
                "Marginal": "M",
            }.get(opp.grade, "?")
            feas_icon = {
                "viable": "V",
                "needs_development": "?",
                "unviable": "X",
            }.get(opp.feasibility, "?")
            lines.append(
                f"| {i} | **{opp.eps}** | {grade_icon} | {opp.dimension[:20]} | "
                f"{opp.category[:25]} | {opp.cross_domain_impact:.0f} | "
                f"{opp.theoretical_fertility:.0f} | {opp.game_theoretic_value:.0f} | "
                f"{opp.teleological_alignment:.0f} | {opp.cascade_impact:.0f} | "
                f"{opp.social_impact:.0f} | {feas_icon} |"
            )

        # Roadmap
        lines.extend(["", "---", "", "## Roadmap de Pesquisa", ""])
        for route in roadmap.routes:
            lines.extend([
                f"### {route.name}",
                f"**Impacto estimado**: {route.estimated_impact:.1f}/100 | "
                f"**Esforco**: {route.estimated_effort}",
                f"",
                f"{route.description}",
                f"",
            ])
            for j, opp in enumerate(route.opportunities[:5], 1):
                lines.append(
                    f"{j}. **{opp.category}** (EPS={opp.eps}) — {opp.rationale[:80]}"
                )
            lines.append("")

        return "\n".join(lines)

    def save_report(self, result: dict[str, Any], output_path: str | Path) -> Path:
        """Salva relatorio em disco."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generate_report(result), encoding="utf-8")
        return path

    def save_json(self, result: dict[str, Any], output_path: str | Path) -> Path:
        """Salva resultado como JSON."""
        import json
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "spec": "SPEC-045",
            "version": "2.0",
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            "summary": result["summary"],
            "opportunities": [
                {
                    "rank": i + 1,
                    "dimension": o.dimension,
                    "category": o.category,
                    "eps": o.eps,
                    "grade": o.grade,
                    "feasibility": o.feasibility,
                    "scores": {
                        "cross_domain_impact": o.cross_domain_impact,
                        "theoretical_fertility": o.theoretical_fertility,
                        "game_theoretic_value": o.game_theoretic_value,
                        "teleological_alignment": o.teleological_alignment,
                        "cascade_impact": o.cascade_impact,
                        "social_impact": o.social_impact,
                    },
                    "rationale": o.rationale,
                    "suggested_method": o.suggested_method,
                    "source_scanners": o.source_scanners,
                }
                for i, o in enumerate(result["opportunities"])
            ],
            "feasibility": {
                cat: {
                    "status": f.status,
                    "feasible": f.feasible,
                    "dna_match": f.dna_match,
                    "capabilities_present": f.capabilities_present,
                    "capabilities_missing": f.capabilities_missing,
                }
                for cat, f in result["feasibility"].items()
            },
            "roadmap": {
                "title": result["roadmap"].title,
                "total_opportunities": result["roadmap"].total_opportunities,
                "routes": [
                    {
                        "name": r.name,
                        "description": r.description,
                        "impact": r.estimated_impact,
                        "effort": r.estimated_effort,
                        "count": len(r.opportunities),
                    }
                    for r in result["roadmap"].routes
                ],
            },
        }

        path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    # ═══════════════════════════════════════════════════════════════════
    # SENSITIVITY ANALYSIS (SPEC-045 v2.1)
    # ═══════════════════════════════════════════════════════════════════

    def sensitivity_analysis(
        self,
        base_result: dict[str, Any],
        delta: float = 0.2,
        steps: int = 5,
    ) -> dict[str, Any]:
        """Analise de sensibilidade dos pesos da formula EPS v2.

        Testa como variacoes de ±delta nos pesos afetam o ranking
        e as notas dos oportunidades.

        Referencia metodologica:
        - Saltelli et al. (2008). Global Sensitivity Analysis: The Primer.
        - Wong et al. (2021). Methods for Identifying Health Research Gaps.
          RAND Corporation, Research Report RR-A119-1.

        Args:
            base_result: Resultado base do scan()
            delta: Variacao maxima dos pesos (default ±20%)
            steps: Numero de passos entre -delta e +delta

        Returns:
            Dict com sensibilidade por dimensao e estabilidade do ranking
        """
        base_opps = base_result["opportunities"]
        if not base_opps:
            return {"stable": True, "dimension_sensitivity": {}, "ranking_changes": 0}

        base_ranking = [o.category for o in base_opps]
        dim_sensitivity = {}
        ranking_changes = 0

        # Para cada dimensao, variar o peso
        for dim_name in self.WEIGHTS:
            dim_impacts = []
            original_weight = self.WEIGHTS[dim_name]

            # Gerar variacoes do peso
            weight_range = [
                original_weight * (1 - delta + i * 2 * delta / (steps - 1))
                for i in range(steps)
            ]

            for new_weight in weight_range:
                # Criar copia dos pesos
                modified_weights = self.WEIGHTS.copy()
                modified_weights[dim_name] = new_weight

                # Recalcular EPS para cada oportunidade
                modified_eps = []
                for opp in base_opps:
                    eps = (
                        opp.cross_domain_impact * modified_weights["cross_domain"] +
                        opp.theoretical_fertility * modified_weights["theoretical_fertility"] +
                        opp.game_theoretic_value * modified_weights["game_theoretic"] +
                        opp.teleological_alignment * modified_weights["teleological_alignment"] +
                        opp.cascade_impact * modified_weights["cascade_impact"] +
                        opp.social_impact * modified_weights["social_impact"]
                    ) * 10
                    eps = round(min(100, max(0, eps)), 1)
                    modified_eps.append(eps)

                # Calcular impacto medio
                base_eps = [o.eps for o in base_opps]
                avg_impact = sum(abs(a - b) for a, b in zip(base_eps, modified_eps)) / len(base_eps)
                dim_impacts.append(avg_impact)

            # Sensibilidade da dimensao = media dos impactos
            avg_sensitivity = sum(dim_impacts) / len(dim_impacts) if dim_impacts else 0
            max_sensitivity = max(dim_impacts) if dim_impacts else 0

            dim_sensitivity[dim_name] = {
                "original_weight": original_weight,
                "avg_eps_change": round(avg_sensitivity, 2),
                "max_eps_change": round(max_sensitivity, 2),
                "stability": "high" if avg_sensitivity < 5 else "medium" if avg_sensitivity < 10 else "low",
            }

            # Verificar mudancas no ranking
            if dim_impacts:
                max_impact_dim = max(dim_impacts)
                if max_impact_dim > 5:
                    ranking_changes += 1

        # Estabilidade geral
        total_avg = sum(d["avg_eps_change"] for d in dim_sensitivity.values()) / len(dim_sensitivity)
        overall_stability = "high" if total_avg < 3 else "medium" if total_avg < 7 else "low"

        return {
            "stable": ranking_changes == 0,
            "overall_stability": overall_stability,
            "avg_eps_change": round(total_avg, 2),
            "ranking_changes": ranking_changes,
            "dimension_sensitivity": dim_sensitivity,
            "recommendation": self._sensitivity_recommendation(dim_sensitivity, overall_stability),
        }

    def _sensitivity_recommendation(
        self, dim_sensitivity: dict[str, Any], stability: str
    ) -> str:
        """Gera recomendacao baseada na analise de sensibilidade."""
        if stability == "high":
            return (
                "Os pesos sao estaveis. Variacoes de ±20% nao alteram "
                "significativamente o ranking. Modelo confiavel para tomada de decisao."
            )
        elif stability == "medium":
            return (
                "Sensibilidade moderada. Algumas dimensoes influenciam mais o ranking. "
                "Recomenda-se validacao adicional com dados empiricos."
            )
        else:
            # Identificar dimensoes mais criticas
            critical = [
                k for k, v in dim_sensitivity.items()
                if v["stability"] == "low"
            ]
            return (
                f"Alta sensibilidade detectada em: {', '.join(critical)}. "
                "Os pesos devem ser recalibrados com base em validacao empirica "
                "antes de usar o ranking para decisoes criticas."
            )


# ── Quick test ──
if __name__ == "__main__":
    estimator = PotentialityEstimatorV2()
    result = estimator.scan(
        noological_results={
            "dimensions": {
                "teoria_jogos": {"name": "Teoria dos Jogos", "absent": ["equilibrio_nash_aplicado"], "density": 0.2},
                "dominios": {"name": "Dominios", "absent": ["neurociencia_cognitiva"], "density": 0.3},
            }
        },
        teleological_results={"goals": [{"required_dimensions": ["teoria_jogos"], "keywords": ["nash"]}]},
        evolutionary_results={"bottlenecks": [{"dimension": "teoria_jogos", "category": "equilibrio_nash_aplicado", "cascade_impact": 8}]},
        dna_results={"capability_map": {"noological_scanner": ["gap_detection"], "cross_validation_engine": ["cross_validation"]}},
        social_impact_results={"consolidated_score": 65},
    )

    print(f"Oportunidades: {result['summary']['total_opportunities']}")
    print(f"Discovery: {result['summary']['discovery']}")
    print(f"Viaveis: {result['summary']['feasibility']['viable']}")
    for opp in result["opportunities"]:
        print(f"  [{opp.grade}] {opp.category} — EPS={opp.eps} | Feasibility={opp.feasibility}")
