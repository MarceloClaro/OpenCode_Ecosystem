#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TokenEconomyMonitor v1.0 — Monitor de Economia de Tokens
==========================================================
Rastreia consumo de tokens por interação, sessão e nível de publicação,
comparando com orçamentos predefinidos para cada nível.

Níveis de Publicação (3 níveis):
  Nível 1 — Magnum/Tese/Qualis A1: até 43 agentes, sem economia (rigor máximo)
  Nível 2 — Standard Paper/Q1-Q2: ~20 agentes, eficiência exigida
  Nível 3 — Short Communication: max 10 agentes, pipeline expresso

Estratégias de Otimização:
  1. Contexto em chinês (+40% densidade)
  2. Progressive disclosure (SKILL.md ≤ 2.500B)
  3. Edição cirúrgica (apenas delta)
  4. MCP Lazy Init
  5. Modelo gratuito 200K contexto

Uso:
  from token_economy_monitor import TokenEconomyMonitor
  monitor = TokenEconomyMonitor(level=1)
  monitor.record_usage(input_tokens=500, output_tokens=200)
  monitor.get_efficiency_report()
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

BRAZIL_TZ = timezone.utc

# Orçamentos por nível (em tokens estimados)
LEVEL_BUDGETS: dict[int, dict[str, Any]] = {
    1: {  # Magnum/Tese/Qualis A1
        "name": "Magnum/Tese/Qualis A1",
        "agents": 43,
        "budget_per_interaction": 8000,
        "budget_per_session": 500_000,
        "economy_mode": False,
        "description": "Rigor máximo, sem economia de tokens",
    },
    2: {  # Standard Paper
        "name": "Standard Paper/Q1-Q2",
        "agents": 20,
        "budget_per_interaction": 4000,
        "budget_per_session": 200_000,
        "economy_mode": True,
        "description": "Eficiência de tempo exigida",
    },
    3: {  # Short Communication
        "name": "Short Communication/Congresso",
        "agents": 10,
        "budget_per_interaction": 1500,
        "budget_per_session": 50_000,
        "economy_mode": True,
        "description": "Pipeline expresso, economia máxima",
    },
}


@dataclass
class TokenUsage:
    """Registro de uso de tokens em uma interação."""
    interaction_id: str
    timestamp: str
    estimated_input: int
    estimated_output: int
    pipeline_stage: str
    context_size: int = 200_000


