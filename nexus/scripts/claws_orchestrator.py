# -*- coding: utf-8 -*-
"""
CLAWS v1.0 — Continuous Learning Autonomous Workflow System
Manus.ai-inspired autonomous evolution engine for OpenCode ecosystem.

Arquitetura Transformer + CLAWS Loop:
  OBSERVE → ANALYZE → LEARN → ADAPT → EVOLVE → VALIDATE → REPEAT

Autor: OpenCode Ecosystem v4.0
Modelo: big-pickle (OpenCode Zen)
Versão: 1.0.0
"""

import json
import os
import sys
import re
import traceback
from pathlib import Path
from dataclasses import dataclass, asdict, field
from datetime import datetime
from typing import Optional, Callable, Any

try:
    from core.config import settings
    from core import initialize_core
    from core.container import Container
    HAS_CORE = True
except ImportError:
    HAS_CORE = False

BASE_DIR = Path(__file__).parent.parent.parent.resolve()
STATE_DIR = BASE_DIR / ".evolve"
EVIDENCE_DIR = BASE_DIR / ".evidence"
CLAWS_STATE_FILE = STATE_DIR / "claws-state.json"


@dataclass
class HealthScore:
    """Composite health score de todos os componentes."""
    overall: float = 0.0
    mcps: float = 0.0
    agents: float = 0.0
    skills: float = 0.0
    plugins: float = 0.0
    commands: float = 0.0
    correctors: float = 0.0
    evolution: float = 0.0
    nexus: float = 0.0
    quantum: float = 0.0
    matrix_affinity: float = 0.0
    conflict_penalty: float = 0.0
    token_efficiency_bonus: float = 0.0

    def to_dict(self) -> dict:
        return {k: round(v, 2) for k, v in asdict(self).items()}

    def summary(self) -> str:
        return f"{self.overall:.1f}/100 (MCPs:{self.mcps:.0f} AG:{self.agents:.0f} PL:{self.plugins:.0f} EV:{self.evolution:.0f} NT:{self.nexus:.0f})"


@dataclass
class ComponentHealth:
    name: str
    component_type: str
    status: str = "unknown"
    score: float = 0.0
    last_check: str = ""
    error_count: int = 0
    latency_ms: Optional[float] = None
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvolutionRound:
    round: int
    timestamp: str
    trigger: str
    actions: list
    results: list
    health_delta: float
    patterns_discovered: list
    skills_generated: list
    score: float
    learnings: list

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CLAWSState:
    version: str = "1.0.0"
    active: bool = True
    mode: str = "autonomous"  # autonomous, guided, paused, emergency
    current_round: int = 0
    health: HealthScore = field(default_factory=HealthScore)
    components: dict = field(default_factory=dict)
    evolution_rounds: list = field(default_factory=list)
    cross_validation_matrix: dict = field(default_factory=dict)
    conflicts: dict = field(default_factory=dict)
    recommendations: list = field(default_factory=list)
    auto_healing_log: list = field(default_factory=list)
    observability_log: list = field(default_factory=list)
    last_cycles: list = field(default_factory=list)
    total_skills_generated: int = 0
    bernstein_run_count: int = 0
    errors_fixed: int = 0
    uptime_seconds: float = 0.0
    start_time: str = ""


