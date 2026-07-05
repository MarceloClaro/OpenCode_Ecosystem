"""
Adaptador para execução de suítes de teste do ecossistema.

Delega para o pytest com seleção de suíte por diretório.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


TEST_SUITES: dict[str, str] = {
    "ecosystem": "tests/ecosystem/",
    "specs": "tests/",
    "core": "tests/core/",
    "nexus": "tests/nexus/",
    "all": "",
}


def run_tests(suite: str | None = None, verbose: bool = False) -> int:
    """Executa suítes de teste do ecossistema.

    Args:
        suite: Nome da suíte ('ecosystem', 'specs', 'core', 'nexus', 'all').
        verbose: Se True, ativa modo verboso do pytest.

    Returns:
        Código de saída do pytest.
    """
    import sys as _sys

    cmd = [sys.executable, "-m", "pytest"]

    if verbose:
        cmd.append("-v")

    if suite and suite in TEST_SUITES:
        test_path = TEST_SUITES[suite]
        cmd.append(test_path)
        print(f"Executando suíte '{suite}' ({test_path})...")
    elif suite and suite not in TEST_SUITES:
        # Assume caminho personalizado
        cmd.append(suite)
        print(f"Executando testes em: {suite}...")
    else:
        # Padrão: testes do ecossistema
        cmd.append("tests/ecosystem/")
        print("Executando testes do ecossistema...")

    cmd.extend(["-q", "--tb=short"])

    try:
        result = subprocess.run(cmd, cwd=Path.cwd())
        return result.returncode
    except Exception as e:
        print(f"ERRO ao executar testes: {e}", file=_sys.stderr)
        return 1
