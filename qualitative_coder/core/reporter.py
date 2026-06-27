"""
QualitativeCoder Reporter — Geração de Relatórios
SPEC-048 | Ciclo R27

Gera relatórios em LaTeX, Markdown e JSON a partir dos dados de análise.
"""
from __future__ import annotations
import json
from typing import Any


class Reporter:
    """
    Gador de relatórios de análise qualitativa.

    Suporta formatos LaTeX, Markdown e JSON.
    """

    def __init__(self):
        """Inicializa o reporter."""
        pass

    def report(self, data: dict, format: str = "latex") -> Any:
        """
        Gera relatório no formato especificado.

        Args:
            data: Dict com 'categories' e 'triangulation'.
            format: Formato de saída ('latex', 'markdown', 'json').

        Returns:
            Relatório formatado.
        """
        if format == "latex":
            return self._report_latex(data)
        elif format == "markdown":
            return self._report_markdown(data)
        elif format == "json":
            return data
        else:
            raise ValueError(f"Formato não suportado: {format}")

    def _report_latex(self, data: dict) -> str:
        """Gera relatório em LaTeX."""
        categories = data.get("categories", [])
        triangulation = data.get("triangulation", {})

        lines = []
        lines.append("\\section{Análise Qualitativa}")
        lines.append("")
        lines.append("%% Gerado por QualitativeCoder v0.1.0 (SPEC-048)")
        lines.append("")

        # Categorias
        if categories:
            lines.append("\\subsection{Categorias Identificadas}")
            lines.append("")
            lines.append("\\begin{tabular}{llcc}")
            lines.append("\\toprule")
            lines.append("Categoria & Códigos & Frequência & Conf. Média \\\\")
            lines.append("\\midrule")

            for cat in categories:
                name = cat.get("category", "N/A")
                freq = cat.get("frequency", 0)
                conf = cat.get("avg_confidence", 0.0)
                codes = cat.get("codes", [])
                code_str = ", ".join(codes[:3])
                if len(codes) > 3:
                    code_str += "..."
                # Escapar caracteres LaTeX
                name = name.replace("_", "\\_")
                code_str = code_str.replace("_", "\\_")
                lines.append(f"{name} & {code_str} & {freq} & {conf:.2f} \\\\")

            lines.append("\\bottomrule")
            lines.append("\\end{tabular}")
            lines.append("")

        # Triangulação
        if triangulation:
            conv = triangulation.get("convergence", 0.0)
            div = triangulation.get("divergence", [])
            gaps = triangulation.get("gaps", [])

            lines.append("\\subsection{Triangulação}")
            lines.append("")
            lines.append(f"Grau de convergência: \\textbf{{{conv:.2f}}}")
            lines.append("")

            if div:
                lines.append("\\subsubsection{Divergências}")
                lines.append("")
                for d in div:
                    desc = d.get("description", "N/A")
                    desc = desc.replace("_", "\\_")
                    lines.append(f"\\item {desc}")
                lines.append("")

            if gaps:
                lines.append("\\subsubsection{Lacunas}")
                lines.append("")
                for g in gaps:
                    desc = g.get("description", "N/A")
                    desc = desc.replace("_", "\\_")
                    lines.append(f"\\item {desc}")
                lines.append("")

        if not categories and not triangulation:
            lines.append("Nenhuma análise qualitativa disponível.")
            lines.append("")

        return "\n".join(lines)

    def _report_markdown(self, data: dict) -> str:
        """Gera relatório em Markdown."""
        categories = data.get("categories", [])
        triangulation = data.get("triangulation", {})

        lines = []
        lines.append("## Análise Qualitativa")
        lines.append("")
        lines.append("*Gerado por QualitativeCoder v0.1.0 (SPEC-048)*")
        lines.append("")

        # Categorias
        if categories:
            lines.append("### Categorias Identificadas")
            lines.append("")
            lines.append("| Categoria | Códigos | Frequência | Conf. Média |")
            lines.append("|-----------|---------|------------|-------------|")

            for cat in categories:
                name = cat.get("category", "N/A")
                freq = cat.get("frequency", 0)
                conf = cat.get("avg_confidence", 0.0)
                codes = cat.get("codes", [])
                code_str = ", ".join(codes[:3])
                if len(codes) > 3:
                    code_str += "..."
                lines.append(f"| {name} | {code_str} | {freq} | {conf:.2f} |")

            lines.append("")

        # Triangulação
        if triangulation:
            conv = triangulation.get("convergence", 0.0)
            div = triangulation.get("divergence", [])
            gaps = triangulation.get("gaps", [])

            lines.append("### Triangulação")
            lines.append("")
            lines.append(f"**Grau de convergência: {conv:.2f}**")
            lines.append("")

            if div:
                lines.append("#### Divergências")
                lines.append("")
                for d in div:
                    lines.append(f"- {d.get('description', 'N/A')}")
                lines.append("")

            if gaps:
                lines.append("#### Lacunas")
                lines.append("")
                for g in gaps:
                    lines.append(f"- {g.get('description', 'N/A')}")
                lines.append("")

        if not categories and not triangulation:
            lines.append("Nenhuma análise qualitativa disponível.")
            lines.append("")

        return "\n".join(lines)
