"""
QualitativeCoder MCP Server — Integração com OpenCode Ecosystem
SPEC-048 | Ciclo R27

Expõe ferramentas de análise qualitativa como MCP (Model Context Protocol).
"""
import json
from typing import Any

# Importar módulo principal
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from qualitative_coder import QualitativeCoder


# Instância global do coder
_coder = QualitativeCoder(language="pt-br")


def code_text(text: str, method: str = "open") -> str:
    """
    Codifica texto qualitativo em unidades de sentido.

    Args:
        text: Texto a ser codificado.
        method: Método de codificação ('open' ou 'axial').

    Returns:
        JSON com lista de códigos.
    """
    codes = _coder.code(text, method=method)
    return json.dumps(codes, ensure_ascii=False, indent=2)


def categorize_codes(codes_json: str) -> str:
    """
    Categoriza códigos em temas.

    Args:
        codes_json: JSON com lista de códigos.

    Returns:
        JSON com categorias.
    """
    codes = json.loads(codes_json)
    categories = _coder.categorize(codes)
    return json.dumps(categories, ensure_ascii=False, indent=2)


def triangulate(quant_json: str, qual_json: str, method: str = "convergence") -> str:
    """
    Triangula dados quantitativos e qualitativos.

    Args:
        quant_json: JSON com dados quantitativos.
        qual_json: JSON com dados qualitativos.
        method: Método de triangulação.

    Returns:
        JSON com resultado da triangulação.
    """
    data_quant = json.loads(quant_json)
    data_qual = json.loads(qual_json)
    result = _coder.triangulate(data_quant, data_qual, method=method)
    return json.dumps(result, ensure_ascii=False, indent=2)


def generate_report(data_json: str, format: str = "latex") -> str:
    """
    Gera relatório da análise.

    Args:
        data_json: JSON com categories e triangulation.
        format: Formato de saída ('latex', 'markdown', 'json').

    Returns:
        Relatório formatado.
    """
    data = json.loads(data_json)
    report = _coder.report(data, format=format)
    if isinstance(report, dict):
        return json.dumps(report, ensure_ascii=False, indent=2)
    return report


def analyze_interview(text: str, method: str = "axial") -> str:
    """
    Pipeline completo: codifica → categoriza → gera relatório.

    Args:
        text: Texto da entrevista.
        method: Método de codificação.

    Returns:
        JSON com codes, categories e report.
    """
    # Step 1: Code
    codes = _coder.code(text, method=method)

    # Step 2: Categorize
    categories = _coder.categorize(codes)

    # Step 3: Report
    report = _coder.report(
        {"categories": categories, "triangulation": {"convergence": 0.0, "divergence": [], "gaps": []}},
        format="markdown",
    )

    result = {
        "codes": codes,
        "categories": categories,
        "report": report,
    }
    return json.dumps(result, ensure_ascii=False, indent=2)


# Registro de ferramentas MCP
MCP_TOOLS = [
    {
        "name": "code_text",
        "description": "Codifica texto qualitativo em unidades de sentido (métodos open ou axial)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Texto a ser codificado"},
                "method": {"type": "string", "enum": ["open", "axial"], "default": "open"},
            },
            "required": ["text"],
        },
    },
    {
        "name": "categorize_codes",
        "description": "Categoriza códigos em temas usando clustering temático",
        "inputSchema": {
            "type": "object",
            "properties": {
                "codes_json": {"type": "string", "description": "JSON com lista de códigos"},
            },
            "required": ["codes_json"],
        },
    },
    {
        "name": "triangulate",
        "description": "Triangula dados quantitativos e qualitativos",
        "inputSchema": {
            "type": "object",
            "properties": {
                "quant_json": {"type": "string", "description": "JSON com dados quantitativos"},
                "qual_json": {"type": "string", "description": "JSON com dados qualitativos"},
                "method": {"type": "string", "enum": ["convergence", "divergence", "mixed"], "default": "convergence"},
            },
            "required": ["quant_json", "qual_json"],
        },
    },
    {
        "name": "generate_report",
        "description": "Gera relatório da análise qualitativa (LaTeX, Markdown ou JSON)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "data_json": {"type": "string", "description": "JSON com categories e triangulation"},
                "format": {"type": "string", "enum": ["latex", "markdown", "json"], "default": "latex"},
            },
            "required": ["data_json"],
        },
    },
    {
        "name": "analyze_interview",
        "description": "Pipeline completo: codifica → categoriza → gera relatório",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "Texto da entrevista"},
                "method": {"type": "string", "enum": ["open", "axial"], "default": "axial"},
            },
            "required": ["text"],
        },
    },
]
