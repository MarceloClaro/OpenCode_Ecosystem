#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NoologicalScanner v1.0 — Scanner Epistemológico / Scanner Noológico
=====================================================================
Camada complementar de análise que identifica AUSÊNCIAS, não erros.
Não pergunta "o que está errado?" mas "o que não está sendo considerado?"

Conceito original proposto por: interlocutor anônimo (2026)
Inspirado em: epistemologia de Bachelard, noologia de Teilhard de Chardin,
              gap analysis de Booth, mapeamento conceitual de Novak

Arquitetura:
  1. Knowledge Space Mapping — mapeia dimensões do espaço de conhecimento
  2. Dimensional Density Analysis — calcula densidade de exploração por dimensão
  3. Blind Spot Detection — identifica regiões conceituais não investigadas
  4. Expansion Recommendations — sugere direções de pesquisa complementares

Integra-se com:
  - AcademicAuditTrail (parágrafos → evidências)
  - ResearcherScore (score de qualidade)
  - ReasoningOrchestrator (68 tipos de raciocínio)
  - GameTheoryValidator (10 estratégias)

Uso:
  from noological_scanner import NoologicalScanner
  scanner = NoologicalScanner()
  report = scanner.scan(audit_trail, research_domain="psicologia")
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BRAZIL_TZ = timezone.utc


# ═══════════════════════════════════════════════════════════════════════
# DIMENSÕES DO ESPAÇO DE CONHECIMENTO
# ═══════════════════════════════════════════════════════════════════════

@dataclass
class KnowledgeDimension:
    """Uma dimensão do espaço de conhecimento."""
    name: str
    categories: list[str]
    description: str = ""
    covered: list[str] = field(default_factory=list)
    absent: list[str] = field(default_factory=list)
    density: float = 0.0  # 0.0 = vazio, 1.0 = totalmente explorado


# Dimensões predefinidas para escaneamento
EPISTEMOLOGICAL_DIMENSIONS: dict[str, KnowledgeDimension] = {
    "paradigmas": KnowledgeDimension(
        name="Paradigmas Epistemológicos",
        categories=["Positivista", "Interpretativista", "Crítico/Transformador",
                    "Pragmatista", "Fenomenológico", "Construtivista",
                    "Pós-estruturalista", "Complexo/Sistêmico"],
        description="Lentes epistemológicas através das quais o fenômeno é observado"
    ),
    "metodos": KnowledgeDimension(
        name="Métodos de Investigação",
        categories=["Quantitativo experimental", "Quantitativo correlacional",
                    "Qualitativo fenomenológico", "Qualitativo grounded theory",
                    "Misto sequencial", "Misto convergente",
                    "Revisão sistemática", "Meta-análise",
                    "Estudo de caso", "Pesquisa-ação"],
        description="Abordagens metodológicas empregadas"
    ),
    "teorias": KnowledgeDimension(
        name="Referenciais Teóricos",
        categories=["Cognitivo-comportamental", "Psicanalítico", "Humanista",
                    "Sistêmico", "Neurobiológico", "Evolucionista",
                    "Social-crítico", "Fenomenológico-existencial",
                    "Comportamental", "Integrativo/transdiagnóstico"],
        description="Marcos teóricos que fundamentam a análise"
    ),
    "raciocinio": KnowledgeDimension(
        name="Tipos de Raciocínio",
        categories=["Dedutivo", "Indutivo", "Abdutivo", "Dialético",
                    "Sistêmico", "Probabilístico", "Contrafactual",
                    "Metacognitivo", "Teleológico", "Pragmático"],
        description="Modos de inferência e construção de conhecimento"
    ),
    "teoria_jogos": KnowledgeDimension(
        name="Perspectivas Estratégicas (Teoria dos Jogos)",
        categories=["Equilíbrio de Nash", "Dilema do Prisioneiro", "Soma Zero",
                    "Tit-for-Tat", "Stackelberg", "Barganha",
                    "Sinalização", "Evolutivo", "Bayesiano", "Cooperativo"],
        description="Modelos estratégicos para análise de decisões"
    ),
    "niveis_analise": KnowledgeDimension(
        name="Níveis de Análise",
        categories=["Individual/intrapsíquico", "Interpessoal/relacional",
                    "Grupal/organizacional", "Comunitário", "Sistêmico/político",
                    "Neurobiológico", "Evolutivo/filogenético", "Cultural/antropológico"],
        description="Escalas de observação do fenômeno"
    ),
    "temporalidade": KnowledgeDimension(
        name="Perspectiva Temporal",
        categories=["Transversal (momento único)", "Longitudinal (curto prazo)",
                    "Longitudinal (longo prazo)", "Histórico/retrospectivo",
                    "Prospectivo/preditivo", "Desenvolvimental (ciclo de vida)"],
        description="Enquadramento temporal da análise"
    ),
    "populacao": KnowledgeDimension(
        name="População e Contexto",
        categories=["Adultos", "Idosos", "Adolescentes", "Infância",
                    "Gênero feminino", "Gênero masculino", "Diversidade de gênero",
                    "Contexto clínico", "Contexto comunitário", "Contexto organizacional",
                    "Brasil/América Latina", "Cross-cultural"],
        description="Características da população estudada e contexto"
    ),
    "dados": KnowledgeDimension(
        name="Tipos de Dados e Evidências",
        categories=["Dados clínicos (escalas, inventários)", "Dados neurobiológicos",
                    "Dados qualitativos (entrevistas)", "Dados observacionais",
                    "Dados epidemiológicos", "Dados longitudinais",
                    "Dados comparativos (cross-cultural)", "Metadados (revisões)"],
        description="Natureza das evidências utilizadas"
    ),
    "dominios": KnowledgeDimension(
        name="Domínios de Conhecimento Cruzados",
        categories=["Psicologia clínica", "Neurociências", "Sociologia",
                    "Antropologia", "Economia comportamental", "Filosofia da mente",
                    "Psicofarmacologia", "Saúde pública", "Educação",
                    "Inteligência Artificial / Tecnologia"],
        description="Áreas do conhecimento potencialmente relevantes"
    ),
}


