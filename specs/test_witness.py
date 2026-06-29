# -*- coding: utf-8 -*-
"""Testes TDD para Witness Pattern (R28)"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "nexus", "scripts"))

from witness_pattern import (
    WitnessObserver, TrustEngineBridge, WitnessSignal,
    ActionRisk, SignalSeverity,
)


def test_witness_001_observe_safe_action():
    """Witness classifica acao segura como SAFE"""
    w = WitnessObserver()
    signal = w.observe({"name": "read_file", "type": "read"})
    assert signal.risk == ActionRisk.SAFE
    assert signal.severity == SignalSeverity.INFO


def test_witness_002_observe_blocked_action():
    """Witness classifica acao bloqueada como BLOCKED"""
    w = WitnessObserver()
    signal = w.observe({"name": "rm -rf /", "type": "execute"})
    assert signal.risk == ActionRisk.BLOCKED


def test_witness_003_observe_risky_action():
    """Witness classifica acao arriscada como RISKY"""
    w = WitnessObserver()
    signal = w.observe({"name": "modify_config"})
    assert signal.risk == ActionRisk.RISKY


def test_witness_004_goal_drift_detection():
    """Witness detecta goal drift em acoes bloqueadas"""
    w = WitnessObserver()
    w.observe({"name": "sudo rm -rf"})
    w.observe({"name": "drop table users"})
    assert w.goal_drift_count == 2
    assert w.witness_count == 2


def test_witness_005_trustengine_bridge_blocks():
    """TrustEngine bridge bloqueia acao perigosa"""
    w = WitnessObserver()
    bridge = TrustEngineBridge(w)
    result = bridge.observe_and_decide({"name": "rm -rf /"})
    assert result["decision"]["decision"] == "block"
    assert result["signal"]["risk"] == "blocked"


def test_witness_006_trustengine_bridge_allows():
    """TrustEngine bridge permite acao segura"""
    w = WitnessObserver()
    bridge = TrustEngineBridge(w)
    result = bridge.observe_and_decide({"name": "read_file", "type": "read"})
    assert result["decision"]["decision"] == "allow"


def test_witness_007_trustengine_bridge_warns():
    """TrustEngine bridge emite warning para acao arriscada"""
    w = WitnessObserver()
    bridge = TrustEngineBridge(w)
    result = bridge.observe_and_decide({"name": "modify_config"})
    assert result["decision"]["decision"] == "warn_and_allow"


def test_witness_008_custom_risk_rule():
    """Regra de risco personalizada funciona"""
    w = WitnessObserver()
    def custom_rule(action):
        if "danger" in action.get("name", ""):
            return WitnessSignal(
                target_action=action["name"],
                risk=ActionRisk.BLOCKED,
                severity=SignalSeverity.CRITICAL,
                reasoning="Regra personalizada",
            )
        return None

    w.add_risk_rule(custom_rule)
    # Acao com "danger"
    signal = w.observe({"name": "dangerous_action"})
    assert signal.risk == ActionRisk.BLOCKED


def test_witness_009_bridge_stats():
    """Bridge retorna estatisticas corretas"""
    w = WitnessObserver()
    bridge = TrustEngineBridge(w)
    bridge.observe_and_decide({"name": "read"})
    bridge.observe_and_decide({"name": "rm -rf"})
    bridge.observe_and_decide({"name": "write_file"})
    stats = bridge.get_stats()
    assert stats["total_observations"] == 3
    assert stats["allowed"] >= 1
    assert stats["blocked"] >= 1


def test_witness_010_signal_has_id():
    """Cada sinal tem ID unico"""
    w = WitnessObserver()
    s1 = w.observe({"name": "acao1"})
    s2 = w.observe({"name": "acao2"})
    assert s1.id != s2.id


def test_witness_011_context_affects_risk():
    """Contexto de goal drift afeta classificacao de risco"""
    w = WitnessObserver()
    signal = w.observe(
        {"name": "escrever_arquivo"},
        {"goal_drift_score": 0.85}
    )
    assert signal.risk in (ActionRisk.RISKY, ActionRisk.MODERATE)


def test_witness_012_get_report():
    """Relatorio do Witness contem todas as metricas"""
    w = WitnessObserver()
    w.observe({"name": "read"})
    w.observe({"name": "rm -rf"})
    report = w.get_report()
    assert report["total_observations"] == 2
    assert report["goal_drift_detections"] >= 1
    assert report["signals_emitted"] == 2
