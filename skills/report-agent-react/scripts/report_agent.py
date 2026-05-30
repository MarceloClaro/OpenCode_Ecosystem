#!/usr/bin/env python3
"""
ReportAgent — ReACT + Reflection
Inspirado pelo ReportAgent do MiroFish-Offline (report_agent.py).

Gera relatórios estruturados usando:
  1. Planning: análise do contexto e geração de sumário
  2. ReACT Loop: geração seção por seção com multi-turno
  3. Reflection: verificação em 3 dimensões (consistência, autocorreção, lacunas)

Modo de uso (CLI):
  python report_agent.py --graph <id> --requirement "Cenário" [--output report.md]
  python report_agent.py plan --graph <id> --requirement "Cenário"
  python report_agent.py reflect --input report.md

Autor: Reversa Engine (padrão MiroFish-Offline ReportAgent)
Licença: MIT
"""

import argparse
import json
import sys
import re
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path


# ──────────────────────────────────────────────
# Estruturas de Dados
# ──────────────────────────────────────────────

@dataclass
class ReportSection:
    title: str
    content: str = ""
    tool_calls: int = 0
    status: str = "pending"  # pending | generating | completed

    def to_dict(self) -> Dict[str, Any]:
        return {"title": self.title, "content": self.content,
                "tool_calls": self.tool_calls, "status": self.status}

    def to_markdown(self, level: int = 2) -> str:
        return f"{'#' * level} {self.title}\n\n{self.content}\n\n"


@dataclass
class ReportOutline:
    title: str
    summary: str
    sections: List[ReportSection]

    def to_dict(self) -> Dict[str, Any]:
        return {"title": self.title, "summary": self.summary,
                "sections": [s.to_dict() for s in self.sections]}

    def to_markdown(self) -> str:
        md = f"# {self.title}\n\n> {self.summary}\n\n"
        for s in self.sections:
            md += s.to_markdown()
        return md


@dataclass
class ReflectionResult:
    consistency_score: float = 1.0
    consistency_issues: List[str] = field(default_factory=list)
    corrections: List[Dict[str, str]] = field(default_factory=list)
    gaps: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "consistency": {"score": self.consistency_score,
                            "issues": self.consistency_issues},
            "self_correction": {"corrections": self.corrections},
            "gaps": {"unanswered": self.gaps, "suggestions": self.suggestions},
        }

    def to_text(self) -> str:
        lines = ["## Reflection Results"]
        lines.append(f"\n### Consistency: {self.consistency_score:.2f}")
        if self.consistency_issues:
            for issue in self.consistency_issues:
                lines.append(f"- ⚠️ {issue}")
        if self.corrections:
            lines.append(f"\n### Corrections Applied: {len(self.corrections)}")
            for c in self.corrections:
                lines.append(f"- {c.get('description','')}")
        if self.gaps:
            lines.append(f"\n### Gaps: {len(self.gaps)}")
            for g in self.gaps:
                lines.append(f"- 🔴 {g}")
        if self.suggestions:
            lines.append(f"\n### Suggestions")
            for s in self.suggestions:
                lines.append(f"- 💡 {s}")
        return "\n".join(lines)


# ──────────────────────────────────────────────
# Simulação de Ferramentas de Busca
# ──────────────────────────────────────────────

class MockGraphTools:
    """
    Simulação das ferramentas de busca para demonstração.
    Em produção, use hybrid_search.py com um banco SQLite real.
    """

    def __init__(self, graph_id: str, requirement: str):
        self.graph_id = graph_id
        self.requirement = requirement

    def insight_forge(self, query: str) -> Dict[str, Any]:
        """Simula InsightForge — análise profunda."""
        return {
            "facts": [
                f"Fato relevante sobre: {query}",
                f"Evidência adicional relacionada a {self.requirement}",
                "Cadeia de eventos identificada: A → B → C",
            ],
            "entities": [{"name": "Entidade A", "type": "Ator"},
                         {"name": "Entidade B", "type": "Influenciador"}],
            "relationships": ["Entidade A --[influencia]--> Entidade B"],
        }

    def panorama_search(self, query: str) -> Dict[str, Any]:
        """Simula PanoramaSearch — visão ampla."""
        return {
            "active_facts": [f"Fato ativo: {query} no contexto {self.requirement}"],
            "historical_facts": ["Fato histórico: cenário anterior"],
            "total_nodes": 10,
            "total_edges": 25,
        }

    def quick_search(self, query: str) -> Dict[str, Any]:
        """Simula QuickSearch — busca rápida."""
        return {
            "facts": [f"{query}: resultado rápido"],
            "total_count": 1,
        }