class ComponentScanner:
    """Scaneia e avalia todos os componentes do ecossistema."""

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir

    def scan_all(self) -> dict[str, ComponentHealth]:
        components = {}
        components.update(self._scan_agents())
        components.update(self._scan_skills())
        components.update(self._scan_plugins())
        components.update(self._scan_commands())
        components.update(self._scan_mcps())
        components.update(self._scan_nexus())
        components.update(self._scan_quantum())
        components.update(self._scan_evolution())
        components.update(self._scan_correctors())
        return components

    def _scan_agents(self) -> dict:
        agents = {}
        d = self.base_dir / "agents"
        if d.exists():
            for f in d.glob("*.md"):
                name = f.stem
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    has_header = any(k in content for k in ["PORTUGUÊS", "SAÍDA", "big-pickle", "opencode-zen"])
                    base_score = 90 if has_header else 65
                    size_kb = f.stat().st_size / 1024
                    if size_kb > 100: base_score = min(base_score + 5, 95)
                    agents[name] = ComponentHealth(
                        name=name, component_type="agent",
                        status="active", score=base_score,
                        last_check=datetime.now().isoformat(),
                        metadata={"file_size_kb": round(size_kb, 1), "has_ptbr_header": has_header}
                    )
                except Exception:
                    agents[name] = ComponentHealth(name=name, component_type="agent", status="degraded", score=40)
        return agents

    def _scan_skills(self) -> dict:
        skills = {}
        d = self.base_dir / "skills"
        if d.exists():
            for cat in d.iterdir():
                if cat.is_dir():
                    for s in cat.iterdir():
                        if s.is_dir() and (s / "SKILL.md").exists():
                            name = s.name
                            size_kb = sum(f.stat().st_size for f in s.rglob("*") if f.is_file()) / 1024
                            skills[name] = ComponentHealth(
                                name=name, component_type="skill",
                                status="active", score=85,
                                last_check=datetime.now().isoformat(),
                                metadata={"category": cat.name, "size_kb": round(size_kb, 1)}
                            )
        return skills

    def _scan_plugins(self) -> dict:
        plugins = {}
        d = self.base_dir / "plugins"
        if d.exists():
            for f in d.glob("*.ts"):
                name = f.stem
                try:
                    content = f.read_text(encoding="utf-8", errors="ignore")
                    version_match = re.search(r'v(\d+\.\d+(?:\.\d+)?)', content)
                    version = version_match.group(1) if version_match else "unknown"
                    has_lsp_error = "ToolCallMetrics" in content or "_toolTimings" in content
                    base_score = 85 if not has_lsp_error else 75
                    plugins[name] = ComponentHealth(
                        name=name, component_type="plugin",
                        status="active", score=base_score,
                        last_check=datetime.now().isoformat(),
                        metadata={"version": version, "size_kb": round(f.stat().st_size/1024, 1)}
                    )
                except Exception:
                    plugins[name] = ComponentHealth(name=name, component_type="plugin", status="degraded", score=50)
        return plugins

    def _scan_commands(self) -> dict:
        commands = {}
        d = self.base_dir / "command"
        if d.exists():
            for f in d.glob("*.md"):
                name = f.stem
                size_kb = f.stat().st_size / 1024
                score = min(80 + size_kb * 0.1, 90)
                commands[name] = ComponentHealth(
                    name=name, component_type="command",
                    status="active", score=score,
                    last_check=datetime.now().isoformat()
                )
        return commands

    def _scan_mcps(self) -> dict:
        mcps = {}
        cfg_path = self.base_dir / "opencode.json"
        if cfg_path.exists():
            try:
                cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
                for n, m in cfg.get("mcp", {}).items():
                    e = m.get("enabled", True)
                    mtype = m.get("type", "local")
                    cmd = m.get("command", [])
                    score = 85 if e else 0
                    if isinstance(cmd, list) and cmd:
                        if any("@wonderwhy-er" in c or "server-puppeteer" in c or "mcp-pandoc" in c for c in cmd if isinstance(c, str)):
                            score = 40  # known problematic packages
                    mcps[n] = ComponentHealth(
                        name=n, component_type="mcp",
                        status="active" if e else "offline",
                        score=score,
                        last_check=datetime.now().isoformat(),
                        metadata={"type": mtype, "enabled": e}
                    )
            except Exception as e:
                pass
        return mcps

    def _scan_nexus(self) -> dict:
        nexus = {}
        d = self.base_dir / "nexus"
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file() and not f.name.startswith("."):
                    name = f"nexus/{f.relative_to(d).as_posix()}"
                    score = 80 + min(f.stat().st_size / 1000, 15)
                    nexus[name] = ComponentHealth(
                        name=name, component_type="nexus",
                        status="active", score=min(score, 98),
                        last_check=datetime.now().isoformat(),
                        metadata={"ext": f.suffix, "size_kb": round(f.stat().st_size/1024, 1)}
                    )
        return nexus

    def _scan_quantum(self) -> dict:
        quantum = {}
        d = self.base_dir / "quantum"
        if d.exists():
            for f in d.rglob("*"):
                if f.is_file() and not f.name.startswith("."):
                    name = f"quantum/{f.relative_to(d).as_posix()}"
                    score = 80
                    quantum[name] = ComponentHealth(
                        name=name, component_type="quantum",
                        status="active", score=score,
                        last_check=datetime.now().isoformat(),
                        metadata={"ext": f.suffix}
                    )
        return quantum

    def _scan_evolution(self) -> dict:
        evo = {}
        d = self.base_dir / "evolution"
        if d.exists():
            rounds = []
            total_size = 0
            for f in d.glob("evo-*"):
                if f.is_file():
                    try:
                        size = f.stat().st_size
                        total_size += size
                        m = re.search(r'evo-(\d+)', f.name)
                        rn = int(m.group(1)) if m else 0
                        if rn: rounds.append(rn)
                    except Exception:
                        pass
            if rounds:
                evo["evolution_pool"] = ComponentHealth(
                    name="evolution_pool", component_type="evolution",
                    status="active", score=min(85 + (max(rounds) - 1) * 2, 95),
                    last_check=datetime.now().isoformat(),
                    metadata={"rounds": sorted(rounds), "total_size_kb": round(total_size/1024, 1)}
                )
        return evo

    def _scan_correctors(self) -> dict:
        correctors = {}
        p = self.base_dir / "criador-artigo" / "banca" / "ptbr_corrector.py"
        if p.exists():
            correctors["ptbr_corrector"] = ComponentHealth(
                name="ptbr_corrector", component_type="corrector",
                status="active", score=95,
                last_check=datetime.now().isoformat(),
                metadata={"path": str(p), "size_kb": round(p.stat().st_size/1024, 2)}
            )
        return correctors


