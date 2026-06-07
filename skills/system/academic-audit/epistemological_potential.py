#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
EpistemologicalPotentialEstimator v1.0 — Scanner Noológico v3.0
=================================================================
Evolucao: ERRO (v1) -> AUSENCIA (v2) -> OPORTUNIDADE (v3)

Conceito original: interlocutor anonimo (2026)
v3.0: Marcelo Claro Laranjeira — "De ausencias a descobertas"

Para cada ponto cego identificado pelo NoologicalScanner,
calcula o Epistemological Potential Score (EPS) baseado em:
  1. Cross-Domain Impact — quantos dominios seriam impactados
  2. Citation Void Density — densidade de citacoes na area do gap
  3. Theoretical Fertility — quantas teorias se conectam ao gap
  4. Game-Theoretic Value — mudaria o equilibrio estrategico?
  5. Temporal Urgency — o gap esta crescendo ou diminuindo?

Output: Ranking de oportunidades de pesquisa por potencial de descoberta.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BRAZIL_TZ = timezone.utc


@dataclass
class ResearchOpportunity:
    """Uma oportunidade de pesquisa priorizada."""
    dimension: str
    category: str  # a categoria ausente especifica
    eps: float  # Epistemological Potential Score (0-100)
    grade: str  # Discovery | Promising | Exploratory | Marginal
    cross_domain_impact: float  # 0-10
    citation_void: float  # 0-10
    theoretical_fertility: float  # 0-10
    game_theoretic_value: float  # 0-10
    temporal_urgency: float  # 0-10
    rationale: str = ""
    suggested_method: str = ""
    expected_contribution: str = ""


# ═══════════════════════════════════════════════════════════════════════
# CROSS-DOMAIN IMPACT MATRIX
# ═══════════════════════════════════════════════════════════════════════

# Quantos dominios seriam impactados se este gap fosse preenchido
CROSS_DOMAIN_IMPACT: dict[str, int] = {
    "teoria_jogos": 8,    # Impacta tudo que envolve decisao/interacao
    "paradigmas": 7,      # Impacta a lente de observacao de todo o resto
    "metodos": 6,         # Impacta como qualquer pesquisa e conduzida
    "dominios": 6,        # Conexoes interdisciplinares
    "raciocinio": 5,      # Impacta a qualidade da inferencia
    "dados": 5,           # Impacta a base empirica
    "niveis_analise": 4,  # Impacta a escala de observacao
    "temporalidade": 3,   # Impacta o enquadramento temporal
    "populacao": 3,       # Impacta a generalizabilidade
    "teorias": 2,         # Impacto mais localizado
}

# ═══════════════════════════════════════════════════════════════════════
# THEORETICAL FERTILITY — Quantas teorias se conectam ao gap
# ═══════════════════════════════════════════════════════════════════════

THEORETICAL_FERTILITY: dict[str, dict[str, int]] = {
    "teoria_jogos": {
        "Equilíbrio de Nash": 9,
        "Dilema do Prisioneiro": 8,
        "Evolutivo": 8,
        "Bayesiano": 9,
        "Cooperativo": 8,
        "default": 6,
    },
    "paradigmas": {
        "Fenomenológico": 7,
        "Construtivista": 7,
        "Complexo/Sistêmico": 8,
        "default": 5,
    },
    "dominios": {
        "Neurociências": 8,
        "Sociologia": 6,
        "Economia comportamental": 7,
        "Inteligência Artificial / Tecnologia": 8,
        "default": 5,
    },
    "default": {"default": 4},
}

# ═══════════════════════════════════════════════════════════════════════
# GAME-THEORETIC VALUE — Mudaria o equilibrio de Nash?
# ═══════════════════════════════════════════════════════════════════════

GAME_THEORETIC_VALUE: dict[str, dict[str, int]] = {
    "teoria_jogos": {"default": 10},  # Preencher gap em GT muda tudo
    "paradigmas": {"default": 7},     # Mudar paradigma muda a paisagem
    "dominios": {"default": 8},       # Cruzamento interdisciplinar e disruptivo
    "metodos": {"default": 6},
    "default": {"default": 4},
}


