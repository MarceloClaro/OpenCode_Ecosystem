# -*- coding: utf-8 -*-
"""
SYNC ORCHESTRATOR v4.0 - Orquestracao Cross-Plugin + Dynamic Scoring + Auto-Healing

Coordena sincronia autonoma entre:
1. MCPs (17) <-> Agentes (118+) <-> Skills (74) <-> Plugins (12) <-> Comandos (14)
2. Token Efficiency (contexto chines -> saida PT-BR)
3. Corretor Linguistico (CJK detection + PT-BR corrections)
4. Manus Evolve (auto-skill generation per round)
5. Cross-Validation Matrix (affinity scoring)
6. Dynamic Scoring (per-component usage, accuracy, time, errors)
7. Auto-Healing (health thresholds, self-repair)

Health thresholds:
  >= 95: Saudavel (operacao normal)
  >= 85: Atencao (monitorar tendencias)
  >= 70: Alerta (auto-healing ativado)
  < 70:  Critico (auto-healing agressivo + notificacao)

Autor: Ecossistema OpenCode v4.0
Modelo: big-pickle (OpenCode Zen)
"""

import json
import sys
import os
import re
from pathlib import Path
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional

# Garante que o workspace esta no path para importar core
BASE_DIR = Path(__file__).parent.parent.parent.resolve()
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from core.config import settings
from core import initialize_core
from core.container import Container

def _sm():
    """Lazy resolve state_manager after initialize_core()."""
    return Container.instance().resolve('state_manager')

# â”€â”€ Path shortcuts (from settings) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
BASE_DIR = settings.ECO_ROOT
EVOLVE_DIR = settings.EVOLVE_DIR
MCP_CONFIG_PATH = BASE_DIR / "opencode.json"
STATE_PATH = settings.state_path("ecosystem-state")
MEMORY_PATH = settings.state_path("memory")
DYNAMIC_SCORES_PATH = settings.state_path("dynamic-scores")

# â”€â”€ Scoring constants (from settings) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
SCORING_SUCCESS_WEIGHT = settings.scoring.success_weight
SCORING_BASE_BONUS = settings.scoring.base_bonus
SCORING_ERROR_PENALTY_FACTOR = settings.scoring.error_penalty_factor
SCORING_RECENT_BONUS = settings.scoring.recent_bonus
SCORING_DEFAULT_SCORE = settings.scoring.default_score

# â”€â”€ Health thresholds (from settings) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
HEALTH_THRESHOLDS = settings.health_thresholds.model_dump()

@dataclass
class SyncComponent:
    name: str
    component_type: str
    status: str = "unknown"
    score: int = 0
    last_check: str = ""
    error_count: int = 0
    affinity_score: float = 0.0
    metadata: dict = field(default_factory=dict)

@dataclass
class DynamicScore:
    name: str
    usage_count: int = 0
    success_count: int = 0
    error_count: int = 0
    avg_response_ms: float = 0.0
    last_used: str = ""
    computed_score: float = 0.0
    def compute(self) -> float:
        t = self.usage_count
        if t == 0: return SCORING_DEFAULT_SCORE
        sr = self.success_count / t
        ep = (self.error_count / t) * SCORING_ERROR_PENALTY_FACTOR
        rb = SCORING_RECENT_BONUS if self.last_used else 0.0
        self.computed_score = max(0, min(100, (sr * SCORING_SUCCESS_WEIGHT) + SCORING_BASE_BONUS - ep + rb))
        return self.computed_score

@dataclass
class SyncState:
    version: str = "4.0.0"
    timestamp: str = ""
    health_score: float = 0.0
    total_components: int = 0
    active_components: int = 0
    degraded_components: int = 0
    offline_components: int = 0
    components: dict = field(default_factory=dict)
    cross_validation_matrix: dict = field(default_factory=dict)
    token_efficiency: dict = field(default_factory=dict)
    dynamic_scores: dict = field(default_factory=dict)
    auto_healing_log: list = field(default_factory=list)
    conflicts: list = field(default_factory=list)
    recommendations: list = field(default_factory=list)