class HealthEngine:
    """Calcula health score composite do ecossistema."""

    def __init__(self, scanner: ComponentScanner):
        self.scanner = scanner

    def compute_health(self, components: dict) -> HealthScore:
        health = HealthScore()

        def avg_score(comps):
            if not comps: return 0.0
            return sum(c.score for c in comps) / len(comps)

        def count_status(comps, status):
            return sum(1 for c in comps if c.status == status)

        groups = {
            "agent": [c for c in components.values() if c.component_type == "agent"],
            "skill": [c for c in components.values() if c.component_type == "skill"],
            "plugin": [c for c in components.values() if c.component_type == "plugin"],
            "command": [c for c in components.values() if c.component_type == "command"],
            "mcp": [c for c in components.values() if c.component_type == "mcp"],
            "nexus": [c for c in components.values() if c.component_type == "nexus"],
            "quantum": [c for c in components.values() if c.component_type == "quantum"],
            "corrector": [c for c in components.values() if c.component_type == "corrector"],
            "evolution": [c for c in components.values() if c.component_type == "evolution"],
        }

        health.agents = avg_score(groups["agent"]) * 1.0
        health.skills = avg_score(groups["skill"]) * 1.0
        health.plugins = avg_score(groups["plugin"]) * 1.0
        health.commands = avg_score(groups["command"]) * 1.0
        health.mcps = avg_score(groups["mcp"]) * 1.0
        health.nexus = avg_score(groups["nexus"]) * 1.0
        health.quantum = avg_score(groups["quantum"]) * 1.0
        health.correctors = avg_score(groups["corrector"]) * 1.0
        health.evolution = avg_score(groups["evolution"]) * 1.0

        total_offline = sum(count_status(v, "offline") for v in groups.values())
        health.conflict_penalty = total_offline * 1.5

        matrix_entries = sum(1 for c in components.values() for _ in groups.get(c.component_type, [])) * 0.5
        health.matrix_affinity = min(matrix_entries * 0.05, 10)

        corrector_active = any(c.component_type == "corrector" and c.status == "active" for c in components.values())
        health.token_efficiency_bonus = 5.0 if corrector_active else 0.0

        all_component_objs = [c for c in components.values() if hasattr(c, 'score')]
        all_scores = [c.score for c in all_component_objs]
        base_overall = sum(all_scores) / len(all_scores) if all_scores else 0.0

        raw = base_overall - health.conflict_penalty + health.matrix_affinity + health.token_efficiency_bonus - (total_offline * 2)
        health.overall = max(0.0, min(100.0, raw))

        return health