class EpistemologicalPotentialEstimator:
    """Estima o potencial epistemologico de pontos cegos.

    Transforma ausencias identificadas pelo NoologicalScanner
    em oportunidades de pesquisa priorizadas por potencial de descoberta.

    Uso:
        estimator = EpistemologicalPotentialEstimator()
        opportunities = estimator.estimate(scan_results)
        for opp in opportunities:
            print(f"{opp.grade}: {opp.dimension}/{opp.category} — EPS={opp.eps}")
    """

    WEIGHTS = {
        "cross_domain": 0.30,
        "citation_void": 0.15,
        "theoretical_fertility": 0.25,
        "game_theoretic": 0.20,
        "temporal_urgency": 0.10,
    }

    def estimate(self, scan_results: dict[str, Any]) -> list[ResearchOpportunity]:
        """Estima potencial epistemologico de todos os pontos cegos.

        Args:
            scan_results: Resultado do NoologicalScanner.scan()

        Returns:
            Lista de ResearchOpportunity ordenada por EPS decrescente
        """
        opportunities = []

        for dim_key, dim_data in scan_results.get("dimensions", {}).items():
            for category in dim_data.get("absent", []):
                opp = self._estimate_single(dim_key, category, dim_data)
                opportunities.append(opp)

        # Ordenar por EPS decrescente
        return sorted(opportunities, key=lambda x: x.eps, reverse=True)

    def _estimate_single(self, dim_key: str, category: str,
                         dim_data: dict[str, Any]) -> ResearchOpportunity:
        """Estima potencial de uma unica ausencia."""
        # 1. Cross-Domain Impact (0-10)
        cdi = min(10, CROSS_DOMAIN_IMPACT.get(dim_key, 3))

        # 2. Citation Void Density (0-10)
        cvd = min(10, int((1 - dim_data.get("density", 0)) * 10))

        # 3. Theoretical Fertility (0-10)
        tf_map = THEORETICAL_FERTILITY.get(dim_key, THEORETICAL_FERTILITY["default"])
        tf = 0
        for kw, val in tf_map.items():
            if kw.lower() in category.lower():
                tf = val
                break
        if tf == 0:
            tf = tf_map.get("default", 4)

        # 4. Game-Theoretic Value (0-10)
        gtv_map = GAME_THEORETIC_VALUE.get(dim_key, GAME_THEORETIC_VALUE["default"])
        gtv = gtv_map.get("default", 4)

        # 5. Temporal Urgency (0-10) — heuristico baseado em trends
        urgency_keywords = ["ia", "inteligencia artificial", "neurociencia",
                           "mudanca climatica", "pandemia", "crise"]
        tu = 7 if any(kw in category.lower() for kw in urgency_keywords) else 4

        # EPS ponderado
        eps = (
            cdi * self.WEIGHTS["cross_domain"] +
            cvd * self.WEIGHTS["citation_void"] +
            tf * self.WEIGHTS["theoretical_fertility"] +
            gtv * self.WEIGHTS["game_theoretic"] +
            tu * self.WEIGHTS["temporal_urgency"]
        ) * 10  # escala 0-100

        # Grade
        if eps >= 80: grade = "Discovery"
        elif eps >= 60: grade = "Promising"
        elif eps >= 40: grade = "Exploratory"
        else: grade = "Marginal"

        # Rationale
        rationale = self._generate_rationale(dim_key, category, cdi, tf, gtv)
        suggested_method = self._suggest_method(dim_key, category)
        expected_contribution = self._expected_contribution(eps)

        return ResearchOpportunity(
            dimension=dim_data.get("name", dim_key),
            category=category,
            eps=round(eps),
            grade=grade,
            cross_domain_impact=cdi,
            citation_void=cvd,
            theoretical_fertility=tf,
            game_theoretic_value=gtv,
            temporal_urgency=tu,
            rationale=rationale,
            suggested_method=suggested_method,
            expected_contribution=expected_contribution,
        )

    def _generate_rationale(self, dim_key: str, category: str,
                           cdi: int, tf: int, gtv: int) -> str:
        """Gera justificativa para a pontuacao."""
        parts = []
        if cdi >= 7:
            parts.append(f"Alto impacto interdisciplinar (afeta {cdi} dominios)")
        if tf >= 7:
            parts.append(f"Alta fertilidade teorica ({tf}/10)")
        if gtv >= 7:
            parts.append(f"Potencial de mudar o equilibrio estrategico da area")
        if cdi >= 5 and tf >= 5:
            parts.append("Oportunidade de contribuicao original significativa")
        return ". ".join(parts) if parts else "Oportunidade de pesquisa incremental."

    def _suggest_method(self, dim_key: str, category: str) -> str:
        """Sugere metodo de investigacao."""
        method_map = {
            "teoria_jogos": "Modelagem formal + simulacao computacional",
            "paradigmas": "Ensaio teorico + analise comparativa",
            "metodos": "Estudo metodologico com validacao empirica",
            "dominios": "Revisao sistematica interdisciplinar",
            "dados": "Coleta e analise de dados primarios",
            "raciocinio": "Estudo de caso com multiplos frameworks",
        }
        return method_map.get(dim_key, "Estudo exploratorio com triangulacao metodologica")

    def _expected_contribution(self, eps: float) -> str:
        """Estima a contribuicao esperada."""
        if eps >= 80: return "Potencial de abrir nova linha de pesquisa"
        if eps >= 60: return "Contribuicao significativa para a area"
        if eps >= 40: return "Complementacao relevante ao campo"
        return "Refinamento incremental"

    def generate_report(self, opportunities: list[ResearchOpportunity]) -> str:
        """Gera relatorio Markdown de oportunidades priorizadas."""
        lines = [
            "# Relatorio de Oportunidades de Pesquisa",
            "",
            f"**Data**: {datetime.now(BRAZIL_TZ).strftime('%d/%m/%Y %H:%M')}",
            f"**Total de oportunidades**: {len(opportunities)}",
            "",
            "---",
            "",
            "## Oportunidades Priorizadas por Potencial de Descoberta",
            "",
            "| # | EPS | Grade | Dimensao | Categoria | Impacto | Justificativa |",
            "|:--:|:---:|:-----:|----------|-----------|:------:|--------------|",
        ]

        for i, opp in enumerate(opportunities[:20], 1):
            grade_icon = {"Discovery": "D", "Promising": "P", "Exploratory": "E", "Marginal": "M"}.get(opp.grade, "?")
            lines.append(
                f"| {i} | **{opp.eps}** | {grade_icon} | {opp.dimension[:25]} | "
                f"{opp.category[:30]} | {opp.cross_domain_impact}/10 | "
                f"{opp.rationale[:60]}... |"
            )

        lines.extend([
            "",
            "---",
            "",
            "## Top 5 Oportunidades de Descoberta",
            "",
        ])

        discoveries = [o for o in opportunities if o.grade == "Discovery"]
        promising = [o for o in opportunities if o.grade == "Promising"]
        top5 = (discoveries + promising)[:5]

        for i, opp in enumerate(top5, 1):
            lines.extend([
                f"### {i}. {opp.dimension}: {opp.category}",
                f"",
                f"**EPS**: {opp.eps}/100 | **Grade**: {opp.grade}",
                f"",
                f"**Por que investigar**: {opp.rationale}",
                f"",
                f"**Metodo sugerido**: {opp.suggested_method}",
                f"",
                f"**Contribuicao esperada**: {opp.expected_contribution}",
                f"",
                f"**Score detalhado**:",
                f"- Cross-Domain Impact: {opp.cross_domain_impact}/10",
                f"- Theoretical Fertility: {opp.theoretical_fertility}/10",
                f"- Game-Theoretic Value: {opp.game_theoretic_value}/10",
                f"- Citation Void: {opp.citation_void}/10",
                f"- Temporal Urgency: {opp.temporal_urgency}/10",
                f"",
            ])

        return "\n".join(lines)

    def save_report(self, opportunities: list[ResearchOpportunity],
                    output_path: str | Path) -> Path:
        """Salva relatorio em disco."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generate_report(opportunities), encoding="utf-8")
        return path


# ── Teste ──
if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from noological_scanner import NoologicalScanner
    from academic_audit_trail import AcademicAuditTrail

    trail = AcademicAuditTrail()
    trail.record_paragraph("P01", "TCC eficaz para ansiedade. Equilibrio de Nash na relacao terapeutica. fMRI mostra reducao da amigdala.")
    scanner = NoologicalScanner()
    scan_results = scanner.scan(trail, "psicologia")

    estimator = EpistemologicalPotentialEstimator()
    opportunities = estimator.estimate(scan_results)

    print(f"Oportunidades: {len(opportunities)}")
    for opp in opportunities[:10]:
        print(f"  [{opp.grade}] {opp.category[:30]} — EPS={opp.eps} | CDI={opp.cross_domain_impact} TF={opp.theoretical_fertility} GTV={opp.game_theoretic_value}")
