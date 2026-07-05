"""
Descoberta de Plugins — Varre entrypoints registrados e plugins do ecossistema.

Permite que a CLI canônica `ecosystem --list-plugins` e o comando `list-plugins`
enumerem todos os plugins disponíveis no ecossistema.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

# Caminho para o arquivo de registro de plugins do menu adaptativo
MENU_REGISTRY_PATH = Path(".menu_registry.json")

# Plugins internos conhecidos do ecossistema
KNOWN_PLUGINS: list[dict[str, Any]] = [
    {
        "name": "autoevolve",
        "version": "1.0.0",
        "description": "Ciclo autônomo de evolução Plan-Act-Reflect-Extract-Evolve",
        "type": "builtin",
    },
    {
        "name": "reversa",
        "version": "1.0.0",
        "description": "Orquestrador de engenharia reversa multiagente",
        "type": "builtin",
    },
    {
        "name": "cora-eval",
        "version": "1.0.0",
        "description": "Benchmark CORA-Eval para ciências exatas da natureza",
        "type": "builtin",
    },
    {
        "name": "manus-evolve",
        "version": "1.0.0",
        "description": "Motor de evolução autônoma Manus Evolve",
        "type": "builtin",
    },
    {
        "name": "quantum-nexus",
        "version": "1.0.0",
        "description": "Pipeline de computação quântica e QML",
        "type": "builtin",
    },
    {
        "name": "academic-pipeline",
        "version": "2.0.0",
        "description": "Pipeline de produção acadêmica Qualis A1",
        "type": "builtin",
    },
    {
        "name": "mcp-inventory",
        "version": "1.0.0",
        "description": "Inventário e descoberta de servidores MCP",
        "type": "builtin",
    },
]


def _load_menu_registry() -> list[dict[str, Any]]:
    """Carrega plugins registrados no arquivo .menu_registry.json."""
    if not MENU_REGISTRY_PATH.exists():
        return []
    try:
        with open(MENU_REGISTRY_PATH, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("plugins", data.get("commands", []))
        return []
    except (json.JSONDecodeError, OSError):
        return []


def list_plugins() -> list[dict[str, Any]]:
    """Retorna lista de todos os plugins disponíveis.

    Returns:
        Lista de dicionários com 'name', 'version', 'description', 'type'.
    """
    plugins = list(KNOWN_PLUGINS)
    registry_plugins = _load_menu_registry()
    for rp in registry_plugins:
        name = rp.get("name", rp.get("command", "unknown"))
        # Evita duplicatas com builtins
        if not any(p["name"] == name for p in plugins):
            plugins.append({
                "name": name,
                "version": rp.get("version", "0.0.0"),
                "description": rp.get("description", ""),
                "type": "registered",
            })
    return plugins