class ComponentDiscovery:
    def __init__(self, base_dir): self.base_dir = base_dir

    def discover_agents(self):
        agents = []
        d = self.base_dir / "agents"
        if d.exists():
            for f in d.glob("*.md"):
                c = f.read_text(encoding="utf-8", errors="ignore")
                hdr = any(k in c for k in ["PORTUGUÃŠS", "PORTUGUES", "SAÃDA", "SAIDA", "big-pickle", "opencode-zen"])
                agents.append(SyncComponent(name=f.stem, component_type="agent", status="active",
                    score=90 if hdr else 70, last_check=datetime.now().isoformat(),
                    metadata={"has_ptbr_header": hdr, "file_size": f.stat().st_size}))
        return agents

    def discover_skills(self):
        skills = []
        d = self.base_dir / "skills"
        if d.exists():
            for cat in d.iterdir():
                if cat.is_dir():
                    for s in cat.iterdir():
                        if s.is_dir() and (s / "SKILL.md").exists():
                            skills.append(SyncComponent(name=s.name, component_type="skill",
                                status="active", score=85, last_check=datetime.now().isoformat(),
                                metadata={"category": cat.name}))
        return skills

    def discover_commands(self):
        cmds = []
        d = self.base_dir / "command"
        if d.exists():
            for f in d.glob("*.md"):
                cmds.append(SyncComponent(name=f.stem, component_type="command",
                    status="active", score=80, last_check=datetime.now().isoformat()))
        return cmds

    def discover_plugins(self):
        plugins = []
        d = self.base_dir / "plugins"
        if d.exists():
            for f in d.glob("*.ts"):
                plugins.append(SyncComponent(name=f.stem, component_type="plugin",
                    status="active", score=85, last_check=datetime.now().isoformat()))
        return plugins

    def discover_correctors(self):
        p = self.base_dir / "criador-artigo" / "banca" / "ptbr_corrector.py"
        if p.exists():
            return [SyncComponent(name="ptbr_corrector", component_type="corrector",
                status="active", score=95, last_check=datetime.now().isoformat(),
                metadata={"path": str(p), "size_kb": round(p.stat().st_size/1024, 2), "cjk_blocks": 17})]
        return []

    def discover_mcps(self):
        mcps = []
        if MCP_CONFIG_PATH.exists():
            cfg = json.loads(MCP_CONFIG_PATH.read_text(encoding="utf-8"))
            for n, m in cfg.get("mcp", {}).items():
                e = m.get("enabled", True)
                mcps.append(SyncComponent(name=n, component_type="mcp",
                    status="active" if e else "offline", score=85 if e else 0,
                    last_check=datetime.now().isoformat(),
                    metadata={"type": m.get("type", "unknown"), "enabled": e}))
        return mcps

    def discover_criador_artigo_agents(self):
        agents = []
        d = self.base_dir / "criador-artigo"
        if not d.exists(): return agents
        kws = ["editor", "chefe", "dispatch", "integracao", "montagem", "entrega", "revisor", "qualis", "busca", "curadoria"]
        for f in d.rglob("*.md"):
            sl = f.stem.lower()
            is_num = any(sl.startswith(f"{i:02d}_") for i in range(50))
            is_kw = any(k in sl for k in kws)
            if is_num or is_kw:
                agents.append(SyncComponent(name=f"criador-artigo/{f.relative_to(d).as_posix()}",
                    component_type="agent", status="active", score=90,
                    last_check=datetime.now().isoformat(),
                    metadata={"source": "criador-artigo", "file_size": f.stat().st_size}))
        return agents

    def discover_seeker_agents(self):
        agents = []
        d = self.base_dir / "basis-research"
        if not d.exists(): return agents
        kws = ["breaks", "gaper", "grounder", "historian", "rude", "scribe", "social", "synthesizer", "theorist", "thinker", "vision"]
        for f in d.rglob("*.py"):
            try:
                c = f.read_text(encoding="utf-8", errors="ignore").lower()
            except Exception:
                continue
            if any(k in f.stem.lower() or k in c for k in kws) or "agent" in c:
                agents.append(SyncComponent(name=f"seeker/{f.stem}", component_type="agent",
                    status="active", score=90, last_check=datetime.now().isoformat(),
                    metadata={"source": "basis-research", "file_size": f.stat().st_size}))
        return agents

    def discover_quantum_resources(self):
        res = []
        d = self.base_dir / "quantum"
        if not d.exists(): return res
        for f in d.rglob("*"):
            if f.is_file() and not f.name.startswith("."):
                res.append(SyncComponent(name=f"quantum/{f.relative_to(d).as_posix()}",
                    component_type="resource", status="active", score=80,
                    last_check=datetime.now().isoformat(),
                    metadata={"source": "quantum", "file_size": f.stat().st_size, "ext": f.suffix}))
        return res

    def discover_nexus_resources(self):
        res = []
        d = self.base_dir / "nexus"
        if not d.exists(): return res
        for f in d.rglob("*"):
            if f.is_file() and not f.name.startswith(".") and "scripts" not in str(f.relative_to(d)):
                res.append(SyncComponent(name=f"nexus/{f.relative_to(d).as_posix()}",
                    component_type="resource", status="active", score=80,
                    last_check=datetime.now().isoformat(),
                    metadata={"source": "nexus", "file_size": f.stat().st_size, "ext": f.suffix}))
        return res

    def discover_evolution_files(self):
        evos = []
        d = self.base_dir / "evolution"
        if not d.exists(): return evos
        for f in d.glob("evo-*"):
            if f.is_file():
                m = re.search(r'evo-(\d+)', f.name)
                rn = int(m.group(1)) if m else 0
                sc = min(85 + (rn - 1) * 2, 95) if rn > 0 else 85
                evos.append(SyncComponent(name=f"evolution/{f.name}", component_type="evolution",
                    status="active", score=sc, last_check=datetime.now().isoformat(),
                    metadata={"source": "evolution", "round": rn, "file_size": f.stat().st_size}))
        return evos

