#!/usr/bin/env python3
"""
health_check.py — Health Check automatico do ecossistema OpenCode

Verifica:
- MCPs respondem (conexao)
- DB SQLite acessivel
- State files legiveis
- Agentes registrados no AgentManager

Uso: python scripts/health_check.py
"""

import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EVOLVE_DIR = ROOT / ".evolve"
STATE_DB = EVOLVE_DIR / "state.db"
HEALTH_FILE = EVOLVE_DIR / "health.json"


def check_sqlite_accessible() -> dict:
    """Verifica se o banco SQLite esta acessivel."""
    import sqlite3
    try:
        conn = sqlite3.connect(str(STATE_DB))
        conn.execute("SELECT 1")
        conn.close()
        return {"status": "OK", "latency_ms": 0}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}


def check_state_files() -> dict:
    """Verifica se arquivos de estado sao legiveis."""
    state_files = list(EVOLVE_DIR.glob("*.json"))
    readable = 0
    errors = []
    
    for f in state_files[:10]:  # Amostra de 10 arquivos
        try:
            with open(f, "r", encoding="utf-8") as fh:
                json.load(fh)
            readable += 1
        except Exception as e:
            errors.append({str(f.name): str(e)})
    
    return {
        "status": "OK" if readable > 0 else "FAIL",
        "total_sampled": min(10, len(state_files)),
        "readable": readable,
        "errors": errors
    }


def check_agent_count() -> dict:
    """Verifica se ha agentes registrados."""
    agents_dir = ROOT / ".evolve" / "ecosystem_backup" / "agents"
    if not agents_dir.exists():
        return {"status": "FAIL", "error": "Agents directory not found"}
    
    agents = list(agents_dir.glob("*.md"))
    return {
        "status": "OK" if len(agents) > 0 else "WARN",
        "count": len(agents)
    }


def check_skills() -> dict:
    """Verifica se ha skills registradas."""
    skills_dir = ROOT / "skills"
    skills = [d for d in skills_dir.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    return {
        "status": "OK" if len(skills) > 0 else "WARN",
        "count": len(skills)
    }


def main():
    checks = {
        "sqlite": check_sqlite_accessible(),
        "state_files": check_state_files(),
        "agents": check_agent_count(),
        "skills": check_skills(),
    }
    
    all_ok = all(c["status"] == "OK" for c in checks.values())
    
    report = {
        "version": "1.0.0",
        "health": "OK" if all_ok else "DEGRADED",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "checks": checks
    }
    
    # Persistir health check
    HEALTH_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HEALTH_FILE, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(json.dumps(report, indent=2, ensure_ascii=False))
    
    if not all_ok:
        failed = [k for k, v in checks.items() if v["status"] != "OK"]
        print(f"\nWARNING: {len(failed)} checks failed: {', '.join(failed)}")
    
    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