class TokenEconomyMonitor:
    """Monitor de economia de tokens por sessão.

    Rastreia consumo, compara com orçamento e sugere otimizações.
    """

    def __init__(self, level: int = 1, session_id: str = "") -> None:
        self.level = level
        self.session_id = session_id
        self.budget = LEVEL_BUDGETS.get(level, LEVEL_BUDGETS[1])
        self.usage_history: list[TokenUsage] = []
        self.total_input = 0
        self.total_output = 0
        self.interaction_count = 0
        self.monitor_dir = Path(__file__).parent.parent.parent.parent / ".evolve" / "token-monitor"

    def record_usage(
        self,
        interaction_id: str,
        estimated_input: int = 0,
        estimated_output: int = 0,
        pipeline_stage: str = "",
    ) -> TokenUsage:
        """Registra uso de tokens em uma interação."""
        usage = TokenUsage(
            interaction_id=interaction_id,
            timestamp=datetime.now(BRAZIL_TZ).isoformat(),
            estimated_input=estimated_input,
            estimated_output=estimated_output,
            pipeline_stage=pipeline_stage,
        )
        self.usage_history.append(usage)
        self.total_input += estimated_input
        self.total_output += estimated_output
        self.interaction_count += 1
        return usage

    def get_efficiency_report(self) -> dict[str, Any]:
        """Gera relatório de eficiência de tokens."""
        session_budget = self.budget["budget_per_session"]
        session_used = self.total_input + self.total_output
        budget_remaining = max(0, session_budget - session_used)
        efficiency = (self.total_output / max(1, self.total_input)) if self.total_input > 0 else 0

        return {
            "level": self.level,
            "level_name": self.budget["name"],
            "economy_mode": self.budget["economy_mode"],
            "interactions": self.interaction_count,
            "total_input_tokens": self.total_input,
            "total_output_tokens": self.total_output,
            "total_tokens": session_used,
            "session_budget": session_budget,
            "budget_remaining": budget_remaining,
            "budget_used_pct": round(session_used / max(1, session_budget) * 100, 1),
            "efficiency_ratio": round(efficiency, 3),
            "avg_input_per_interaction": self.total_input // max(1, self.interaction_count),
            "avg_output_per_interaction": self.total_output // max(1, self.interaction_count),
            "estimated_savings_from_chinese": round(self.total_input * 0.40),
            "estimated_savings_from_progressive_disclosure": round(self.total_input * 0.25),
            "estimated_savings_from_lazy_init": round(self.total_input * 0.10),
        }

    def get_optimization_suggestions(self) -> list[str]:
        """Sugere otimizações baseadas no perfil de uso."""
        suggestions = []
        report = self.get_efficiency_report()

        if report["budget_used_pct"] > 80:
            suggestions.append(
                f"⚠️  Orçamento em {report['budget_used_pct']}%. "
                f"Considere reduzir para Nível {min(3, self.level + 1)}."
            )

        if report["efficiency_ratio"] < 0.3:
            suggestions.append(
                "⚠️  Baixa eficiência (output/input). "
                "Considere usar edição cirúrgica para reduzir output redundante."
            )

        if self.level == 1 and report["interactions"] > 50:
            suggestions.append(
                "💡 Nível 1 com muitas interações. "
                "Considere consolidar queries para reduzir round-trips."
            )

        if self.level == 3 and report["total_tokens"] > 60000:
            suggestions.append(
                "⚠️  Nível 3 excedendo orçamento. "
                "Considere migrar para Nível 2 se o rigor for necessário."
            )

        return suggestions

    def generate_markdown_report(self) -> str:
        """Gera relatório Markdown de economia de tokens."""
        r = self.get_efficiency_report()
        suggestions = self.get_optimization_suggestions()

        lines = [
            f"# Relatório de Economia de Tokens",
            f"",
            f"**Nível**: {r['level']} — {r['level_name']}",
            f"**Modo economia**: {'Sim' if r['economy_mode'] else 'Não (rigor máximo)'}",
            f"",
            f"## Consumo",
            f"",
            f"| Métrica | Valor |",
            f"|---------|-------|",
            f"| Interações | {r['interactions']} |",
            f"| Tokens entrada | {r['total_input_tokens']:,} |",
            f"| Tokens saída | {r['total_output_tokens']:,} |",
            f"| Tokens totais | {r['total_tokens']:,} |",
            f"| Orçamento | {r['session_budget']:,} |",
            f"| Restante | {r['budget_remaining']:,} ({r['budget_used_pct']}%) |",
            f"| Eficiência (out/in) | {r['efficiency_ratio']:.2f} |",
            f"| Médio in/interação | {r['avg_input_per_interaction']:,} |",
            f"| Médio out/interação | {r['avg_output_per_interaction']:,} |",
            f"",
            f"## Economias Estimadas",
            f"",
            f"| Estratégia | Tokens Economizados |",
            f"|-----------|-------------------:|",
            f"| Contexto em chinês (+40%) | {r['estimated_savings_from_chinese']:,} |",
            f"| Progressive disclosure (25%) | {r['estimated_savings_from_progressive_disclosure']:,} |",
            f"| MCP Lazy Init (10%) | {r['estimated_savings_from_lazy_init']:,} |",
            f"| **Total estimado** | **{r['estimated_savings_from_chinese'] + r['estimated_savings_from_progressive_disclosure'] + r['estimated_savings_from_lazy_init']:,}** |",
        ]

        if suggestions:
            lines.append("")
            lines.append("## Sugestões de Otimização")
            for s in suggestions:
                lines.append(f"- {s}")

        return "\n".join(lines)

    def save(self) -> Path:
        """Salva relatório em disco."""
        self.monitor_dir.mkdir(parents=True, exist_ok=True)
        path = self.monitor_dir / f"tokens-{self.session_id}.md"
        path.write_text(self.generate_markdown_report(), encoding="utf-8")
        return path