# ──────────────────────────────────────────────
# Motor de Reflexão
# ──────────────────────────────────────────────

class ReflectionEngine:
    """
    Motor de reflexão em 3 dimensões.
    Opera sobre o relatório gerado e identifica problemas.
    """

    def reflect(self, report_md: str, context: str = "") -> ReflectionResult:
        """
        Executa reflexão completa no relatório.

        1. Consistência: score 0-1 com lista de problemas
        2. Autocorreção: lista de correções sugeridas
        3. Lacunas: perguntas não respondidas
        """
        result = ReflectionResult()

        # 1. Verificar consistência
        issues = []
        score = 1.0

        # Detectar contradições (mesma afirmação dita de formas diferentes)
        sentences = re.findall(r'[^.!?]+[.!?]', report_md)
        for i, s1 in enumerate(sentences):
            for s2 in sentences[i + 1:]:
                # Verificar similaridade superficial como proxy
                words1 = set(s1.lower().split())
                words2 = set(s2.lower().split())
                overlap = words1 & words2
                if len(overlap) > 5 and len(words1) > 3 and len(words2) > 3:
                    ratio = len(overlap) / min(len(words1), len(words2))
                    if ratio > 0.8:
                        issues.append(f"Possível redundância: Sentenças muito similares")
                        score -= 0.1

        # Verificar se há conteúdo vs. placeholders
        if len(report_md.strip()) < 100:
            issues.append("Relatório muito curto, pode faltar conteúdo")
            score -= 0.2

        # Detectar linguagem especulativa sem dados
        speculation_words = ["talvez", "possivelmente", "pode ser que",
                             "maybe", "perhaps", "possibly", "might"]
        for word in speculation_words:
            count = len(re.findall(rf'\b{word}\b', report_md.lower()))
            if count > 3:
                issues.append(f"Uso excessivo de '{word}' ({count}x) — dados insuficientes?")
                score -= 0.05 * min(count, 5)

        result.consistency_score = max(0, score)
        result.consistency_issues = issues

        # 2. Autocorreção
        if "TODO" in report_md or "FIXME" in report_md:
            result.corrections.append({
                "type": "placeholder",
                "description": "Remover placeholders (TODO/FIXME)",
                "severity": "high",
            })

        if "[" in report_md and "]" in report_md:
            brackets = re.findall(r'\[.*?\]', report_md)
            for b in brackets:
                if b.lower() in ["[inserir", "[TODO", "[FIXME", "[nota", "[insira"]:
                    result.corrections.append({
                        "type": "placeholder",
                        "description": f"Substituir placeholder: {b}",
                        "severity": "high",
                    })

        # 3. Lacunas
        # Verificar se contexto está sendo referenciado
        if context and context.lower() not in report_md.lower():
            result.gaps.append(f"O contexto '{context[:50]}...' não foi explicitamente mencionado")

        # Verificar se há dados citados
        quote_count = len(re.findall(r'>\s+"', report_md))
        if quote_count == 0:
            result.gaps.append("Nenhum fato citado literalmente (>) — faltam evidências")

        if quote_count < 3:
            result.suggestions.append("Incluir mais citações literais dos dados do grafo")

        return result


# ──────────────────────────────────────────────
# ReportAgent Principal
# ──────────────────────────────────────────────

