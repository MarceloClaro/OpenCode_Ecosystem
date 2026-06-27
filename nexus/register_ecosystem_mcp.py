#!/usr/bin/env python3
"""
REGISTER ECOSYSTEM MCP SERVER
=============================
Registra o servidor MCP do OpenCode Ecosystem no Antigravity CLI,
adicionando a configuração ao settings.json do Antigravity.

Uso:
  python register_ecosystem_mcp.py              # Registrar
  python register_ecosystem_mcp.py --unregister  # Remover
  python register_ecosystem_mcp.py --status      # Verificar status

SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
"""

import json
import sys
import os
from pathlib import Path

# ============================================================
# Constantes
# ============================================================

ANTIGRAVITY_DIR = Path.home() / ".gemini" / "antigravity-cli"
SETTINGS_FILE = ANTIGRAVITY_DIR / "settings.json"
ECOSYSTEM_ROOT = Path(__file__).parent.parent
MCP_SERVER_SCRIPT = Path(__file__).parent / "ecosystem_capabilities_server.py"

MCP_SERVER_NAME = "ecosystem-capabilities"
MCP_SERVER_CONFIG = {
    "command": "python",
    "args": [str(MCP_SERVER_SCRIPT)],
    "env": {
        "ECOSYSTEM_ROOT": str(ECOSYSTEM_ROOT),
    },
}


def load_settings() -> dict:
    """Carrega o settings.json do Antigravity."""
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError) as e:
            print(f"[AVISO] Erro ao ler settings.json: {e}")
    return {}


def save_settings(settings: dict) -> None:
    """Persiste o settings.json do Antigravity."""
    SETTINGS_FILE.write_text(
        json.dumps(settings, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"[OK] Settings salvo em: {SETTINGS_FILE}")


def register() -> None:
    """Registra o MCP server do ecossistema no Antigravity."""
    print("=" * 60)
    print("REGISTRO DO MCP SERVER DO OPENCODE ECOSYSTEM")
    print("=" * 60)
    print(f"Antigravity dir: {ANTIGRAVITY_DIR}")
    print(f"Settings file:   {SETTINGS_FILE}")
    print(f"MCP server:      {MCP_SERVER_SCRIPT}")
    print(f"Ecosystem root:  {ECOSYSTEM_ROOT}")
    print()

    # Verificar se o script do servidor existe
    if not MCP_SERVER_SCRIPT.exists():
        print(f"[ERRO] Script do servidor MCP não encontrado: {MCP_SERVER_SCRIPT}")
        sys.exit(1)

    # Carregar settings existente
    settings = load_settings()

    # Adicionar/Atualizar configuração MCP
    if "mcpServers" not in settings:
        settings["mcpServers"] = {}

    settings["mcpServers"][MCP_SERVER_NAME] = MCP_SERVER_CONFIG

    # Salvar
    save_settings(settings)

    print()
    print("[OK] MCP Server registrado com sucesso!")
    print(f"     Nome: {MCP_SERVER_NAME}")
    print(f"     Comando: {MCP_SERVER_CONFIG['command']}")
    print(f"     Args: {MCP_SERVER_CONFIG['args']}")
    print()
    print("PRÓXIMOS PASSOS:")
    print("  1. Reinicie o Antigravity CLI (agy)")
    print("  2. Execute /mcp dentro do TUI para verificar se o servidor está ativo")
    print("  3. Use as ferramentas eco_* disponíveis")
    print()
    print("FERRAMENTAS DISPONÍVEIS:")
    print("  - eco_run_noological_scanner    (Scanner Noológico)")
    print("  - eco_run_teleological_scanner  (Scanner Teleológico)")
    print("  - eco_run_evolutionary_scanner  (Scanner Evolutivo)")
    print("  - eco_run_potentiality_v2       (Potentiality Estimator v2)")
    print("  - eco_run_social_impact         (Social Impact Scanner)")
    print("  - eco_run_full_pipeline         (Pipeline Completo)")
    print("  - eco_z3_verify                 (Verificação Formal Z3)")
    print("  - eco_sympy_analyze             (Análise Simbólica SymPy)")
    print("  - eco_critical_analyze          (Análise de Falácias)")
    print("  - eco_list_skills               (227+ Skills)")
    print("  - eco_list_agents               (128+ Agentes)")
    print("  - eco_list_mcps                 (46 MCPs)")
    print("  - eco_status                    (Status do Ecossistema)")


def unregister() -> None:
    """Remove o MCP server do ecossistema do Antigravity."""
    print("=" * 60)
    print("REMOÇÃO DO MCP SERVER DO OPENCODE ECOSYSTEM")
    print("=" * 60)

    settings = load_settings()

    if "mcpServers" in settings and MCP_SERVER_NAME in settings["mcpServers"]:
        del settings["mcpServers"][MCP_SERVER_NAME]
        save_settings(settings)
        print(f"[OK] MCP Server '{MCP_SERVER_NAME}' removido com sucesso!")
    else:
        print(f"[INFO] MCP Server '{MCP_SERVER_NAME}' não estava registrado.")


def status() -> None:
    """Verifica o status do registro do MCP server."""
    print("=" * 60)
    print("STATUS DO MCP SERVER DO OPENCODE ECOSYSTEM")
    print("=" * 60)

    settings = load_settings()
    mcp_servers = settings.get("mcpServers", {})

    if MCP_SERVER_NAME in mcp_servers:
        config = mcp_servers[MCP_SERVER_NAME]
        print(f"[OK] MCP Server '{MCP_SERVER_NAME}' está REGISTRADO")
        print(f"     Comando: {config.get('command', 'N/A')}")
        print(f"     Args: {config.get('args', [])}")
        print(f"     Env: {config.get('env', {})}")

        # Verificar se o script existe
        script_path = Path(config.get("args", [""])[0]) if config.get("args") else None
        if script_path and script_path.exists():
            print(f"     Script: EXISTE ({script_path})")
        else:
            print(f"     Script: NÃO ENCONTRADO")
    else:
        print(f"[INFO] MCP Server '{MCP_SERVER_NAME}' NÃO está registrado")
        print(f"       Execute: python register_ecosystem_mcp.py")

    # Listar todos os MCPs registrados
    print()
    print("TODOS OS MCP SERVERS REGISTRADOS:")
    if mcp_servers:
        for name, config in mcp_servers.items():
            marker = " [ECOSYSTEM]" if name == MCP_SERVER_NAME else ""
            print(f"  - {name}: {config.get('command', 'N/A')} {config.get('args', [])}{marker}")
    else:
        print("  (nenhum)")


# ============================================================
# Entrypoint
# ============================================================

if __name__ == "__main__":
    args = sys.argv[1:]

    if "--unregister" in args:
        unregister()
    elif "--status" in args:
        status()
    else:
        register()
