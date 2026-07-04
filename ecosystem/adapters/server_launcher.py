"""
Adaptador para lançamento de servidores.
"""

import subprocess
import sys
from pathlib import Path


SERVERS: dict[str, str] = {
    "dashboard": "nexus/dashboard_server.py",
    "api": "editais-br/api/main.py",
    "mcp": "nexus/antigravity_mcp_server.py",
}


def launch_server(service: str, port: int | None = None) -> int:
    """Inicia um servidor do ecossistema.

    Args:
        service: Nome do serviço
        port: Porta opcional

    Returns:
        Código de saída
    """
    script = SERVERS.get(service)
    if not script:
        print(f"ERRO: Serviço desconhecido: {service}", file=sys.stderr)
        print(f"Serviços disponíveis: {', '.join(SERVERS.keys())}")
        return 1

    path = Path(script)
    if not path.exists():
        print(f"ERRO: Script não encontrado: {script}", file=sys.stderr)
        return 1

    cmd = [sys.executable, str(path)]
    if port:
        cmd.extend(["--port", str(port)])

    print(f"Iniciando {service}...")
    try:
        result = subprocess.run(cmd)
        return result.returncode
    except Exception as e:
        print(f"ERRO: {e}", file=sys.stderr)
        return 1
