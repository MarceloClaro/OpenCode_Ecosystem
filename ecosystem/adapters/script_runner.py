"""
Adaptador para execução de scripts.
"""

import subprocess
import sys
from pathlib import Path


# Mapeamento de nomes conhecidos para caminhos
KNOWN_SCRIPTS: dict[str, str] = {
    "menu": "menu.py",
    "sync": "nexus/scripts/sync_orchestrator.py",
    "evolve": "nexus/evolution_loop.py",
    "audit": "ecosystem-auditor/scripts/audit_ecosystem.py",
    "test_env": "tests/test_environment.sh",
    "dashboard": "nexus/dashboard_server.py",
    "asde": "nexus/scripts/asde_engine.py",
}


def run_script(script: str | None, args: list[str] | None = None) -> int:
    """Executa um script no ecossistema.

    Args:
        script: Nome do script ou caminho
        args: Argumentos para o script

    Returns:
        Código de saída
    """
    if not script:
        print("Uso: ecosystem run <script> [args...]")
        print("\nScripts conhecidos:")
        for name, path in sorted(KNOWN_SCRIPTS.items()):
            exists = "✅" if Path(path).exists() else "❌"
            print(f"  {exists} {name:12s} → {path}")
        return 0

    # Resolve caminho
    if script in KNOWN_SCRIPTS:
        script_path = KNOWN_SCRIPTS[script]
    else:
        script_path = script

    path = Path(script_path)
    if not path.exists():
        print(f"ERRO: Script não encontrado: {script_path}", file=sys.stderr)
        return 1

    cmd = [sys.executable, str(path)]
    if args:
        cmd.extend(args)

    try:
        result = subprocess.run(cmd, cwd=path.parent if path.parent else None)
        return result.returncode
    except FileNotFoundError:
        print(f"ERRO: Python não encontrado", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"ERRO ao executar script: {e}", file=sys.stderr)
        return 1