# ═══════════════════════════════════════════════════════════════════════
# SCANNER NOOLÓGICO
# ═══════════════════════════════════════════════════════════════════════

class NoologicalScanner:
    """Scanner que identifica AUSÊNCIAS no espaço de conhecimento.

    Complementa o AcademicAuditTrail (que identifica ERROS)
    com uma camada que identifica INCOMPLETUDES.
    """

    def __init__(self, dimensions: dict[str, KnowledgeDimension] | None = None):
        self.dimensions = dimensions or EPISTEMOLOGICAL_DIMENSIONS
        self.scan_results: dict[str, Any] = {}

    def scan(
        self,
        audit_trail: Any,
        research_domain: str = "",
    ) -> dict[str, Any]:
        """Executa varredura completa do espaço de conhecimento.

        Args:
            audit_trail: Instância de AcademicAuditTrail com parágrafos e evidências
            research_domain: Domínio principal da pesquisa

        Returns:
            Relatório completo com dimensões exploradas, ausentes e recomendações
        """
        # Extrair texto completo do corpus
        corpus_text = self._extract_corpus(audit_trail)
        corpus_lower = corpus_text.lower()

        # Analisar cada dimensão
        dimension_results = {}
        total_covered = 0
        total_categories = 0

        for dim_key, dimension in self.dimensions.items():
            covered = []
            absent = []

            for category in dimension.categories:
                total_categories += 1
                # Verificar se a categoria está presente no corpus
                if self._category_present(category, corpus_lower, dim_key):
                    covered.append(category)
                    total_covered += 1
                else:
                    absent.append(category)

            density = len(covered) / max(1, len(dimension.categories))
            dimension_results[dim_key] = {
                "name": dimension.name,
                "description": dimension.description,
                "covered": covered,
                "absent": absent,
                "density": round(density, 2),
                "coverage_pct": round(density * 100),
            }

        # Calcular métricas globais
        overall_density = total_covered / max(1, total_categories)
        blind_spots = self._identify_blind_spots(dimension_results)
        recommendations = self._generate_recommendations(dimension_results, research_domain)

        self.scan_results = {
            "research_domain": research_domain,
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            "overall_density": round(overall_density, 2),
            "overall_coverage_pct": round(overall_density * 100),
            "dimensions_analyzed": len(dimension_results),
            "total_categories": total_categories,
            "categories_covered": total_covered,
            "categories_absent": total_categories - total_covered,
            "dimensions": dimension_results,
            "blind_spots": blind_spots,
            "recommendations": recommendations,
            "completeness_grade": self._grade(overall_density),
        }

        return self.scan_results

    def _extract_corpus(self, audit_trail: Any) -> str:
        """Extrai texto completo do corpus de pesquisa."""
        texts = []
        if hasattr(audit_trail, "paragraphs"):
            for para in audit_trail.paragraphs.values():
                if hasattr(para, "text"):
                    texts.append(para.text)
                elif isinstance(para, dict):
                    texts.append(para.get("text", ""))
        # Também incluir evidências/claims
        if hasattr(audit_trail, "citation_map"):
            for src in audit_trail.citation_map:
                texts.append(str(src))
        return " ".join(texts)

    def _category_present(self, category: str, corpus_lower: str, dim_key: str) -> bool:
        """Verifica se uma categoria está presente no corpus.

        Usa casamento semântico por palavras-chave específicas de cada dimensão.
        """
        cat_lower = category.lower()

        # Palavras-chave por dimensão
        keyword_map = {
            "paradigmas": {
                "positivista": ["positiv", "quantitativ", "experimental", "hipotese", "mensura"],
                "interpretativista": ["interpretativ", "qualitativ", "fenomenolog", "compreens"],
                "crítico": ["critic", "transformador", "emancip", "dialetic"],
                "pragmatista": ["pragmat", "misto", "multimetod", "triangul"],
                "construtivista": ["construtiv", "construcion", "significado"],
                "pós-estruturalista": ["estrutural", "desconst", "foucault", "derrida"],
                "complexo": ["complex", "sistem", "emerg", "holistic", "caos"],
            },
            "metodos": {
                "quantitativo experimental": ["experiment", "randomiz", "control", "ensaio clinico"],
                "quantitativo correlacional": ["correla", "regress", "associac", "preditor"],
                "qualitativo": ["qualitativ", "entrevista", "analise tematica", "fenomenolog"],
                "grounded theory": ["grounded", "teoria fundamentada"],
                "misto": ["misto", "multimetod", "triangul"],
                "revisão sistemática": ["revisao sistematica", "systematic review", "prisma"],
                "meta-análise": ["meta-analise", "meta analise", "tamanho de efeito"],
                "estudo de caso": ["estudo de caso", "case study", "caso clinico", "caso unico"],
                "pesquisa-ação": ["pesquisa-acao", "pesquisa acao", "action research"],
            },
            "teorias": {
                "cognitivo-comportamental": ["cognitiv", "comportamental", "tcc", "beck", "pensamento automatico"],
                "psicanalítico": ["psicanal", "freud", "inconscient", "transferenc"],
                "humanista": ["humanist", "roger", "centrado na pessoa", "auto-atualiz"],
                "sistêmico": ["sistemic", "familia", "cibernet", "padrao relacional"],
                "neurobiológico": ["neurobiolog", "neurocien", "amigdala", "cortex", "pre-frontal"],
                "evolucionista": ["evolucion", "adaptativ", "selecao natural"],
                "social-crítico": ["social critic", "critic social", "desiguald", "opress"],
                "fenomenológico-existencial": ["existencial", "heidegger", "sartre", "sentido da vida"],
                "comportamental": ["comportament", "skinner", "condicion", "reforc"],
                "integrativo": ["integrat", "transdiagnost", "unificad", "ecletic"],
            },
            "raciocinio": {
                "dedutivo": ["dedut", "premissa", "conclusao necessaria"],
                "indutivo": ["indut", "generaliz", "padrao", "regularidad"],
                "abdutivo": ["abdut", "hipotese", "melhor explicacao"],
                "dialético": ["dialet", "tese", "antitese", "sintes", "contradic"],
                "sistêmico": ["sistemic", "interconex", "retroaliment", "emergenc"],
                "probabilístico": ["probabil", "bayes", "incerteza", "estatistic"],
                "contrafactual": ["contrafactual", "se", "cenario alternativ"],
                "metacognitivo": ["metacognit", "pensar sobre", "auto-regul"],
                "teleológico": ["teleolog", "proposit", "finalidad", "objetivo"],
                "pragmático": ["pragmat", "aplic", "util", "pratico", "funcional"],
            },
        }

        # Buscar keywords específicas da dimensão
        if dim_key in keyword_map:
            for kw_category, keywords in keyword_map[dim_key].items():
                if kw_category in cat_lower:
                    for kw in keywords:
                        if kw in corpus_lower:
                            return True
                    return False  # Categoria específica não encontrada

        # Fallback: busca genérica
        words = cat_lower.split()
        match_count = sum(1 for w in words if len(w) > 3 and w in corpus_lower)
        return match_count >= len(words) * 0.5

    def _identify_blind_spots(self, dimension_results: dict[str, Any]) -> list[dict[str, Any]]:
        """Identifica pontos cegos — dimensões com densidade zero ou muito baixa."""
        blind_spots = []

        for dim_key, dim_data in dimension_results.items():
            if dim_data["density"] < 0.2:
                blind_spots.append({
                    "dimension": dim_data["name"],
                    "key": dim_key,
                    "density": dim_data["density"],
                    "absent_categories": dim_data["absent"][:5],
                    "severity": "critical" if dim_data["density"] == 0 else "high" if dim_data["density"] < 0.1 else "moderate",
                    "impact": f"A dimensão '{dim_data['name']}' está praticamente inexplorada. "
                             f"Isso pode indicar viés metodológico ou limitação de escopo."
                })

        return sorted(blind_spots, key=lambda x: x["density"])

    def _generate_recommendations(
        self,
        dimension_results: dict[str, Any],
        research_domain: str,
    ) -> list[str]:
        """Gera recomendações de expansão baseadas nos gaps identificados."""
        recommendations = []

        # Recomendações por dimensão com baixa densidade
        for dim_key, dim_data in dimension_results.items():
            if dim_data["density"] < 0.3 and dim_data["absent"]:
                top_absent = dim_data["absent"][:3]
                recommendations.append(
                    f"[{dim_data['name']}] Explorar: {', '.join(top_absent)}. "
                    f"A densidade atual é de apenas {dim_data['coverage_pct']}%."
                )

        # Recomendações de cruzamento interdisciplinar
        if dimension_results.get("dominios", {}).get("density", 1) < 0.3:
            recommendations.append(
                "[Domínios Cruzados] A pesquisa está concentrada em poucas áreas do conhecimento. "
                "Considere incorporar perspectivas da neurociência, sociologia ou economia comportamental."
            )

        # Recomendações de diversidade metodológica
        if dimension_results.get("metodos", {}).get("density", 1) < 0.3:
            recommendations.append(
                "[Métodos] A abordagem metodológica é restrita. "
                "Considere complementar com métodos mistos ou revisão sistemática."
            )

        # Recomendações de Teoria dos Jogos
        if dimension_results.get("teoria_jogos", {}).get("density", 1) == 0:
            recommendations.append(
                "[Teoria dos Jogos] Nenhuma perspectiva estratégica foi aplicada. "
                "Para pesquisas que envolvem decisão ou interação, considere modelar com "
                "Equilíbrio de Nash, Jogos Evolutivos ou Barganha."
            )

        return recommendations if recommendations else ["A pesquisa apresenta boa cobertura multidimensional."]

    def _grade(self, density: float) -> str:
        """Atribui conceito baseado na densidade de cobertura."""
        if density >= 0.7: return "A — Cobertura Epistemológica Ampla"
        if density >= 0.5: return "B — Cobertura Moderada"
        if density >= 0.3: return "C — Cobertura Limitada"
        if density >= 0.1: return "D — Cobertura Restrita"
        return "F — Cobertura Mínima ( muitos pontos cegos)"

    def generate_markdown_report(self) -> str:
        """Gera relatório Markdown do escaneamento."""
        r = self.scan_results
        if not r:
            return "Nenhum escaneamento realizado."

        lines = [
            f"# Scanner Noológico — Relatório de Cobertura Epistemológica",
            f"",
            f"**Domínio**: {r['research_domain'] or 'Não especificado'}",
            f"**Data**: {r['timestamp'][:19]}",
            f"**Cobertura Global**: {r['overall_coverage_pct']}% ({r['categories_covered']}/{r['total_categories']} categorias)",
            f"**Conceito**: {r['completeness_grade']}",
            f"",
            f"---",
            f"",
            f"## Dimensões Analisadas ({r['dimensions_analyzed']})",
            f"",
        ]

        for dim_key, dim_data in r["dimensions"].items():
            bar_len = 30
            filled = int(dim_data["density"] * bar_len)
            bar = "█" * filled + "░" * (bar_len - filled)
            lines.append(f"### {dim_data['name']} — {dim_data['coverage_pct']}%")
            lines.append(f"`{bar}`")
            lines.append(f"")
            if dim_data["covered"]:
                lines.append(f"**Explorado ({len(dim_data['covered'])})**: {', '.join(dim_data['covered'][:5])}")
            if dim_data["absent"]:
                lines.append(f"**Ausente ({len(dim_data['absent'])})**: {', '.join(dim_data['absent'][:5])}")
            lines.append(f"")

        lines.append("---")
        lines.append("")
        lines.append(f"## Pontos Cegos ({len(r['blind_spots'])})")
        lines.append("")
        if r["blind_spots"]:
            for bs in r["blind_spots"]:
                lines.append(f"- 🔴 **{bs['dimension']}** [{bs['severity'].upper()}]: {bs['impact']}")
        else:
            lines.append("Nenhum ponto cego crítico identificado.")
        lines.append("")

        lines.append("---")
        lines.append("")
        lines.append(f"## Recomendações de Expansão ({len(r['recommendations'])})")
        lines.append("")
        for i, rec in enumerate(r["recommendations"], 1):
            lines.append(f"{i}. {rec}")

        return "\n".join(lines)

    def save_report(self, output_path: str | Path) -> Path:
        """Salva relatório em disco."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generate_markdown_report(), encoding="utf-8")
        return path
