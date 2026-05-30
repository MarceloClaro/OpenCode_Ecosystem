"""
MASWOS V5 NEXUS — Launcher unificado dos 3 servidores MCP.
Uso:
  python launch_maswos_mcps.py          # Inicia os 3 em stdio (um de cada vez)
  python launch_maswos_mcps.py --sse    # Inicia os 3 em SSE (background)
  python launch_maswos_mcps.py --sse --port 3001  # Apenas juridico na porta 3001
"""

import sys, subprocess, os, time, signal

BASE = os.path.dirname(os.path.abspath(__file__))
SERVERS = {
    "maswos-juridico": ("juridico_server.py", 3001),
    "maswos-mcp": ("maswos_server.py", 3002),
    "maswos-rag": ("rag_server.py", 3003),
}


def launch_stdio(target):
    """Executa um servidor em modo stdio (bloqueante)."""
    script = os.path.join(BASE, target)
    print(f"Iniciando {target} em modo stdio...", file=sys.stderr)
    proc = subprocess.Popen(
        [sys.executable, script],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    return proc


def launch_sse(target, port):
    """Executa um servidor em modo SSE (background)."""
    script = os.path.join(BASE, target)
    print(f"Iniciando {target} em modo SSE na porta {port}...", file=sys.stderr)
    proc = subprocess.Popen(
        [sys.executable, script, "--sse", "--port", str(port)],
        stdout=subprocess.DEVNULL,
        stderr=sys.stderr
    )
    return proc


if __name__ == "__main__":
    use_sse = "--sse" in sys.argv

    # Check if specific server requested
    specific = None
    for name in SERVERS:
        if f"--{name}" in sys.argv:
            specific = name
            break

    procs = []
    try:
        for name, (script, port) in SERVERS.items():
            if specific and name != specific:
                continue
            if use_sse:
                p = launch_sse(script, port)
            else:
                p = launch_stdio(script)
            procs.append(p)
            if specific:
                break

        if use_sse:
            print(f"\n{len(procs)} servidor(es) MCP rodando em background.", file=sys.stderr)
            print("Pressione Ctrl+C para parar todos.", file=sys.stderr)
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                pass
        else:
            # Em stdio, apenas um servidor roda por vez
            procs[0].wait()

    finally:
        for p in procs:
            if p.poll() is None:
                if sys.platform == "win32":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)],
                                   capture_output=True)
                else:
                    p.terminate()
                p.wait()
