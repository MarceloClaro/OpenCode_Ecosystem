#!/usr/bin/env python3
"""MCP Server - Self-Healer do ecossistema OpenCode.

Expõe ferramentas de diagnóstico e auto-cura via protocolo MCP (stdio).
Uso: python nexus/mcp_self_healer.py
"""

import sys, json, traceback
from pathlib import Path

# Garante que o workspace está no path
WORKSPACE = Path(__file__).parent.parent.resolve()
sys.path.insert(0, str(WORKSPACE))

from nexus.scripts.self_healer import (
    check_cjk_leaks,
    check_frontmatter,
    check_skill_sizes,
    check_scripts_syntax,
    fix_cjk_leaks,
    fix_frontmatter,
    check_and_report,
    auto_fix,
)

from nexus.skills_registry import build_registry as build_skills_registry

REGISTRY_PATH = WORKSPACE / "nexus" / "skills_registry.json"

# ─── Protocolo MCP (stdio) ───────────────────────────────────────────────


def respond(msg: dict):
    """Envia resposta JSON-RPC no stdout."""
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def make_error(msg: str, code: int = -32603) -> dict:
    return {"jsonrpc": "2.0", "error": {"code": code, "message": msg}, "id": None}


def handle_request(msg: dict):
    method = msg.get("method", "")
    req_id = msg.get("id")

    if method == "initialize":
        respond({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {
                        "listChanged": False
                    }
                },
                "serverInfo": {
                    "name": "mcp-self-healer",
                    "version": "1.0.0"
                }
            }
        })
        return

    if method == "notifications/initialized":
        return  # No response needed

    if method == "tools/list":
        respond({
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "health_check",
                        "description": "Varre o ecossistema em busca de anomalias: leaks CJK em SKILL.md, problemas de frontmatter, erros de sintaxe Python, skills acima de 2.5KB. Retorna relatório completo.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": "health_fix",
                        "description": "Corrige automaticamente anomalias encontradas: remove CJK leaks de SKILL.md e adiciona frontmatter faltante. Erros de sintaxe requerem revisão manual.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": "health_stats",
                        "description": "Retorna estatísticas rápidas do ecossistema: total de skills, scripts Python, linhas de código, plugins.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    },
                    {
                        "name": "skills_report",
                        "description": "Relatório completo do Skills Registry: 43 skills escaneadas, categorias, status oversize, frontmatter, CJK. Lê do skills_registry.json persistente.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "category": {
                                    "type": "string",
                                    "description": "Filtrar por categoria (ex.: juridico, research, system). Omite para todas."
                                },
                                "oversize_only": {
                                    "type": "boolean",
                                    "description": "Se true, retorna apenas skills oversize (>2.5KB)"
                                }
                            },
                            "required": []
                        }
                    }
                ]
            }
        })
        return

    if method == "tools/call":
        tool_name = msg.get("params", {}).get("name", "")
        try:
            if tool_name == "health_check":
                report = check_and_report()
                respond({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(report, indent=2, ensure_ascii=False)
                            }
                        ]
                    }
                })

            elif tool_name == "health_fix":
                report = check_and_report()
                result = auto_fix(report)
                respond({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2, ensure_ascii=False)
                            }
                        ]
                    }
                })

            elif tool_name == "health_stats":
                stats = {
                    "skills": len(list(WORKSPACE.rglob("**/SKILL.md"))),
                    "scripts": len(list(WORKSPACE.rglob("*.py"))),
                    "plugins": len(list(WORKSPACE.rglob("plugins/*.ts"))),
                    "cjk_leaks": len(check_cjk_leaks()),
                    "frontmatter_issues": len(check_frontmatter()),
                }
                respond({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(stats, indent=2, ensure_ascii=False)
                            }
                        ]
                    }
                })

            elif tool_name == "skills_report":
                params = msg.get("params", {}).get("arguments", {})
                category = params.get("category")
                oversize_only = params.get("oversize_only", False)

                if REGISTRY_PATH.exists():
                    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
                else:
                    registry = build_skills_registry()

                result = dict(registry)  # shallow copy

                # Filtros
                if category:
                    result["skills"] = [
                        s for s in result["skills"]
                        if s["category"] == category
                    ]
                if oversize_only:
                    result["skills"] = [
                        s for s in result["skills"]
                        if s["is_oversize"]
                    ]

                # Atualiza summary para refletir filtros
                result["summary"]["filtered_count"] = len(result["skills"])
                result["summary"]["filter_oversize"] = oversize_only
                result["summary"]["filter_category"] = category or "all"

                respond({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "result": {
                        "content": [
                            {
                                "type": "text",
                                "text": json.dumps(result, indent=2, ensure_ascii=False)
                            }
                        ]
                    }
                })

            else:
                respond({
                    "jsonrpc": "2.0",
                    "id": req_id,
                    "error": {"code": -32601, "message": f"Tool not found: {tool_name}"}
                })

        except Exception as e:
            respond({
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": f"{type(e).__name__}: {str(e)}"}
            })
        return

    # Método não reconhecido
    if req_id is not None:
        respond({
            "jsonrpc": "2.0",
            "id": req_id,
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        })


def main():
    """Loop principal: lê JSON-RPC do stdin, processa, responde no stdout."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
            handle_request(msg)
        except json.JSONDecodeError as e:
            respond(make_error(f"Invalid JSON: {e}"))
        except Exception as e:
            respond(make_error(f"Internal error: {type(e).__name__}: {e}"))


if __name__ == "__main__":
    main()