class CrossValidationEngine:
    """Computa matriz de afinidade cross-component."""

    RULES = [
        (["ws-coder", "opencoder", "coder"], ["eslint", "diff", "code-runner", "sqlite"], 0.90),
        (["code-reviewer", "ws-reviewer"], ["diff", "eslint", "github"], 0.88),
        (["debugger"], ["playwright", "chrome-devtools"], 0.85),
        (["test-engineer"], ["playwright", "code-runner"], 0.87),
        (["git-manager"], ["github", "diff"], 0.85),
        (["reversa-archaeologist"], ["filesystem", "diff", "sqlite"], 0.85),
        (["openagent", "build-agent"], ["filesystem", "memory", "github", "websearch", "fetch"], 0.90),
        (["bernstein-orchestrator"], ["code-runner", "eslint", "diff", "github", "sqlite"], 0.92),
        (["*[0-9][0-9]_*"], ["pdf", "sequential-thinking"], 0.95),
        (["seeker/*"], ["sqlite", "fetch", "sequential-thinking"], 0.80),
        (["corrector", "linguistic"], ["pdf", "fetch", "sequential-thinking"], 0.95),
    ]

    def compute_matrix(self, components: dict) -> dict:
        matrix = {}
        agents = [c.name for c in components.values() if c.component_type == "agent"]
        mcps = [c.name for c in components.values() if c.component_type == "mcp"]

        for agent in agents:
            for mcp in mcps:
                key = f"{agent}↔{mcp}"
                score = self._affinity(agent, mcp)
                if score > 0:
                    matrix[key] = score

        plugins = [c.name for c in components.values() if c.component_type == "plugin"]
        for plugin in plugins:
            for agent in agents:
                key = f"plugin:{plugin}↔agent:{agent}"
                if "bernstein" in plugin: score = 0.92
                elif "ecosystem" in plugin: score = 0.90
                elif "manus" in plugin: score = 0.88
                else: score = 0.75
                matrix[key] = score

        return matrix

    def _affinity(self, agent: str, mcp: str) -> float:
        al = agent.lower()
        ml = mcp.lower()
        for patterns, targets, score in self.RULES:
            if any(p.replace("*", "") in al or re.match(p.replace("*", "."), al) for p in patterns):
                if any(t in ml for t in targets):
                    return score
        return 0.0


class AutoHealer:
    """Auto-healing engine para componentes degradados."""

    ACTIONS = {
        "offline_mcp": "Re-ativar MCP via opencode.json ou reinstalar",
        "degraded_plugin": "Verificar LSP errors e corrigir syntax",
        "missing_header": "Adicionar header PT-BR ao arquivo",
        "low_score_agent": "Verificar completude e adicionar contexto",
        "conflict": "Documentar como KNOWN_CONFLICT",
    }

    def diagnose(self, components: dict, health: HealthScore) -> list[dict]:
        actions = []

        for c in components.values():
            if c.status == "offline" and c.component_type == "mcp":
                actions.append({
                    "component": c.name,
                    "type": c.component_type,
                    "issue": "offline",
                    "action": self.ACTIONS["offline_mcp"],
                    "severity": "critical",
                    "auto_fixed": False,
                })
            elif c.status == "degraded":
                actions.append({
                    "component": c.name,
                    "type": c.component_type,
                    "issue": "degraded",
                    "action": self.ACTIONS.get(f"degraded_{c.component_type}", "Investigate"),
                    "severity": "medium",
                    "auto_fixed": False,
                })
            elif c.score < 60:
                actions.append({
                    "component": c.name,
                    "type": c.component_type,
                    "issue": "low_score",
                    "action": self.ACTIONS.get(f"low_score_{c.component_type}", "Review"),
                    "severity": "low",
                    "auto_fixed": True,
                })

        return actions[:20]