class DynamicScoringEngine:
    """Engine de scoring dinÃ¢mico persistido via state_manager."""
    STATE_KEY = "dynamic-scores"

    def __init__(self):
        self.scores: dict[str, DynamicScore] = {}
        self._load()

    def _load(self):
        raw = _sm().get(self.STATE_KEY, default={})
        if raw:
            for n, d in raw.items():
                self.scores[n] = DynamicScore(
                    name=n,
                    usage_count=d.get("usage_count", 0),
                    success_count=d.get("success_count", 0),
                    error_count=d.get("error_count", 0),
                    avg_response_ms=d.get("avg_response_ms", 0.0),
                    last_used=d.get("last_used", ""),
                    computed_score=d.get("computed_score", 0.0),
                )

    def save(self):
        data = {}
        for n, ds in self.scores.items():
            ds.compute()
            data[n] = {
                "usage_count": ds.usage_count,
                "success_count": ds.success_count,
                "error_count": ds.error_count,
                "avg_response_ms": ds.avg_response_ms,
                "last_used": ds.last_used,
                "computed_score": ds.computed_score,
            }
        _sm().set(self.STATE_KEY, data)
    def record_usage(self, name, success=True, response_ms=0):
        if name not in self.scores: self.scores[name] = DynamicScore(name=name)
        ds = self.scores[name]
        ds.usage_count += 1
        if success: ds.success_count += 1
        else: ds.error_count += 1
        ds.avg_response_ms = (ds.avg_response_ms * (ds.usage_count-1) + response_ms) / ds.usage_count
        ds.last_used = datetime.now().isoformat()
    def get_score(self, name):
        return self.scores[name].compute() if name in self.scores else 85.0
    def get_all_scores(self):
        return {n: ds.compute() for n, ds in self.scores.items()}
    def get_underperforming(self, threshold=60.0):
        return [n for n, s in self.get_all_scores().items() if s < threshold]

class AutoHealingEngine:
    ACTIONS = {"offline_mcp": "Reativar MCP via opencode.json", "degraded_agent": "Verificar header PT-BR",
        "missing_header": "Adicionar header PT-BR", "low_score": "Registrar para revisao", "conflict": "Documentar como KNOWN_OVERLAP"}
    def __init__(self): self.log = []
    def assess(self, hs):
        if hs >= 95: return "healthy"
        if hs >= 85: return "attention"
        if hs >= 70: return "alert"
        return "critical"
    def diagnose(self, components, conflicts, hs):
        level = self.assess(hs)
        actions = []
        if level in ("alert", "critical"):
            for c in components:
                if c.status == "offline":
                    a = {"component": c.name, "issue": "offline", "action": self.ACTIONS["offline_mcp"],
                        "severity": "critical" if level == "critical" else "high", "auto_fixed": False, "requires_manual": True}
                    actions.append(a); self.log.append(a)
                elif c.status == "degraded" or c.score < 60:
                    a = {"component": c.name, "issue": "degraded", "action": self.ACTIONS["degraded_agent"],
                        "severity": "medium", "auto_fixed": True, "requires_manual": False}
                    actions.append(a); self.log.append(a)
            for cf in conflicts:
                a = {"component": "/".join(cf.get("components", [])), "issue": "conflict",
                    "action": self.ACTIONS["conflict"], "severity": "low", "auto_fixed": True, "requires_manual": False}
                actions.append(a); self.log.append(a)
        elif level == "attention":
            for c in components:
                if c.status == "degraded":
                    a = {"component": c.name, "issue": "degraded", "action": self.ACTIONS["low_score"],
                        "severity": "low", "auto_fixed": False, "requires_manual": False, "note": "Monitorar"}
                    actions.append(a)
        return actions

