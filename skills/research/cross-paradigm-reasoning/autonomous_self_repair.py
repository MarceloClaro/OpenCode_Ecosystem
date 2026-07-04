#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Autonomous Self-Repair System v1.0 — R39 / SPEC-083
====================================================
Monitora continuamente a saude dos motores de raciocinio do ecossistema,
detecta falhas em tempo real, recarrega modulos corrompidos e notifica
o orquestrador central.

Componentes:
  - HealthMonitor: heartbeat + engine/research skill checks
  - RepairEngine: reload, dependency resolution, fallback routing
  - RepairLogger: audit trail SHA-256
  - RepairNotifier: integracao com TrustEngine + ecosystem-state

SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL
"""

from __future__ import annotations

import hashlib
import importlib
import importlib.util
import json
import subprocess
import sys
import time
import traceback
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ────────────────────────────────────────────────────────────
# Tipos
# ────────────────────────────────────────────────────────────

@dataclass
class HealthCheck:
    """Resultado de uma verificacao de saude de um motor/skill."""
    engine: str
    available: bool
    response_time_ms: float = 0.0
    last_error: str = ""
    last_heartbeat: str = ""
    version: str = ""


@dataclass
class RepairRecord:
    """Registro de uma acao de reparo executada."""
    timestamp: str
    engine: str
    diagnosis: str
    action: str
    result: str  # success | failure | partial | deferred
    duration_ms: float = 0.0
    detail: str = ""


@dataclass
class AuditEntry:
    """Entrada unica no audit trail com hash SHA-256."""
    entry_id: str
    timestamp: str
    event_type: str  # health_check | repair | fallback | notification
    data: Dict[str, Any]
    hash: str = ""


# ────────────────────────────────────────────────────────────
# Engines e modulos a monitorar
# ────────────────────────────────────────────────────────────

ENGINES = {
    "z3": {
        "path": "skills/reasoning/formal-verification/scripts/z3_engine.py",
        "class_name": "Z3Engine",
        "deps": ["z3"],
        "fallback": "sympy",
    },
    "sympy": {
        "path": "skills/reasoning/symbolic-math/scripts/sympy_engine.py",
        "class_name": "SymPyEngine",
        "deps": ["sympy"],
        "fallback": "z3",
    },
    "kanren": {
        "path": "skills/reasoning/logic-programming/scripts/kanren_engine.py",
        "class_name": "KanrenEngine",
        "deps": [],
        "fallback": "critical",
    },
    "critical": {
        "path": "skills/reasoning/critical-reasoning/scripts/critical_engine.py",
        "class_name": "CriticalEngine",
        "deps": [],
        "fallback": "kanren",
    },
}

RESEARCH_SKILLS = {
    "game_theory": {
        "path": "skills/research/game-theory/game_theory.py",
        "classes": ["NashEquilibrium", "PayoffMatrix"],
    },
    "temporal_population": {
        "path": "skills/research/temporal-population/temporal_population.py",
        "classes": [
            "TimeSeriesAnalyzer", "LongitudinalAnalyzer",
            "PopulationGeneralizer", "SampleSizeCalculator",
        ],
    },
    "theoretical_empirical": {
        "path": "skills/research/theoretical-empirical/theoretical_empirical.py",
        "classes": [
            "EpistemologicalClassifier", "EffectSizeCalculator",
            "ReliabilityAnalyzer", "TheoreticalFrameworkBuilder",
        ],
    },
    "logical_multiscale": {
        "path": "skills/research/logical-multiscale/logical_multiscale.py",
        "classes": [
            "InferenceEngine", "MultiScaleAnalyzer",
            "ArgumentationValidator",
        ],
    },
}


# ────────────────────────────────────────────────────────────
# SHA-256 helper
# ────────────────────────────────────────────────────────────

def _sha256(data: Dict) -> str:
    """Gera hash SHA-256 de um dicionario."""
    raw = json.dumps(data, sort_keys=True, default=str).encode()
    return hashlib.sha256(raw).hexdigest()


# ────────────────────────────────────────────────────────────
# HealthMonitor
# ────────────────────────────────────────────────────────────

class HealthMonitor:
    """Monitora a saude dos motores de raciocinio e research skills."""

    def __init__(self) -> None:
        self._base = Path(__file__).resolve().parent.parent.parent.parent
        self._results: Dict[str, HealthCheck] = {}

    def check_engine(self, name: str) -> HealthCheck:
        """Verifica disponibilidade de um motor de raciocinio."""
        info = ENGINES.get(name)
        if not info:
            hc = HealthCheck(
                engine=name, available=False,
                last_error=f"Unknown engine: {name}",
                last_heartbeat=datetime.now(timezone.utc).isoformat(),
            )
            self._results[name] = hc
            return hc

        t0 = time.time()
        try:
            mod_path = self._base / info["path"]
            if not mod_path.exists():
                raise FileNotFoundError(f"Module not found: {mod_path}")

            sys.path.insert(0, str(mod_path.parent))
            spec = importlib.util.spec_from_file_location(name, str(mod_path))
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec for {mod_path}")

            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            cls = getattr(mod, info["class_name"], None)
            if cls is None:
                raise ImportError(f"Class {info['class_name']} not found in {mod_path}")

            inst = cls()
            avail = bool(getattr(inst, "available", True))
            ms = (time.time() - t0) * 1000
            hc = HealthCheck(
                engine=name, available=avail,
                response_time_ms=round(ms, 2),
                last_heartbeat=datetime.now(timezone.utc).isoformat(),
                version=getattr(inst, "version", "1.0"),
            )
            self._results[name] = hc
            return hc
        except Exception as e:
            ms = (time.time() - t0) * 1000
            hc = HealthCheck(
                engine=name, available=False,
                response_time_ms=round(ms, 2),
                last_error=str(e),
                last_heartbeat=datetime.now(timezone.utc).isoformat(),
            )
            self._results[name] = hc
            return hc
        finally:
            sys.path.pop(0)
            sys.modules.pop(name, None)

    def check_all_engines(self) -> Dict[str, HealthCheck]:
        """Verifica todos os 4 motores de raciocinio."""
        for name in ENGINES:
            self.check_engine(name)
        return dict(self._results)

    def check_research_skill(self, name: str) -> HealthCheck:
        """Verifica disponibilidade de uma research skill."""
        info = RESEARCH_SKILLS.get(name)
        if not info:
            hc = HealthCheck(
                engine=name, available=False,
                last_error=f"Unknown research skill: {name}",
                last_heartbeat=datetime.now(timezone.utc).isoformat(),
            )
            self._results[name] = hc
            return hc

        t0 = time.time()
        try:
            mod_path = self._base / info["path"]
            if not mod_path.exists():
                raise FileNotFoundError(f"Module not found: {mod_path}")

            sys.path.insert(0, str(mod_path.parent))
            spec = importlib.util.spec_from_file_location(name, str(mod_path))
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load spec for {mod_path}")

            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)

            missing = [c for c in info["classes"] if not hasattr(mod, c)]
            ms = (time.time() - t0) * 1000
            avail = len(missing) == 0
            hc = HealthCheck(
                engine=name, available=avail,
                response_time_ms=round(ms, 2),
                last_error=f"Missing classes: {missing}" if missing else "",
                last_heartbeat=datetime.now(timezone.utc).isoformat(),
            )
            self._results[name] = hc
            return hc
        except Exception as e:
            ms = (time.time() - t0) * 1000
            hc = HealthCheck(
                engine=name, available=False,
                response_time_ms=round(ms, 2),
                last_error=str(e),
                last_heartbeat=datetime.now(timezone.utc).isoformat(),
            )
            self._results[name] = hc
            return hc
        finally:
            sys.path.pop(0)
            sys.modules.pop(name, None)

    def check_all_research_skills(self) -> Dict[str, HealthCheck]:
        """Verifica todas as 4 research skills."""
        for name in RESEARCH_SKILLS:
            self.check_research_skill(name)
        return dict(self._results)

    def heartbeat(self) -> Dict[str, Any]:
        """Heartbeat completo de todos os modulos monitorados."""
        all_checks: Dict[str, HealthCheck] = {}
        all_checks.update(self.check_all_engines())
        all_checks.update(self.check_all_research_skills())

        available = sum(1 for c in all_checks.values() if c.available)
        total = len(all_checks)
        avg_ms = sum(c.response_time_ms for c in all_checks.values()) / max(total, 1)

        return {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_checks": total,
            "available": available,
            "unhealthy": total - available,
            "health_pct": round((available / max(total, 1)) * 100, 1),
            "avg_response_time_ms": round(avg_ms, 2),
            "checks": {k: asdict(v) for k, v in all_checks.items()},
        }


# ────────────────────────────────────────────────────────────
# RepairEngine
# ────────────────────────────────────────────────────────────

class RepairEngine:
    """Executa reparos em modulos com falha."""

    def __init__(self, health_monitor: HealthMonitor) -> None:
        self.hm = health_monitor
        self._base = Path(__file__).resolve().parent.parent.parent.parent

    def reload_module(self, engine_name: str) -> RepairRecord:
        """Recarrega um modulo com falha usando importlib."""
        t0 = time.time()
        ts = datetime.now(timezone.utc).isoformat()

        try:
            # Limpa cache de importacao
            for key in list(sys.modules.keys()):
                if engine_name in key:
                    del sys.modules[key]
            importlib.invalidate_caches()

            info = ENGINES.get(engine_name) or RESEARCH_SKILLS.get(engine_name)
            if info is None:
                ms = (time.time() - t0) * 1000
                return RepairRecord(ts, engine_name, "unknown_engine",
                                    "reload", "failed",
                                    duration_ms=round(ms, 2),
                                    detail=f"Unknown engine: {engine_name}")

            mod_path = self._base / info["path"]
            if not mod_path.exists():
                ms = (time.time() - t0) * 1000
                return RepairRecord(ts, engine_name, "file_not_found",
                                    "reload", "failed",
                                    duration_ms=round(ms, 2),
                                    detail=f"Path not found: {mod_path}")

            sys.path.insert(0, str(mod_path.parent))
            spec = importlib.util.spec_from_file_location(engine_name, str(mod_path))
            if spec and spec.loader:
                spec.loader.exec_module(importlib.util.module_from_spec(spec))
                ms = (time.time() - t0) * 1000
                return RepairRecord(ts, engine_name, "module_reload",
                                    "reload", "success",
                                    duration_ms=round(ms, 2),
                                    detail=f"Reloaded {engine_name}")
            raise ImportError(f"Could not reload {engine_name}")
        except Exception as e:
            ms = (time.time() - t0) * 1000
            return RepairRecord(ts, engine_name, "module_reload_failed",
                           "reload", "failed",
                           duration_ms=round(ms, 2),
                           detail=str(e))
        finally:
            sys.path.pop(0)

    def check_dependencies(self, engine_name: str) -> RepairRecord:
        """Verifica e tenta instalar dependencias faltantes."""
        t0 = time.time()
        ts = datetime.now(timezone.utc).isoformat()
        deps = ENGINES.get(engine_name, {}).get("deps", [])

        if not deps:
            ms = (time.time() - t0) * 1000
            return RepairRecord(ts, engine_name, "no_deps",
                                "dependency_check", "success",
                                duration_ms=round(ms, 2),
                                detail="No dependencies to check")

        missing = []
        for dep in deps:
            try:
                __import__(dep.replace("-", "_"))
            except ImportError:
                missing.append(dep)

        if not missing:
            ms = (time.time() - t0) * 1000
            return RepairRecord(ts, engine_name, "deps_ok",
                                "dependency_check", "success",
                                duration_ms=round(ms, 2),
                                detail="All dependencies satisfied")

        installed = []
        failed = []
        for dep in missing:
            try:
                result = subprocess.run(
                    [sys.executable, "-m", "pip", "install", dep, "-q"],
                    capture_output=True, timeout=60, check=True,
                )
                installed.append(dep)
            except Exception:
                failed.append(dep)

        ms = (time.time() - t0) * 1000
        status = "success" if not failed else "partial"
        return RepairRecord(ts, engine_name,
                           f"installed={installed},failed={failed}",
                           "dependency_resolve", status,
                           duration_ms=round(ms, 2),
                           detail=f"Installed: {installed}, Failed: {failed}")

    def fallback(self, engine_name: str) -> RepairRecord:
        """Redireciona para engine alternativo quando primario falha."""
        t0 = time.time()
        ts = datetime.now(timezone.utc).isoformat()
        fallback_engine = ENGINES.get(engine_name, {}).get("fallback")

        if not fallback_engine:
            ms = (time.time() - t0) * 1000
            return RepairRecord(ts, engine_name, "no_fallback",
                                "fallback", "failed",
                                duration_ms=round(ms, 2),
                                detail=f"No fallback defined for {engine_name}")

        fb_check = self.hm.check_engine(fallback_engine)
        ms = (time.time() - t0) * 1000

        if fb_check.available:
            return RepairRecord(ts, engine_name,
                               f"routed_to_{fallback_engine}",
                               "fallback", "success",
                               duration_ms=round(ms, 2),
                               detail=f"Fell back to {fallback_engine} (available)")
        else:
            return RepairRecord(ts, engine_name,
                               f"fallback_{fallback_engine}_unavailable",
                               "fallback", "failed",
                               duration_ms=round(ms, 2),
                               detail=f"Fallback {fallback_engine} also unavailable")


# ────────────────────────────────────────────────────────────
# RepairLogger
# ────────────────────────────────────────────────────────────

class RepairLogger:
    """Audit trail de reparos com verificacao de integridade SHA-256."""

    def __init__(self) -> None:
        self._entries: List[AuditEntry] = []
        self._entry_counter: int = 0

    def log(self, event_type: str, data: Dict[str, Any]) -> AuditEntry:
        """Registra um evento no audit trail."""
        self._entry_counter += 1
        ts = datetime.now(timezone.utc).isoformat()
        prev_hash = self._entries[-1].hash if self._entries else "0" * 64

        entry_data = {
            "prev_hash": prev_hash,
            "event_type": event_type,
            "data": data,
        }
        entry = AuditEntry(
            entry_id=f"SR-{self._entry_counter:04d}",
            timestamp=ts,
            event_type=event_type,
            data=data,
            hash=_sha256(entry_data),
        )
        self._entries.append(entry)
        return entry

    def get_log(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retorna entradas recentes do log."""
        return [
            {
                "entry_id": e.entry_id,
                "timestamp": e.timestamp,
                "event_type": e.event_type,
                "data": e.data,
                "hash": e.hash,
            }
            for e in self._entries[-limit:]
        ]

    def verify_chain(self) -> bool:
        """Verifica integridade da cadeia de auditoria (SHA-256 chain)."""
        for i, entry in enumerate(self._entries):
            prev_hash = self._entries[i - 1].hash if i > 0 else "0" * 64
            expected = _sha256({
                "prev_hash": prev_hash,
                "event_type": entry.event_type,
                "data": entry.data,
            })
            if entry.hash != expected:
                return False
        return True

    def export_json(self, path: str) -> str:
        """Exporta audit trail completo para arquivo JSON."""
        data = {
            "entries": self.get_log(limit=10000),
            "chain_valid": self.verify_chain(),
            "total_entries": len(self._entries),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return path


# ────────────────────────────────────────────────────────────
# RepairNotifier
# ────────────────────────────────────────────────────────────

class RepairNotifier:
    """Notifica o ecossistema sobre reparos realizados."""

    def __init__(self, logger: RepairLogger) -> None:
        self.logger = logger

    def notify_repair(self, record: RepairRecord) -> AuditEntry:
        """Notifica o ecossistema sobre um reparo."""
        return self.logger.log("repair", asdict(record))

    def notify_health(self, heartbeat: Dict[str, Any]) -> AuditEntry:
        """Notifica estado de saude."""
        return self.logger.log("health_check", {
            "timestamp": heartbeat["timestamp"],
            "available": heartbeat["available"],
            "unhealthy": heartbeat["unhealthy"],
            "health_pct": heartbeat["health_pct"],
        })

    def notify_state_update(self, ecosystem_state_path: str,
                           status: Dict[str, Any]) -> AuditEntry:
        """Atualiza ecosystem-state.json com status de saude."""
        try:
            with open(ecosystem_state_path, "r", encoding="utf-8") as f:
                state = json.load(f)
            state.setdefault("self_repair", {})
            state["self_repair"]["last_heartbeat"] = status.get("timestamp", "")
            state["self_repair"]["health_pct"] = status.get("health_pct", 0)
            state["self_repair"]["unhealthy_engines"] = status.get("unhealthy", 0)
            state["self_repair"]["last_update"] = datetime.now(timezone.utc).isoformat()
            with open(ecosystem_state_path, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

        return self.logger.log("notification", {
            "target": "ecosystem-state.json",
            "status": status,
        })


# ────────────────────────────────────────────────────────────
# SelfRepairOrchestrator (pipeline completo)
# ────────────────────────────────────────────────────────────

class SelfRepairOrchestrator:
    """Orquestrador do pipeline completo de auto-reparo."""

    def __init__(self) -> None:
        self.hm = HealthMonitor()
        self.re = RepairEngine(self.hm)
        self.logger = RepairLogger()
        self.notifier = RepairNotifier(self.logger)

    def run_pipeline(self,
                     ecosystem_state_path: Optional[str] = None) -> Dict[str, Any]:
        """Executa pipeline completo: monitor -> detect -> repair -> log -> notify."""
        t0 = time.time()

        # 1. Health check inicial
        heartbeat = self.hm.heartbeat()
        self.notifier.notify_health(heartbeat)

        repairs: List[Dict[str, Any]] = []

        # 2. Detecta e repara motores com falha
        for name, check in heartbeat["checks"].items():
            if not check["available"]:
                r1 = self.re.reload_module(name)
                repairs.append(asdict(r1))
                self.notifier.notify_repair(r1)

                if r1.result == "failed":
                    r2 = self.re.check_dependencies(name)
                    repairs.append(asdict(r2))
                    self.notifier.notify_repair(r2)

                    if r2.result in ("failed", "partial"):
                        r3 = self.re.fallback(name)
                        repairs.append(asdict(r3))
                        self.notifier.notify_repair(r3)

        # 3. Health check final
        final_hb = self.hm.heartbeat()
        self.notifier.notify_health(final_hb)

        # 4. Atualiza ecosystem-state
        if ecosystem_state_path:
            self.notifier.notify_state_update(ecosystem_state_path, final_hb)

        total_ms = (time.time() - t0) * 1000
        return {
            "pipeline_time_ms": round(total_ms, 2),
            "initial_health": {
                "available": heartbeat["available"],
                "unhealthy": heartbeat["unhealthy"],
                "total": heartbeat["total_checks"],
            },
            "final_health": {
                "available": final_hb["available"],
                "unhealthy": final_hb["unhealthy"],
                "total": final_hb["total_checks"],
            },
            "repairs_attempted": len(repairs),
            "repairs": repairs,
            "log_entries": len(self.logger._entries),
            "chain_valid": self.logger.verify_chain(),
        }


# ────────────────────────────────────────────────────────────
# API Publica
# ────────────────────────────────────────────────────────────

__all__ = [
    "HealthMonitor",
    "RepairEngine",
    "RepairLogger",
    "RepairNotifier",
    "SelfRepairOrchestrator",
    "HealthCheck",
    "RepairRecord",
    "AuditEntry",
]