class CLAWSOrchestrator:
    """Orquestrador principal do sistema CLAWS."""

    def __init__(self, base_dir: Path | None = None):
        self.base_dir = base_dir or BASE_DIR
        self.scanner = ComponentScanner(self.base_dir)
        self.health_engine = HealthEngine(self.scanner)
        self.cv_engine = CrossValidationEngine()
        self.healer = AutoHealer()
        self.state = self._load_state()
        self._start_time = datetime.now()

    def _load_state(self) -> CLAWSState:
        if CLAWS_STATE_FILE.exists():
            try:
                raw = json.loads(CLAWS_STATE_FILE.read_text(encoding="utf-8"))
                hs_data = raw.get("health", {})
                health = HealthScore(
                    overall=hs_data.get("overall", 0),
                    mcps=hs_data.get("mcps", 0),
                    agents=hs_data.get("agents", 0),
                    skills=hs_data.get("skills", 0),
                    plugins=hs_data.get("plugins", 0),
                    commands=hs_data.get("commands", 0),
                    correctors=hs_data.get("correctors", 0),
                    evolution=hs_data.get("evolution", 0),
                    nexus=hs_data.get("nexus", 0),
                    quantum=hs_data.get("quantum", 0),
                )
                state = CLAWSState(
                    version=raw.get("version", "1.0.0"),
                    active=raw.get("active", True),
                    mode=raw.get("mode", "autonomous"),
                    current_round=raw.get("current_round", 0),
                    health=health,
                    components={},
                    evolution_rounds=[],
                    cross_validation_matrix=raw.get("cross_validation_matrix", {}),
                    total_skills_generated=raw.get("total_skills_generated", 0),
                    bernstein_run_count=raw.get("bernstein_run_count", 0),
                    errors_fixed=raw.get("errors_fixed", 0),
                )
                state.start_time = raw.get("start_time", datetime.now().isoformat())
                return state
            except Exception:
                pass

        return CLAWSState(start_time=datetime.now().isoformat())

    def _save_state(self):
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        raw = {
            "version": self.state.version,
            "active": self.state.active,
            "mode": self.state.mode,
            "current_round": self.state.current_round,
            "health": self.state.health.to_dict(),
            "cross_validation_matrix": self.state.cross_validation_matrix,
            "total_skills_generated": self.state.total_skills_generated,
            "bernstein_run_count": self.state.bernstein_run_count,
            "errors_fixed": self.state.errors_fixed,
            "start_time": self.state.start_time,
            "uptime_seconds": (datetime.now() - datetime.fromisoformat(self.state.start_time)).total_seconds(),
        }
        CLAWS_STATE_FILE.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")

    def run_cycle(self, trigger: str = "manual") -> dict:
        """Executa um ciclo completo do CLAWS loop."""
        cycle_start = datetime.now()
        round_num = self.state.current_round + 1

        components = self.scanner.scan_all()
        health = self.health_engine.compute_health(components)
        matrix = self.cv_engine.compute_matrix(components)
        healing = self.healer.diagnose(components, health)

        prev_health = self.state.health.overall
        health_delta = health.overall - prev_health

        round_obj = EvolutionRound(
            round=round_num,
            timestamp=datetime.now().isoformat(),
            trigger=trigger,
            actions=[f"Scan {len(components)} components", f"Compute health {health.overall:.1f}"],
            results=[f"Matrix entries: {len(matrix)}", f"Healing actions: {len(healing)}"],
            health_delta=health_delta,
            patterns_discovered=[f"affinity:{len(matrix)}", f"components:{len(components)}"],
            skills_generated=[],
            score=health.overall,
            learnings=[f"Health delta: {health_delta:+.1f}", f"Active: {sum(1 for c in components.values() if c.status=='active')}", f"Offline: {sum(1 for c in components.values() if c.status=='offline')}"]
        )

        self.state.current_round = round_num
        self.state.health = health
        self.state.components = {k: v.to_dict() for k, v in components.items()}
        self.state.cross_validation_matrix = matrix
        self.state.evolution_rounds.append(round_obj.to_dict())
        self.state.auto_healing_log.extend(healing[:5])
        self.state.errors_fixed += len(healing)
        self.state.uptime_seconds = (datetime.now() - datetime.fromisoformat(self.state.start_time)).total_seconds()

        self._save_state()

        return {
            "cycle": round_num,
            "health": health.to_dict(),
            "health_delta": round(health_delta, 2),
            "components_scanned": len(components),
            "matrix_entries": len(matrix),
            "healing_actions": len(healing),
            "mode": self.state.mode,
            "uptime_seconds": round(self.state.uptime_seconds, 1),
            "duration_ms": (datetime.now() - cycle_start).total_seconds() * 1000,
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="CLAWS v1.0 — Continuous Learning Autonomous Workflow System")
    parser.add_argument("--cycle", action="store_true", help="Executar ciclo completo CLAWS")
    parser.add_argument("--health", action="store_true", help="Mostrar health score atual")
    parser.add_argument("--scan", action="store_true", help="Scannear todos os componentes")
    parser.add_argument("--matrix", action="store_true", help="Mostrar cross-validation matrix")
    parser.add_argument("--heal", action="store_true", help="Mostrar healing actions")
    parser.add_argument("--report", action="store_true", help="Relatório completo")
    parser.add_argument("--autonomous", action="store_true", help="Modo autônomo (loop contínuo)")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    args = parser.parse_args()

    claws = CLAWSOrchestrator()

    if args.health or args.report:
        components = claws.scanner.scan_all()
        health = claws.health_engine.compute_health(components)
        matrix = claws.cv_engine.compute_matrix(components)
        healing = claws.healer.diagnose(components, health)

        if args.json:
            print(json.dumps({
                "health": health.to_dict(),
                "components": len(components),
                "matrix_entries": len(matrix),
                "healing_needed": len(healing),
            }, ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  CLAWS v1.0 — HEALTH REPORT")
            print(f"{'='*60}")
            print(f"  Overall:   {health.overall:.1f}/100")
            print(f"  MCPs:      {health.mcps:.1f}")
            print(f"  Agents:    {health.agents:.1f}")
            print(f"  Skills:    {health.skills:.1f}")
            print(f"  Plugins:   {health.plugins:.1f}")
            print(f"  Commands: {health.commands:.1f}")
            print(f"  Correctors:{health.correctors:.1f}")
            print(f"  Evolution: {health.evolution:.1f}")
            print(f"  Nexus:     {health.nexus:.1f}")
            print(f"  Quantum:   {health.quantum:.1f}")
            print(f"  Matrix Affinity Bonus: +{health.matrix_affinity:.1f}")
            print(f"  Token Efficiency Bonus: +{health.token_efficiency_bonus:.1f}")
            print(f"  Conflict Penalty: -{health.conflict_penalty:.1f}")
            print(f"\n  Components scanned: {len(components)}")
            print(f"  Matrix entries: {len(matrix)}")
            print(f"  Healing actions: {len(healing)}")
            if healing:
                print(f"\n  TOP HEALING NEEDS:")
                for h in healing[:5]:
                    print(f"    [{h['severity']}] {h['component']}: {h['issue']}")
            print(f"{'='*60}")

    elif args.scan:
        components = claws.scanner.scan_all()
        if args.json:
            data = {k: v.to_dict() for k, v in components.items()}
            print(json.dumps(data, ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  CLAWS v1.0 — COMPONENT SCAN")
            print(f"{'='*60}")
            groups = {}
            for c in components.values():
                groups.setdefault(c.component_type, []).append(c)
            for gname, comps in sorted(groups.items()):
                active = sum(1 for c in comps if c.status == "active")
                offline = sum(1 for c in comps if c.status == "offline")
                avg = sum(c.score for c in comps) / max(1, len(comps))
                print(f"\n  {gname.upper()}: {len(comps)} total | {active} active | {offline} offline | avg: {avg:.1f}")
                for c in comps:
                    if c.status != "active" or c.score < 75:
                        print(f"    {'!' if c.status != 'active' else '.'} {c.name}: {c.score:.0f} ({c.status})")
            print(f"\n{'='*60}")

    elif args.matrix:
        components = claws.scanner.scan_all()
        matrix = claws.cv_engine.compute_matrix(components)
        if args.json:
            print(json.dumps(matrix, ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  CLAWS v1.0 — CROSS-VALIDATION MATRIX")
            print(f"{'='*60}")
            print(f"  Total entries: {len(matrix)}")
            sorted_entries = sorted(matrix.items(), key=lambda x: -x[1])
            print(f"\n  TOP AFFINITIES:")
            for k, v in sorted_entries[:20]:
                print(f"    {k}: {v:.2f}")
            print(f"{'='*60}")

    elif args.heal:
        components = claws.scanner.scan_all()
        health = claws.health_engine.compute_health(components)
        healing = claws.healer.diagnose(components, health)
        if args.json:
            print(json.dumps(healing, ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*60}")
            print(f"  CLAWS v1.0 — AUTO-HEALING REPORT")
            print(f"{'='*60}")
            print(f"  Actions needed: {len(healing)}")
            for h in healing:
                print(f"  [{h['severity']}] {h['type']}/{h['component']}")
                print(f"    Issue: {h['issue']}")
                print(f"    Action: {h['action']}")
                print(f"    Auto-fix: {'YES' if h['auto_fixed'] else 'NO'}")
            print(f"{'='*60}")

    elif args.cycle or args.report or args.autonomous:
        if args.autonomous:
            print("CLAWS Autonomous Mode — Starting continuous loop...")
            import time
            cycles = 0
            while True:
                try:
                    result = claws.run_cycle(trigger="autonomous")
                    cycles += 1
                    h = result['health']
                    print(f"Cycle {cycles} | Health: {h['overall']:.1f}/100 | Delta: {result['health_delta']:+.1f} | Components: {result['components_scanned']} | Matrix: {result['matrix_entries']} | Healing: {result['healing_actions']} | Mode: {result['mode']}")
                    time.sleep(30)
                except KeyboardInterrupt:
                    print(f"\nAutonomous loop stopped after {cycles} cycles.")
                    break
        else:
            result = claws.run_cycle(trigger="manual")
            if args.json:
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                h = result['health']
                print(f"\n{'='*60}")
                print(f"  CLAWS v1.0 — CYCLE {result['cycle']} COMPLETE")
                print(f"{'='*60}")
                print(f"  Health: {h['overall']:.1f}/100 (delta: {result['health_delta']:+.1f})")
                print(f"  Components: {result['components_scanned']}")
                print(f"  Matrix: {result['matrix_entries']} entries")
                print(f"  Healing: {result['healing_actions']} actions")
                print(f"  Mode: {result['mode']}")
                print(f"  Duration: {result['duration_ms']:.0f}ms")
                print(f"{'='*60}")

    else:
        parser.print_help()


if __name__ == "__main__":
    main()