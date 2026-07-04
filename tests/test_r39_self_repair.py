#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes TDD — R39: Autonomous Self-Repair System (SPEC-083)
===========================================================
14 CTs validando HealthMonitor, RepairEngine, RepairLogger,
RepairNotifier e SelfRepairOrchestrator.

SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL
"""

import json
import os
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

# Ajusta path para import do modulo
_SELF_REPAIR_PATH = Path(__file__).resolve().parent.parent / \
    "skills/research/cross-paradigm-reasoning"
sys.path.insert(0, str(_SELF_REPAIR_PATH))

from autonomous_self_repair import (
    HealthMonitor,
    RepairEngine,
    RepairLogger,
    RepairNotifier,
    SelfRepairOrchestrator,
    HealthCheck,
    RepairRecord,
    AuditEntry,
    ENGINES,
    RESEARCH_SKILLS,
)


# ────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────

def _fake_heartbeat(available: int = 8, total: int = 8) -> dict:
    """Gera heartbeat fake para testes de notificacao."""
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "total_checks": total,
        "available": available,
        "unhealthy": total - available,
        "health_pct": round((available / max(total, 1)) * 100, 1),
        "avg_response_time_ms": 12.34,
        "checks": {},
    }


# ────────────────────────────────────────────────────────────
# CT-01: HealthMonitor inicializa
# ────────────────────────────────────────────────────────────

def test_health_monitor_init():
    """CT-01: HealthMonitor deve inicializar sem erros."""
    hm = HealthMonitor()
    assert hm is not None
    assert hasattr(hm, "heartbeat")
    assert hasattr(hm, "check_engine")
    assert hasattr(hm, "check_research_skill")


# ────────────────────────────────────────────────────────────
# CT-02: HealthMonitor verifica engine valido
# ────────────────────────────────────────────────────────────

def test_health_monitor_check_engine_valid():
    """CT-02: check_engine() deve retornar HealthCheck para engine valido."""
    hm = HealthMonitor()
    hc = hm.check_engine("z3")
    assert isinstance(hc, HealthCheck)
    assert hc.engine == "z3"
    assert isinstance(hc.available, bool)
    assert isinstance(hc.response_time_ms, (int, float)) and hc.response_time_ms >= 0
    assert isinstance(hc.last_heartbeat, str) and len(hc.last_heartbeat) > 0


# ────────────────────────────────────────────────────────────
# CT-03: HealthMonitor verifica engine desconhecido
# ────────────────────────────────────────────────────────────

def test_health_monitor_check_engine_unknown():
    """CT-03: HealthMonitor deve marcar como unavailable para engine desconhecido."""
    hm = HealthMonitor()
    hc = hm.check_engine("nonexistent_engine_xyz")
    assert hc.available is False
    assert "unknown" in hc.last_error.lower() or "Unknown" in hc.last_error


# ────────────────────────────────────────────────────────────
# CT-04: HealthMonitor verifica research skill valida
# ────────────────────────────────────────────────────────────

def test_health_monitor_check_research_skill():
    """CT-04: check_research_skill() deve retornar HealthCheck."""
    hm = HealthMonitor()
    hc = hm.check_research_skill("game_theory")
    assert isinstance(hc, HealthCheck)
    assert isinstance(hc.available, bool)
    assert isinstance(hc.response_time_ms, (int, float))
    assert hc.engine == "game_theory"


# ────────────────────────────────────────────────────────────
# CT-05: HealthMonitor verifica todas as research skills
# ────────────────────────────────────────────────────────────

def test_health_monitor_check_all_research_skills():
    """CT-05: check_all_research_skills() deve verificar 4 skills."""
    hm = HealthMonitor()
    results = hm.check_all_research_skills()
    assert len(results) == 4
    for name in RESEARCH_SKILLS:
        assert name in results
        assert isinstance(results[name], HealthCheck)


# ────────────────────────────────────────────────────────────
# CT-06: HealthMonitor heartbeat retorna estrutura completa
# ────────────────────────────────────────────────────────────

def test_health_monitor_heartbeat():
    """CT-06: heartbeat() deve retornar dict com 8 checks (4 engines + 4 skills)."""
    hm = HealthMonitor()
    hb = hm.heartbeat()
    assert "timestamp" in hb
    assert hb["total_checks"] == 8  # 4 engines + 4 skills
    assert "available" in hb
    assert "unhealthy" in hb
    assert "health_pct" in hb
    assert "avg_response_time_ms" in hb
    assert "checks" in hb
    assert len(hb["checks"]) == 8


# ────────────────────────────────────────────────────────────
# CT-07: RepairEngine inicializa
# ────────────────────────────────────────────────────────────

def test_repair_engine_init():
    """CT-07: RepairEngine deve inicializar com HealthMonitor."""
    hm = HealthMonitor()
    re = RepairEngine(hm)
    assert re is not None
    assert hasattr(re, "reload_module")
    assert hasattr(re, "check_dependencies")
    assert hasattr(re, "fallback")


# ────────────────────────────────────────────────────────────
# CT-08: RepairEngine reload_module em engine desconhecido
# ────────────────────────────────────────────────────────────

def test_repair_engine_reload_unknown():
    """CT-08: reload_module() deve retornar RepairRecord com result=failed para engine
    desconhecido."""
    hm = HealthMonitor()
    re = RepairEngine(hm)
    record = re.reload_module("nonexistent_engine_xyz")
    assert isinstance(record, RepairRecord)
    assert record.result == "failed"
    assert "unknown" in record.detail.lower() or "Unknown" in record.diagnosis


# ────────────────────────────────────────────────────────────
# CT-09: RepairEngine check_dependencies em engine sem dependencias
# ────────────────────────────────────────────────────────────

def test_repair_engine_check_deps_no_deps():
    """CT-09: check_dependencies() deve retornar success para engine sem deps."""
    hm = HealthMonitor()
    re = RepairEngine(hm)
    record = re.check_dependencies("kanren")
    assert record.result == "success"
    assert record.action == "dependency_check"


# ────────────────────────────────────────────────────────────
# CT-10: RepairEngine fallback retorna fallback definido
# ────────────────────────────────────────────────────────────

def test_repair_engine_fallback():
    """CT-10: fallback() deve retornar RepairRecord com fallback definido."""
    hm = HealthMonitor()
    re = RepairEngine(hm)
    record = re.fallback("z3")
    assert isinstance(record, RepairRecord)
    assert record.action == "fallback"
    assert record.result in ("success", "failed")
    if record.result == "success":
        assert "sympy" in record.detail


# ────────────────────────────────────────────────────────────
# CT-11: RepairLogger inicializa e loga eventos
# ────────────────────────────────────────────────────────────

def test_repair_logger_log():
    """CT-11: RepairLogger deve logar evento e retornar AuditEntry com hash."""
    logger = RepairLogger()
    entry = logger.log("test_event", {"key": "value"})
    assert isinstance(entry, AuditEntry)
    assert entry.entry_id == "SR-0001"
    assert entry.event_type == "test_event"
    assert entry.data == {"key": "value"}
    assert len(entry.hash) == 64  # SHA-256 hex digest


# ────────────────────────────────────────────────────────────
# CT-12: RepairLogger verify_chain integridade
# ────────────────────────────────────────────────────────────

def test_repair_logger_verify_chain():
    """CT-12: verify_chain() deve retornar True para log sem adulteracao."""
    logger = RepairLogger()
    logger.log("event_a", {"a": 1})
    logger.log("event_b", {"b": 2})
    logger.log("event_c", {"c": 3})
    assert logger.verify_chain() is True

    # Simula adulteracao - modifica hash de uma entrada
    logger._entries[1].hash = "0" * 64
    assert logger.verify_chain() is False


# ────────────────────────────────────────────────────────────
# CT-13: RepairNotifier notifica e integra com logger
# ────────────────────────────────────────────────────────────

def test_repair_notifier_notify_health():
    """CT-13: RepairNotifier.notify_health() deve registrar no Logger e retornar
    AuditEntry."""
    logger = RepairLogger()
    notifier = RepairNotifier(logger)
    hb = _fake_heartbeat()
    entry = notifier.notify_health(hb)
    assert isinstance(entry, AuditEntry)
    assert entry.event_type == "health_check"
    assert entry.data["health_pct"] == 100.0

    # Verifica que o log tem a entrada
    log = logger.get_log()
    assert len(log) == 1
    assert log[0]["event_type"] == "health_check"


# ────────────────────────────────────────────────────────────
# CT-14: SelfRepairOrchestrator pipeline completo
# ────────────────────────────────────────────────────────────

def test_self_repair_orchestrator_pipeline():
    """CT-14: SelfRepairOrchestrator.run_pipeline() deve executar pipeline completo
    e retornar relatorio."""
    orchestrator = SelfRepairOrchestrator()
    result = orchestrator.run_pipeline()

    assert "pipeline_time_ms" in result
    assert result["pipeline_time_ms"] > 0
    assert "initial_health" in result
    assert "final_health" in result
    assert "repairs_attempted" in result
    assert isinstance(result["repairs"], list)
    assert "log_entries" in result
    assert result["log_entries"] > 0
    assert "chain_valid" in result
    assert result["chain_valid"] is True

    # Estado inicial e final devem ser consistentes
    init = result["initial_health"]
    final = result["final_health"]
    assert init["total"] == 8  # 4 engines + 4 skills
    assert final["total"] == 8


# ────────────────────────────────────────────────────────────
# Execucao direta
# ────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))