class ReportAgent:
    """
    Agente de relatório com ciclo ReACT + Reflexão.

    Pipeline:
      1. Planning — analisa contexto e gera sumário
      2. Generate — para cada seção, executa ReACT loop
      3. Reflect — verifica qualidade em 3 dimensões
    """

    MIN_SECTIONS = 2
    MAX_SECTIONS = 5
    MIN_TOOL_CALLS_PER_SECTION = 3
    MAX_TOOL_CALLS_PER_SECTION = 5

    def __init__(self, graph_id: str, requirement: str,
                 mock: bool = True):
        self.graph_id = graph_id
        self.requirement = requirement
        self.tools = MockGraphTools(graph_id, requirement) if mock else None
        self.reflector = ReflectionEngine()

    # ── Fase 1: Planning ─────────────────────

    def plan_outline(self) -> ReportOutline:
        """
        Planeja o sumário do relatório com base no contexto.

        Em produção, usa LLM para analisar o contexto e gerar
        seções. Na simulação, usa templates pré-definidos.
        """
        # Na simulação, geramos um template baseado no requisito
        req_lower = self.requirement.lower()

        if "impacto" in req_lower or "impact" in req_lower:
            sections = [
                ReportSection("Cenário e Contexto"),
                ReportSection("Impactos Imediatos"),
                ReportSection("Reações dos Envolvidos"),
            ]
        elif "tendência" in req_lower or "trend" in req_lower:
            sections = [
                ReportSection("Panorama Atual"),
                ReportSection("Tendências Emergentes"),
                ReportSection("Projeções Futuras"),
            ]
        elif "regulação" in req_lower or "regulation" in req_lower:
            sections = [
                ReportSection("Contexto Regulatório"),
                ReportSection("Impacto no Setor"),
                ReportSection("Estratégias de Adaptação"),
                ReportSection("Riscos e Oportunidades"),
            ]
        else:
            sections = [
                ReportSection("Contexto e Antecedentes"),
                ReportSection("Análise Principal"),
                ReportSection("Conclusões e Recomendações"),
            ]

        title = self._generate_title()
        summary = f"Relatório de simulação: {self.requirement}"

        return ReportOutline(title=title, summary=summary, sections=sections)

    def _generate_title(self) -> str:
        """Gera título a partir do requisito."""
        words = self.requirement.split()
        short = " ".join(words[:8])
        return f"Análise Preditiva: {short}"

    # ── Fase 2: ReACT Generation ─────────────

    def generate_section(self, section: ReportSection,
                         outline: ReportOutline,
                         previous_content: str = "") -> str:
        """
        Gera conteúdo de uma seção usando ciclo ReACT.

        Pipeline interno:
          1. Thought: define o que precisa saber
          2. Action: chama ferramenta
          3. Observation: analisa resultado
          4. Repeat: até informação suficiente
          5. Final: escreve conteúdo
        """
        tool_calls = 0
        all_observations = []

        # ReACT Loop
        while tool_calls < self.MAX_TOOL_CALLS_PER_SECTION:
            # Thought
            thought = self._generate_thought(section.title, tool_calls,
                                             outline.sections.index(section))

            # Action (alterna entre ferramentas para não viciar)
            if tool_calls % 3 == 0:
                obs = self.tools.insight_forge(f"{section.title}: {self.requirement}")
                action = "insight_forge"
            elif tool_calls % 3 == 1:
                obs = self.tools.panorama_search(section.title)
                action = "panorama_search"
            else:
                obs = self.tools.quick_search(section.title)
                action = "quick_search"

            tool_calls += 1
            all_observations.append({action: obs})

            # Observation — verificar se já temos info suficiente
            if tool_calls >= self.MIN_TOOL_CALLS_PER_SECTION:
                # Simulação: info suficiente após mínimo de calls
                break

        section.tool_calls = tool_calls

        # Final Answer: gerar conteúdo a partir das observações
        content = self._synthesize_content(section.title, all_observations)
        section.content = content
        section.status = "completed"

        return content

    def _generate_thought(self, title: str, call_num: int,
                          section_idx: int) -> str:
        """Gera pensamento direcionado para a tool call."""
        thoughts = [
            f"Entender o contexto fundamental de '{title}'",
            f"Buscar dados temporais e evolutivos sobre '{title}'",
            f"Verificar fatos específicos e evidências sobre '{title}'",
            f"Explorar relações e conexões de '{title}' com outros tópicos",
            f"Identificar padrões e insights em '{title}'",
        ]
        idx = min(call_num, len(thoughts) - 1)
        return thoughts[idx]

    def _synthesize_content(self, title: str,
                            observations: List[Dict]) -> str:
        """
        Sintetiza observações em conteúdo de seção.

        Em produção, usa LLM. Na simulação, template.
        """
        facts = set()
        for obs in observations:
            for key, val in obs.items():
                if isinstance(val, dict):
                    for fact_list in val.get("facts", []):
                        facts.add(fact_list)
                    for fact_list in val.get("active_facts", []):
                        facts.add(fact_list)

        facts_list = list(facts)[:5]

        content = f"**Análise de {title}**\n\n"
        content += f"A simulação de '{self.requirement}' revela padrões importantes "
        content += f"no contexto analisado.\n\n"

        if facts_list:
            content += "**Evidências encontradas:**\n\n"
            for f in facts_list:
                content += f'> "{f}"\n\n'

        content += "**Insights principais:**\n\n"
        content += (
            f"- O cenário simulado indica tendências que merecem atenção\n"
            f"- Os dados coletados sugerem necessidade de ação preventiva\n"
            f"- Múltiplas perspectivas foram consideradas na análise\n"
        )

        return content

    # ── Fase 3: Reflection ───────────────────

    def reflect_report(self, report_md: str) -> ReflectionResult:
        """Executa reflexão completa no relatório gerado."""
        return self.reflector.reflect(report_md, self.requirement)

    # ── Pipeline Completo ────────────────────

    def generate_report(self) -> str:
        """Gera relatório completo: Planning → ReACT → Reflection."""
        parts = []

        # Fase 1: Planning
        outline = self.plan_outline()
        parts.append(f"# {outline.title}\n")
        parts.append(f"> {outline.summary}\n")

        # Fase 2: ReACT Generation
        previous = ""
        for i, section in enumerate(outline.sections):
            content = self.generate_section(section, outline, previous)
            parts.append(f"## {section.title}\n")
            parts.append(content)
            previous += content

        report = "\n".join(parts)

        # Fase 3: Reflection
        reflection = self.reflect_report(report)
        parts.append("\n---\n")
        parts.append(reflection.to_text())

        return "\n".join(parts)


