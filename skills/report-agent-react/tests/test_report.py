"""
TDD tests for ReportAgent — ReACT + Reflection para geracao de relatorios.
CT-1: test_init — inicializacao de ReportAgent e ReflectionEngine
CT-2: test_plan_outline — geracao de ReportOutline com secoes
CT-3: test_generate_section — geracao de conteudo via ReACT mock
CT-4: test_available — reflexao em 3 dimensoes sobre texto
"""

import os
import sys
import pytest

SCRIPT_DIR = os.path.join(os.path.dirname(__file__), "..", "scripts")
sys.path.insert(0, SCRIPT_DIR)

from report_agent import (
    ReportAgent, ReflectionEngine, ReportOutline,
    ReportSection, ReflectionResult, MockGraphTools,
)


class TestReportAgent:

    def test_init(self):
        agent = ReportAgent("graph-001", "Analisar impacto da IA", mock=True)
        assert agent.graph_id == "graph-001"
        assert agent.requirement == "Analisar impacto da IA"
        assert agent.tools is not None
        assert isinstance(agent.reflector, ReflectionEngine)

    def test_plan_outline(self):
        agent = ReportAgent("graph-001", "Impacto da IA no mercado", mock=True)
        outline = agent.plan_outline()
        assert isinstance(outline, ReportOutline)
        assert len(outline.sections) >= agent.MIN_SECTIONS
        assert outline.title != ""
        assert outline.summary != ""

        assert all(isinstance(s, ReportSection) for s in outline.sections)
        assert all(s.status == "pending" for s in outline.sections)

    def test_generate_section(self):
        agent = ReportAgent("graph-001", "Impacto da IA no Brasil", mock=True)
        outline = agent.plan_outline()
        section = outline.sections[0]

        content = agent.generate_section(section, outline)
        assert content != ""
        assert section.status == "completed"
        assert section.tool_calls >= agent.MIN_TOOL_CALLS_PER_SECTION

    def test_available(self):
        engine = ReflectionEngine()
        report_md = """
# Relatorio Teste

## Introducao
Este relatorio analisa dados do mercado de IA.

## Resultados
Os resultados indicam crescimento significativo.
Possivelmente o setor continuara expandindo nos proximos anos.

## Conclusao
Recomenda-se monitoramento continuo.
"""
        result = engine.reflect(report_md, context="mercado de IA")
        assert isinstance(result, ReflectionResult)
        assert 0 <= result.consistency_score <= 1.0
        assert isinstance(result.consistency_issues, list)
        assert isinstance(result.gaps, list)
        assert isinstance(result.suggestions, list)
        assert isinstance(result.corrections, list)