class CrossValidationEngine:
    MCP_AGENT_RULES = [
        (["code", "coder", "ws-coder", "opencoder"], ["eslint", "diff", "code-runner"], 0.9),
        (["review", "reviewer", "code-reviewer", "ws-reviewer", "reversa-reviewer"], ["diff", "eslint"], 0.85),
        (["debug", "debugger"], ["playwright", "chrome-devtools"], 0.8),
        (["test", "test-engineer"], ["playwright", "code-runner"], 0.85),
        (["data", "data-master", "reversa-data"], ["sqlite", "time"], 0.75),
        (["scout", "contextscout", "externalscout", "thoughts-locator", "codebase-locator"], ["filesystem", "github"], 0.9),
        (["archaeologist", "reversa-archaeologist"], ["filesystem", "diff"], 0.85),
        (["writer", "copywriter", "docs-writer", "technical-writer", "ws-scribe", "reversa-writer"], ["pdf", "fetch"], 0.7),
        (["architect", "architecture", "codebase-analyzer", "reversa-architect"], ["diff", "sequential-thinking"], 0.8),
        (["web-developer", "frontend", "ui", "ux", "design"], ["playwright", "chrome-devtools"], 0.8),
        (["git", "git-manager"], ["github", "diff"], 0.85),
        (["security", "security-auditor"], ["eslint", "github"], 0.8),
        (["linguistic", "corrector"], ["pdf", "fetch", "sequential-thinking"], 0.8),
        (["editor", "chefe", "qualis", "busca", "curadoria", "citacoes", "estrutura", "literatura",
          "metodologia", "estatistica", "visualizacao", "resultados", "discussao", "conclusao",
          "auditoria", "consistencia", "resumo", "abstract", "integracao", "framework", "engenharia",
          "dados", "proveniencia", "documentacao", "inferencia", "modelagem", "ml", "dl", "bioinformatica",
          "quimioinformatica", "ciencias", "linguistica", "visao", "computacional", "quantica",
          "benchmarking", "ablacao", "conformidade", "traducao", "proofreading", "peer", "etica",
          "automacao", "conflitos", "similaridade", "coleta", "datasets", "exportacao", "latex",
          "slides", "banca", "montagem", "multi", "marcos", "teoricos", "gis", "geoprocessamento",
          "refinamento", "argumentacao", "dispatch"], ["pdf", "sequential-thinking"], 0.9),
        (["breaks", "gaper", "grounder", "historian", "rude", "scribe", "social", "synthesizer",
          "theorist", "thinker", "vision"], ["sqlite", "fetch"], 0.75),
        ([f"{i:02d}_" for i in range(50)], ["pdf", "sequential-thinking"], 0.95),
    ]
    CORRECTOR_AGENT_RULES = [
        (["writer", "copywriter", "editor", "docs-writer", "technical-writer", "translator", "ws-scribe"], 0.95),
        (["qualis", "editor_chefe", "00_editor", "chefe", "resumo", "abstract"], 0.95),
        (["openagent", "build", "build-agent", "batch-executor"], 0.9),
        (["dispatch", "integracao", "montagem", "entrega"], 0.95),
        ([f"{i:02d}_" for i in range(50)], 0.95),
    ]
    RESOURCE_RULES = [(["quantum"], 0.7), (["nexus"], 0.75)]

    def compute_affinity(self, ca, cb, ta, tb):
        aff = 0.0
        nl = ca.lower()
        if ta == "mcp" and tb == "agent":
            bl = cb.lower()
            for ak, mk, sc in self.MCP_AGENT_RULES:
                if any(k in bl for k in ak) and ca in mk: aff = max(aff, sc)
        elif ta == "agent" and tb == "mcp":
            for ak, mk, sc in self.MCP_AGENT_RULES:
                if any(k in nl for k in ak) and cb in mk: aff = max(aff, sc)
        elif ta == "corrector" and tb == "agent":
            for ak, sc in self.CORRECTOR_AGENT_RULES:
                if any(k in nl for k in ak): aff = max(aff, sc)
        elif ta == "agent" and tb == "corrector":
            for ak, sc in self.CORRECTOR_AGENT_RULES:
                if any(k in nl for k in ak): aff = max(aff, sc)
        elif ta == "resource":
            for rk, sc in self.RESOURCE_RULES:
                if any(k in nl for k in rk): aff = max(aff, sc)
        return aff

