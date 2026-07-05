"""
Adaptador para execução do ciclo evolutivo do ecossistema.

Delega para o evolution_loop Nexus quando disponível.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


EVOLVE_SCRIPT = Path("nexus/evolution_loop.py")


def run_evolve(dry_run: bool = False) -> int:
    """Executa ciclo evolutivo do ecossistema.

    Args:
        dry_run: Se True, simula o ciclo sem aplicar mudanças.

    Returns:
        Código de saída (0 = sucesso).
    """
    if EVOLVE_SCRIPT.exists():
        cmd = [sys.executable, str(EVOLVE_SCRIPT)]
        if dry_run:
            cmd.append("--dry-run")
        print(f"Ciclo evolutivo{' (simulação)' if dry_run else ''}...")
        try:
            result = subprocess.run(cmd, cwd=Path.cwd())
            return result.returncode
        except Exception as e:
            print(f"ERRO no ciclo evolutivo: {e}", file=sys.stderr)
            return 1
    else:
        print(
            "Aviso: evolution_loop.py não encontrado em nexus/.\n"
            "Use 'python -m ecosystem doctor' para diagnóstico completo.",
            file=sys.stderr,
        )
        return 1