# ──────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ReportAgent — Geração de Relatórios com ReACT + Reflection"
    )
    parser.add_argument("mode", nargs="?", default="full",
                        choices=["full", "plan", "reflect"],
                        help="Modo de operação")
    parser.add_argument("--graph", default="mirofish_abc", help="Graph ID")
    parser.add_argument("--requirement", default="",
                        help="Requisito/contexto da simulação")
    parser.add_argument("--input", default=None,
                        help="Arquivo de entrada (para reflect)")
    parser.add_argument("--output", default=None, help="Arquivo de saída")
    parser.add_argument("--mock", action="store_true", default=True,
                        help="Usar dados simulados")

    args = parser.parse_args()

    agent = ReportAgent(args.graph, args.requirement, mock=args.mock)

    if args.mode == "full":
        print("🤖 ReportAgent: Iniciando geração completa...")
        print(f"📋 Requisito: {args.requirement}")
        print(f"🔗 Graph ID: {args.graph}")
        print()

        report = agent.generate_report()

        if args.output:
            Path(args.output).write_text(report, encoding="utf-8")
            print(f"✅ Relatório salvo em: {args.output}")
        else:
            print(report)

    elif args.mode == "plan":
        outline = agent.plan_outline()
        print(json.dumps(outline.to_dict(), indent=2, ensure_ascii=False))

    elif args.mode == "reflect":
        if not args.input:
            print("ERRO: --input é obrigatório no modo reflect")
            sys.exit(1)

        report_md = Path(args.input).read_text(encoding="utf-8")
        reflection = agent.reflect_report(report_md)
        print(reflection.to_text())


if __name__ == "__main__":
    main()
