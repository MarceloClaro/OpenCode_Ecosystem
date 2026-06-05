#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ECOSYSTEM BRIDGE v1.0 — Ponte Autonoma entre os 8 Componentes do Ecossistema OpenCode

Substitui o ECOSYSTEM_BRIDGE.md (documentacao estatica) por codigo executavel.
Conecta: editais-local, SEEKER, criador-artigo, nexus, evolution, quantum, plugins, skills

Pipeline autonomo:
  Dados (editais-local) -> Pesquisa (SEEKER) -> Artigo (criador-artigo) -> Evolucao (nexus/evolution)

Uso:
  python ecosystem_bridge.py health              # Health check de todos componentes
  python ecosystem_bridge.py route <pipeline>     # Roteia pipeline entre componentes
  python ecosystem_bridge.py discover             # Descobre componentes disponiveis
  python ecosystem_bridge.py watch                # Monitor continuo (loop)
  python ecosystem_bridge.py pipeline from-editais-to-article <edital_id>
"""

import json, sys, os, subprocess, time, logging
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Optional

ECO_ROOT = Path(r"C:\Users\marce\.config\opencode")
EDITAIS_LOCAL_ROOT = Path(r"C:\Users\marce\editais-local")
BRIDGE_STATE = ECO_ROOT / ".evolve" / "bridge-state.json"

COMPONENTS = {
    "editais-local": {
        "path": EDITAIS_LOCAL_ROOT,
        "health_endpoints": [
            ("db", lambda p: (p / "data" / "editais.db").exists()),
            ("cli", lambda p: (p / ".venv" / "Scripts" / "editais-local.exe").exists() or (p / "pyproject.toml").exists()),
            ("frontend", lambda p: (p / "frontend" / "dist" / "index.html").exists()),
            ("embeddings", lambda p: (p / "data" / "embeddings.npy").exists()),
        ],
        "weight": 1.0,
    },
    "basis-research": {
        "path": ECO_ROOT / "basis-research",
        "health_endpoints": [
            ("main", lambda p: (p / "main.py").exists()),
            ("agents", lambda p: len(list((p / "agents").glob("*.py"))) >= 3),
            ("db", lambda p: any((p / "db").glob("*.db*"))),
            ("tools", lambda p: (p / "tools" / "editais_hook.py").exists()),
        ],
        "weight": 1.0,
    },
    "criador-artigo": {
        "path": ECO_ROOT / "criador-artigo",
        "health_endpoints": [
            ("agents", lambda p: len(list((p / "agents").glob("*.md"))) >= 40),
            ("banca", lambda p: (p / "banca" / "iterative_correction_loop.py").exists()),
            ("corretor", lambda p: (p / "banca" / "ptbr_corrector.py").exists()),
            ("bridge", lambda p: True),
        ],
        "weight": 1.0,
    },
    "nexus": {
        "path": ECO_ROOT / "nexus",
        "health_endpoints": [
            ("scripts", lambda p: len(list((p / "scripts").glob("*.py"))) >= 20),
            ("orchestrator", lambda p: (p / "scripts" / "sync_orchestrator.py").exists()),
            ("references", lambda p: len(list((p / "references").glob("*.md"))) >= 10),
        ],
        "weight": 1.0,
    },
    "evolution": {
        "path": ECO_ROOT / "evolution",
        "health_endpoints": [
            ("skills", lambda p: len(list(p.glob("evo-*.md"))) >= 5),
            ("nexus-bridge", lambda p: (ECO_ROOT / "nexus" / "scripts" / "ecosystem_bridge.py").exists()),
            ("evolution-cycle", lambda p: (ECO_ROOT / "nexus" / "scripts" / "evolution_cycle.py").exists()),
        ],
        "weight": 1.0,
    },
    "quantum": {
        "path": ECO_ROOT / "quantum",
        "health_endpoints": [
            ("scripts", lambda p: len(list((p / "scripts").glob("*.py"))) >= 10),
            ("outputs", lambda p: len(list((p / "outputs").glob("*"))) >= 3),
            ("references", lambda p: len(list(p.glob("references/*.md"))) >= 10),
            ("frontend", lambda p: (p / "frontend" / "App.tsx").exists()),
        ],
        "weight": 1.0,
    },
    "plugins": {
        "path": ECO_ROOT / "plugins",
        "health_endpoints": [
            ("ecosystem-sync", lambda p: (p / "ecosystem-sync.ts").exists()),
            ("manus-evolve", lambda p: (p / "manus-evolve.ts").exists()),
            ("ecosystem-bridge-py", lambda p: (ECO_ROOT / "nexus" / "scripts" / "ecosystem_bridge.py").exists()),
        ],
        "weight": 1.0,
    },
    "skills": {
        "path": ECO_ROOT / "skills",
        "health_endpoints": [
            ("categories", lambda p: len([d for d in p.iterdir() if d.is_dir()]) >= 8),
            ("total", lambda p: len(list(p.rglob("*.md"))) >= 80),
            ("evolution-skills", lambda p: len(list((p / "evolution").glob("*.md"))) >= 1 or len(list((p / "research").glob("evo-*.md"))) >= 1),
            ("system-skills", lambda p: len(list((p / "system").glob("*.md"))) >= 5),
        ],
        "weight": 1.0,
    },
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(ECO_ROOT / ".evolve" / "bridge.log", encoding="utf-8"),
    ],
)
log = logging.getLogger("ecosystem-bridge")


@dataclass
class ComponentHealth:
    name: str
    exists: bool = False
    checks: dict = field(default_factory=dict)
    score: float = 0.0
    status: str = "unknown"
    last_check: Optional[str] = None
    error: Optional[str] = None

    @property
    def detail(self) -> str:
        passed = sum(1 for v in self.checks.values() if v)
        total = len(self.checks)
        return f"{passed}/{total} checks passed, score={self.score:.0f}%, status={self.status}"


@dataclass
class BridgeState:
    components: dict = field(default_factory=dict)
    overall_health: float = 0.0
    last_sync: Optional[str] = None
    pipeline_history: list = field(default_factory=list)
    version: str = "1.0.0"


def check_component(name: str, config: dict) -> ComponentHealth:
    health = ComponentHealth(name=name)
    path = config["path"]
    if not path.exists():
        health.status = "absent"
        health.error = f"Path {path} does not exist"
        return health
    health.exists = True
    for check_name, check_fn in config["health_endpoints"]:
        try:
            health.checks[check_name] = bool(check_fn(path))
        except Exception as e:
            health.checks[check_name] = False
            log.warning(f"  [{name}] check '{check_name}' failed: {e}")
    passed = sum(1 for v in health.checks.values() if v)
    total = len(health.checks)
    health.score = (passed / total * 100) if total > 0 else 0
    health.score = min(100, health.score * config.get("weight", 1.0))
    if health.score >= 85:
        health.status = "healthy"
    elif health.score >= 60:
        health.status = "degraded"
    elif health.score >= 30:
        health.status = "critical"
    else:
        health.status = "offline"
    health.last_check = datetime.now(timezone.utc).isoformat()
    return health


def compute_overall_health(components: dict) -> float:
    scores = [c.score for c in components.values() if c.exists]
    return sum(scores) / len(scores) if scores else 0.0


def run_health_check() -> BridgeState:
    state = BridgeState()
    log.info("=" * 50)
    log.info("HEALTH CHECK - Ecossistema OpenCode")
    log.info("=" * 50)
    for name, config in COMPONENTS.items():
        health = check_component(name, config)
        state.components[name] = health
        icon = {"healthy": "OK", "degraded": "~", "critical": "!", "offline": "x", "absent": "-"}.get(health.status, "?")
        log.info(f"  [{icon}] {name}: {health.detail}")
        if health.error:
            log.warning(f"       error: {health.error}")
    state.overall_health = compute_overall_health(state.components)
    state.last_sync = datetime.now(timezone.utc).isoformat()
    log.info("-" * 50)
    log.info(f"Overall Health: {state.overall_health:.1f}%")
    healthy = sum(1 for c in state.components.values() if c.status == "healthy")
    degraded = sum(1 for c in state.components.values() if c.status == "degraded")
    offline = sum(1 for c in state.components.values() if c.status in ("offline", "absent"))
    log.info(f"Healthy: {healthy} | Degraded: {degraded} | Offline: {offline}")
    log.info("=" * 50)
    _save_bridge_state(state)
    return state


def _save_bridge_state(state: BridgeState):
    BRIDGE_STATE.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "overall_health": state.overall_health,
        "last_sync": state.last_sync,
        "components": {
            name: {
                "score": c.score,
                "status": c.status,
                "checks": c.checks,
                "exists": c.exists,
                "last_check": c.last_check,
                "error": c.error,
            }
            for name, c in state.components.items()
        },
        "pipeline_history": state.pipeline_history[-50:],
        "version": state.version,
    }
    BRIDGE_STATE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def load_bridge_state() -> BridgeState:
    if not BRIDGE_STATE.exists():
        return BridgeState()
    try:
        data = json.loads(BRIDGE_STATE.read_text(encoding="utf-8"))
        state = BridgeState(
            overall_health=data.get("overall_health", 0),
            last_sync=data.get("last_sync"),
            pipeline_history=data.get("pipeline_history", []),
            version=data.get("version", "1.0.0"),
        )
        for name, cdata in data.get("components", {}).items():
            health = ComponentHealth(
                name=name,
                exists=cdata.get("exists", False),
                checks=cdata.get("checks", {}),
                score=cdata.get("score", 0),
                status=cdata.get("status", "unknown"),
                last_check=cdata.get("last_check"),
                error=cdata.get("error"),
            )
            state.components[name] = health
        return state
    except Exception as e:
        log.warning(f"Failed to load bridge state: {e}")
        return BridgeState()


def route_editais_to_seeker() -> dict:
    log.info("Routing: editais-local -> SEEKER")
    seeker_main = ECO_ROOT / "basis-research" / "main.py"
    if not seeker_main.exists():
        return {"status": "error", "message": "SEEKER main.py not found"}
    log.info(f"  SEEKER available at {seeker_main}")
    return {
        "status": "ready",
        "source": "editais-local",
        "target": "basis-research",
        "pipeline": "editais-to-seeker",
        "command": f"cd {ECO_ROOT / 'basis-research'} && python main.py --research-mode quick",
    }


def route_seeker_to_artigo() -> dict:
    log.info("Routing: SEEKER -> criador-artigo")
    dispatcher = ECO_ROOT / "criador-artigo" / "agents" / "DISPATCHER_ATIVACAO.md"
    if not dispatcher.exists():
        return {"status": "error", "message": "criador-artigo dispatcher not found"}
    agent_count = len(list((ECO_ROOT / "criador-artigo" / "agents").glob("*.md")))
    log.info(f"  criador-artigo available, {agent_count} agents")
    return {
        "status": "ready",
        "source": "basis-research",
        "target": "criador-artigo",
        "pipeline": "seeker-to-artigo",
        "agent_count": agent_count,
    }


def cmd_health():
    state = run_health_check()
    print(json.dumps({
        "overall_health": round(state.overall_health, 1),
        "components": {
            name: {"score": round(c.score, 1), "status": c.status, "checks": c.checks}
            for name, c in state.components.items()
        },
        "last_sync": state.last_sync,
    }, ensure_ascii=False, indent=2))


def cmd_discover():
    log.info("Descobrindo componentes do ecossistema...")
    result = {}
    for name, config in COMPONENTS.items():
        path = config["path"]
        entry = {"path": str(path), "exists": path.exists()}
        if path.exists():
            md_count = len(list(path.rglob("*.md")))
            py_count = len(list(path.rglob("*.py")))
            ts_count = len(list(path.rglob("*.ts")))
            result[name] = {**entry, "files": {"md": md_count, "py": py_count, "ts": ts_count}}
        else:
            result[name] = entry
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_route(pipeline: str):
    log.info(f"Routing pipeline: {pipeline}")
    if pipeline == "from-editais-to-seeker":
        result = route_editais_to_seeker()
    elif pipeline == "from-seeker-to-artigo":
        result = route_seeker_to_artigo()
    elif pipeline == "full":
        result = {"steps": [route_editais_to_seeker(), route_seeker_to_artigo()], "pipeline": "full-editais-to-artigo"}
    else:
        result = {"status": "error", "message": f"Unknown pipeline: {pipeline}"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_watch(interval: int = 60):
    log.info(f"Watching ecosystem (interval={interval}s). Ctrl+C to stop.")
    try:
        while True:
            state = run_health_check()
            degraded = [n for n, c in state.components.items() if c.status in ("degraded", "critical", "offline")]
            if degraded:
                log.warning(f"Components needing attention: {', '.join(degraded)}")
            time.sleep(interval)
    except KeyboardInterrupt:
        log.info("Watch stopped.")


def cmd_pipeline_full(edital_id: Optional[str] = None):
    log.info("=" * 50)
    log.info("PIPELINE COMPLETO: editais-local -> SEEKER -> criador-artigo")
    log.info("=" * 50)
    state = load_bridge_state()
    health = run_health_check()
    if health.overall_health < 50:
        log.error("Overall health too low to run pipeline")
        return {"status": "aborted", "reason": "low_health"}
    step1 = route_editais_to_seeker()
    state.pipeline_history.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pipeline": "editais-to-seeker",
        "result": step1,
    })
    step2 = route_seeker_to_artigo()
    state.pipeline_history.append({
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pipeline": "seeker-to-artigo",
        "result": step2,
    })
    _save_bridge_state(state)
    result = {
        "status": "completed",
        "overall_health": health.overall_health,
        "steps": [step1, step2],
        "edital_id": edital_id,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return result


def cmd_pipeline_seeker_to_artigo(seeker_run_id: Optional[str] = None):
    """Pipeline SEEKER -> criador-artigo via seeker_bridge."""
    log.info("Routing: SEEKER -> criador-artigo (via seeker_bridge)")
    seeker_bridge = ECO_ROOT / "criador-artigo" / "seeker_bridge.py"
    if not seeker_bridge.exists():
        return {"status": "error", "message": "seeker_bridge.py not found"}
    cmd = [sys.executable, str(seeker_bridge), "from-seeker"]
    if seeker_run_id:
        cmd.append(seeker_run_id)
    try:
        import subprocess
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        log.info(f"  seeker_bridge exit code: {result.returncode}")
        return {"status": "completed" if result.returncode == 0 else "error", "output": result.stdout[-500:]}
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def cmd_evolve():
    """Executa ciclo de evolucao."""
    log.info("Executing evolution cycle...")
    evolve_script = ECO_ROOT / "nexus" / "scripts" / "evolution_cycle.py"
    if not evolve_script.exists():
        return {"status": "error", "message": "evolution_cycle.py not found"}
    try:
        import subprocess
        result = subprocess.run([sys.executable, str(evolve_script), "run"], capture_output=True, text=True, timeout=120)
        log.info(f"  evolution_cycle exit code: {result.returncode}")
        return {"status": "completed" if result.returncode == 0 else "error", "output": result.stdout[-500:]}
    except subprocess.TimeoutExpired:
        return {"status": "timeout"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd = sys.argv[1]
    if cmd == "health":
        cmd_health()
    elif cmd == "discover":
        cmd_discover()
    elif cmd == "route":
        if len(sys.argv) < 3:
            print("Usage: ecosystem_bridge.py route <pipeline>")
            return
        cmd_route(sys.argv[2])
    elif cmd == "watch":
        interval = int(sys.argv[2]) if len(sys.argv) > 2 else 60
        cmd_watch(interval)
    elif cmd == "pipeline":
        if len(sys.argv) < 3:
            print("Usage: ecosystem_bridge.py pipeline <subcommand> [args]")
            print("Subcommands: from-editais-to-article, from-seeker-to-artigo")
            return
        sub_cmd = sys.argv[2]
        if sub_cmd == "from-editais-to-article":
            edital_id = sys.argv[3] if len(sys.argv) > 3 else None
            cmd_pipeline_full(edital_id)
        elif sub_cmd == "from-seeker-to-artigo":
            seeker_run_id = sys.argv[3] if len(sys.argv) > 3 else None
            result = cmd_pipeline_seeker_to_artigo(seeker_run_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Unknown pipeline subcommand: {sub_cmd}")
    elif cmd == "evolve":
        result = cmd_evolve()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Unknown command: {cmd}")
        print("Available: health, discover, route, watch, pipeline, evolve")


if __name__ == "__main__":
    main()