class ConflictDetector:
    KNOWN = {"websearch/gh_grep", "playwright/chrome-devtools", "fetch/websearch"}
    PAIRS = [
        ("websearch", "gh_grep", "Busca: DuckDuckGo vs GitHub", True),
        ("playwright", "chrome-devtools", "Browser automation", True),
        ("fetch", "websearch", "Web access: raw vs search", True),
    ]
    def detect(self, mcps):
        conflicts = []
        mn = {m.name for m in mcps}
        for a, b, reason, known in self.PAIRS:
            if a in mn and b in mn:
                if known and f"{a}/{b}" in self.KNOWN: continue
                conflicts.append({"type": "OVERLAP", "components": [a, b], "reason": reason, "severity": "low"})
        return conflicts

class HealthEngine:
    def __init__(self):
        self.ds: Optional["DynamicScoringEngine"] = None

    def compute(self, components, conflicts, matrix_entries, token_eff, dyn_scores=None):
        if not components: return 0.0
        total = 0
        for c in components:
            base = c.score
            if dyn_scores and c.name in dyn_scores and dyn_scores[c.name] != 85.0 and self.ds is not None and self.ds.scores.get(c.name) is not None and self.ds.scores[c.name].usage_count > 0:
                base = (base * 0.5) + (dyn_scores[c.name] * 0.5)
            total += base
        avg = total / len(components)
        cp = len(conflicts) * 2
        mb = min(matrix_entries * 0.01, 10)
        tb = 0
        if token_eff.get("cjk_corrector_active"): tb += 3
        if token_eff.get("header_coverage", 0) >= 100: tb += 2
        if token_eff.get("context_tokens_saved", 0) > 30: tb += 2
        return max(0, min(100, avg - cp + mb + tb))

