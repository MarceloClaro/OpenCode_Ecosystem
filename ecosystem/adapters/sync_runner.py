"""
Adaptador para execução de sincronização do ecossistema.

Delega para o orquestrador de sincronização Nexus quando disponível.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


SYNC_SCRIPT = Path("nexus/scripts/sync_orchestrator.py")


def run_sync(force: bool = False) -> int:
    """Executa sincronização do ecossistema.

    Args:
        force: Se True, força sincronização completa mesmo sem mudanças.

    Returns:
        Código de saída (0 = sucesso).
    """
    if SYNC_SCRIPT.exists():
        cmd = [sys.executable, str(SYNC_SCRIPT)]
        if force:
            cmd.append("--force")
        print(f"Sincronizando ecossistema{' (forçado)' if force else ''}...")
        try:
            result = subprocess.run(cmd, cwd=Path.cwd())
            return result.returncode
        except Exception as e:
            print(f"ERRO na sincronização: {e}", file=sys.stderr)
            return 1
    else:
        print(
            "Aviso: sync_orchestrator.py não encontrado em nexus/scripts/.\n"
            "Execute manualmente os scanners do ecossistema:\n"
            "  python -m ecosystem doctor\n"
            "  python -m ecosystem status",
            file=sys.stderr,
        )
        return 1
