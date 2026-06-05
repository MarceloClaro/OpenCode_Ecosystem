#!/usr/bin/env python3
"""Lançador do Dashboard do Ecossistema OpenCode.

Uso:
    python nexus/dashboard/start_dashboard.py          # Inicia na porta 8081
    python nexus/dashboard/start_dashboard.py 9090    # Porta customizada
"""

import sys, os, subprocess, time, webbrowser, signal
from pathlib import Path

WORKSPACE = Path(__file__).parent.parent.parent.resolve()
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8081
SERVER_SCRIPT = WORKSPACE / "nexus" / "dashboard_server.py"
LOG_DIR = WORKSPACE / "nexus" / "dashboard"

proc = None

def cleanup(signum=None, frame=None):
    if proc and proc.poll() is None:
        proc.terminate()
        print("\nDashboard encerrado.")
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

print(f"🚀 Iniciando OpenCode Ecosystem Dashboard...")
print(f"   Porta: {PORT}")
print(f"   URL:   http://localhost:{PORT}")
print("   Pressione Ctrl+C para encerrar\n")

proc = subprocess.Popen(
    [sys.executable, str(SERVER_SCRIPT), "--porta", str(PORT)],
    cwd=str(WORKSPACE),
    stdout=open(LOG_DIR / "stdout.log", "a"),
    stderr=open(LOG_DIR / "stderr.log", "a"),
)

# Aguarda servidor ficar pronto
for _ in range(10):
    time.sleep(0.5)
    if proc.poll() is not None:
        print(f"ERRO: Dashboard morreu (código {proc.returncode})")
        sys.exit(1)
    try:
        import urllib.request
        urllib.request.urlopen(f"http://localhost:{PORT}/", timeout=2)
        print("✅ Dashboard pronto!")
        webbrowser.open(f"http://localhost:{PORT}")
        break
    except:
        continue

proc.wait()