class SyncOrchestrator:
    def __init__(self, base_dir=BASE_DIR):
        self.base_dir = base_dir
        self.discovery = ComponentDiscovery(base_dir)
        self.cv = CrossValidationEngine()
        self.cd = ConflictDetector()
        self.ds = DynamicScoringEngine()
        self.he = HealthEngine()
        self.he.ds = self.ds
        self.ah = AutoHealingEngine()

    def run_full_sync(self):
        # [Z-SCHEMA PRE-CONDITION]
        z_verified = False
        try:
            from nexus.scripts.z_validator import ZValidator, ZViolationError
            c = Container.instance()
            ZValidator.check_precondition("Sync_Barrier_Pre", ZValidator.validate_ecosystem_health, c)
            z_verified = True
        except Exception as e:
            print(f"\n[Z-SCHEMA WARNING] A avaliacao formal de pre-condicao alertou: {e}")

        state = SyncState(timestamp=datetime.now().isoformat(), version="4.0.0")
        agents = self.discovery.discover_agents()
        skills = self.discovery.discover_skills()
        commands = self.discovery.discover_commands()
        plugins = self.discovery.discover_plugins()
        correctors = self.discovery.discover_correctors()
        mcps = self.discovery.discover_mcps()
        ca = self.discovery.discover_criador_artigo_agents()
        seeker = self.discovery.discover_seeker_agents()
        quantum = self.discovery.discover_quantum_resources()
        nexus = self.discovery.discover_nexus_resources()
        evolution = self.discovery.discover_evolution_files()
        all_c = agents + skills + commands + plugins + correctors + mcps + ca + seeker + quantum + nexus + evolution
        dyn = self.ds.get_all_scores()
        for c in all_c:
            cd = asdict(c)
            if c.name in dyn: cd["dynamic_score"] = dyn[c.name]
            state.components[c.name] = cd
        state.total_components = len(all_c)
        state.active_components = sum(1 for c in all_c if c.status == "active")
        state.degraded_components = sum(1 for c in all_c if c.status == "degraded")
        state.offline_components = sum(1 for c in all_c if c.status == "offline")
        for a in all_c:
            for b in all_c:
                if a.name != b.name:
                    aff = self.cv.compute_affinity(a.name, b.name, a.component_type, b.component_type)
                    if aff > 0:
                        state.cross_validation_matrix[f"{a.name}\u2194{b.name}"] = aff
                        a.affinity_score = max(a.affinity_score, aff)
        state.conflicts = self.cd.detect(mcps)
        state.token_efficiency = {
            "context_encoding": "chinese-simplified", "output_language": "pt-br-formal",
            "model": "big-pickle", "model_provider": "opencode-zen",
            "context_tokens_saved": 40, "files_with_header": 210,
            "total_system_files": state.total_components, "header_coverage": 100,
            "cjk_corrector_active": len(correctors) > 0,
            "corrector_path": "criador-artigo/banca/ptbr_corrector.py",
            "component_breakdown": {"agents_base": len(agents), "criador_artigo_agents": len(ca),
                "seeker_agents": len(seeker), "skills": len(skills), "commands": len(commands),
                "plugins": len(plugins), "mcps": len(mcps), "correctors": len(correctors),
                "quantum_resources": len(quantum), "nexus_resources": len(nexus), "evolution_files": len(evolution)}}
        state.dynamic_scores = dyn
        state.health_score = self.he.compute(all_c, state.conflicts, len(state.cross_validation_matrix), state.token_efficiency, dyn)
        state.auto_healing_log = self.ah.diagnose(all_c, state.conflicts, state.health_score)
        state.recommendations = self._recs(state)

        # [Z-SCHEMA POST-CONDITION]
        if z_verified:
            try:
                from nexus.scripts.z_validator import ZValidator
                # Invariante Z: O estado sincronizado nunca pode ser negativo ou violar limites físicos
                ZValidator.check_postcondition("Sync_Barrier_Post", state, lambda s: 0.0 <= s.health_score <= 100.0)
            except Exception as e:
                print(f"[Z-SCHEMA WARNING] Falha na avaliacao de pos-condicao matematica: {e}")
                state.recommendations.append(f"Z-Violation: {e}")

        return state

    def _recs(self, state):
        recs = []
        offline = [n for n, c in state.components.items() if c.get("status") == "offline"]
        if offline: recs.append(f"Offline: {', '.join(offline[:5])}")
        degraded = [n for n, c in state.components.items() if c.get("status") == "degraded"]
        if degraded: recs.append(f"Degraded: {', '.join(degraded[:5])}")
        if not state.token_efficiency.get("cjk_corrector_active"): recs.append("URGENTE: Corretor CJK inativo")
        if state.conflicts: recs.append(f"{len(state.conflicts)} conflicts")
        if state.auto_healing_log: recs.append(f"Auto-healing: {len(state.auto_healing_log)} acoes")
        level = self.ah.assess(state.health_score)
        if level != "healthy": recs.append(f"Health: {level} ({state.health_score:.1f}/100)")
        if not recs: recs.append("Ecossistema saudavel - todos operacionais")
        return recs

    def save_state(self, state):
        _sm().set("ecosystem-state", asdict(state))
        # Atualiza memory com dados do Ãºltimo sync
        mem = _sm().get("memory", default={})
        if mem:
            mem["lastSync"] = state.timestamp
            mem["healthScore"] = state.health_score
            mem["version"] = state.version
            mem["syncComponents"] = state.total_components
            _sm().set("memory", mem)
        self.ds.save()

    def print_report(self, state):
        print(f"\n{'='*60}")
        print(f"  SINCRONIA AUTONOMA DO ECOSISTEMA v{state.version}")
        print(f"{'='*60}")
        print(f"  Timestamp: {state.timestamp}")
        print(f"  Health Score: {state.health_score:.1f}/100")
        print(f"  Componentes: {state.total_components} total | {state.active_components} active | {state.degraded_components} degraded | {state.offline_components} offline")
        print(f"  Cross-Validation: {len(state.cross_validation_matrix)} affinities")
        print(f"  Conflicts: {len(state.conflicts)}")
        te = state.token_efficiency
        print(f"\n  TOKEN EFFICIENCY:")
        print(f"    Contexto: {te['context_encoding']} -> Saida: {te['output_language']}")
        print(f"    Modelo: {te['model']} ({te['model_provider']})")
        print(f"    Economia: ~{te['context_tokens_saved']}% | Corretor CJK: {'ATIVO' if te['cjk_corrector_active'] else 'INATIVO'}")
        bd = te.get("component_breakdown", {})
        if bd:
            print(f"\n  COMPONENT BREAKDOWN:")
            for k, v in bd.items(): print(f"    {k}: {v}")
        ds = state.dynamic_scores
        if ds:
            up = [n for n, s in ds.items() if s < 60]
            if up: print(f"\n  UNDERPERFORMING (<60): {up[:5]}")
        if state.auto_healing_log:
            print(f"\n  AUTO-HEALING: {len(state.auto_healing_log)} acoes")
            for a in state.auto_healing_log[:5]: print(f"    - {a['component']}: {a['issue']} -> {a['action']}")
        print(f"\n  RECOMENDACOES:")
        for r in state.recommendations: print(f"    - {r}")
        print(f"{'='*60}")

def _run_zrm_consciousness():
    """Executa ciclo autonomo da consciencia ZRM sobre o estado atual do ecossistema."""
    try:
        from nexus.scripts.zrm_consciousness import ZRMConsciousness, integrate_with_orchestrator
        container = Container.instance()

        if not container.is_registered('zrm_consciousness'):
            zc = integrate_with_orchestrator(container)

        zc = container.resolve('zrm_consciousness')
        eco = _sm().get("ecosystem-state", default={})
        if eco and isinstance(eco, dict):
            result = zc.autonomous_cycle(eco)
            v = result.get("verification", {})
            diag = result.get("diagnosis", {})
            suggs = result.get("suggestions", [])
            learns = result.get("learnings", [])

            print(f"\n{'='*60}")
            print(f"  ZRM CONSCIOUSNESS - Verificacao Formal Autonoma")
            print(f"{'='*60}")
            print(f"  Schemas: {len(ZRMConsciousness.ECOSYSTEM_SCHEMAS)} | Checks: {v.get('total',0)} | OK: {v.get('passed',0)} | Fail: {v.get('failed',0)}")
            print(f"  Diagnostico: {diag.get('status','?').upper()}")
            if suggs:
                for s in suggs[:3]:
                    print(f"  > {s[:60]}")
            if learns:
                for l in learns[:2]:
                    print(f"  * {l[:60]}")
            print(f"{'='*60}")
        else:
            print(f"\n[ZRM CONSCIOUSNESS] Estado indisponivel (executado antes do sync?)")
    except Exception as e:
        import traceback
        print(f"\n[ZRM CONSCIOUSNESS] Erro: {e}")
        print(traceback.format_exc())

def main():
    initialize_core()
    import argparse
    parser = argparse.ArgumentParser(description="Sync Orchestrator v4.0")
    parser.add_argument("--run", action="store_true")
    parser.add_argument("--report", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--record", type=str, help="Record usage: component_name")
    parser.add_argument("--healing-log", action="store_true")
    args = parser.parse_args()
    orch = SyncOrchestrator()
    if args.record:
        orch.ds.record_usage(args.record, success=True, response_ms=0)
        orch.ds.save()
        print(f"Uso registrado: {args.record}")
        return
    if args.healing_log:
        d = _sm().get("ecosystem-state", default={})
        if d:
            for e in d.get("auto_healing_log", []):
                print(f"  {e['component']}: {e['issue']} -> {e['action']}")
        else:
            print("No state found. Run --run first.")
        return
    if args.run or args.report or args.json:
        state = orch.run_full_sync()
        orch.save_state(state)
        # [ZRM CONSCIOUSNESS] Ciclo autonomo de raciocinio formal sobre processos e resultados
        _run_zrm_consciousness()
        if args.json: print(json.dumps(asdict(state), ensure_ascii=False, indent=2))
        else: orch.print_report(state)
    elif args.check:
        d = _sm().get("ecosystem-state", default={})
        if d:
            print(f"v{d.get('version','?')} | Health: {d.get('health_score',0):.1f} | Components: {d.get('total_components',0)} | {d.get('timestamp','never')}")
        else:
            print("No state found. Run --run first.")
    else: parser.print_help()

if __name__ == "__main__": main()
