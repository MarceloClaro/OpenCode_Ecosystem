# -*- coding: utf-8 -*-
"""Testes TDD para OPUS 4-Phase Orchestration Contract (R28)"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "nexus", "scripts"))

from opus_orchestration import (
    OPUSContract, OPUSState, ActionAuthorizationBoundary,
    Phase, ActionCategory, AuthorizationLevel, opus_execute_pipeline,
)


def test_opus_001_create_contract():
    """OPUS contract pode ser criado com missao"""
    c = OPUSContract("Teste")
    assert c.mission == "Teste"
    assert c.state.phase == Phase.OPEN


def test_opus_002_open_phase():
    """Fase OPEN executa e retorna escopo"""
    c = OPUSContract("Missao teste")
    result = c.open({"context": "teste"})
    assert result["phase"] == "open"
    assert result["next"] == "plan"
    assert "scope" in c.state.artifacts


def test_opus_003_plan_phase():
    """Fase PLAN apos OPEN"""
    c = OPUSContract("Missao teste")
    c.open()
    result = c.plan({"steps": ["passo1", "passo2"]})
    assert result["phase"] == "plan"
    assert result["next"] == "unfold"
    assert "plan" in c.state.artifacts


def test_opus_004_unfold_phase():
    """Fase UNFOLD executa acoes"""
    c = OPUSContract("Missao teste")
    c.open()
    c.plan({"steps": ["passo1"]})
    result = c.unfold([{"action": "executar", "target": "alvo"}])
    assert result["phase"] == "unfold"
    assert result["next"] == "seal"
    assert "execution_results" in c.state.artifacts


def test_opus_005_seal_phase():
    """Fase SEAL completa o ciclo"""
    c = OPUSContract("Missao teste")
    c.open()
    c.plan()
    c.unfold()
    result = c.seal({"status": "ok"})
    assert result["phase"] == "seal"
    assert result["status"] == "COMPLETED"
    assert c.state.completed_at is not None


def test_opus_006_aab_blocks_unauthorized():
    """AAB bloqueia acao nao autorizada na fase"""
    c = OPUSContract("Teste AAB")
    # Tenta EXECUTE na fase OPEN (deve bloquear)
    level = c.aab.authorize(Phase.OPEN, ActionCategory.EXECUTE)
    assert level == AuthorizationLevel.BLOCKED


def test_opus_007_aab_allows_authorized():
    """AAB permite acao autorizada na fase"""
    c = OPUSContract("Teste AAB")
    level = c.aab.authorize(Phase.UNFOLD, ActionCategory.DELEGATE)
    assert level == AuthorizationLevel.AUTO


def test_opus_008_full_pipeline():
    """Pipeline completo OPEN->PLAN->UNFOLD->SEAL"""
    c = OPUSContract("Pipeline completo")
    c.open()
    c.plan({"steps": 3})
    c.unfold([{"a": 1}, {"a": 2}])
    result = c.seal()
    assert result["status"] == "COMPLETED"
    assert c.state.phase == Phase.SEAL


def test_opus_009_decision_tracking():
    """Decisoes sao registradas durante execucao"""
    c = OPUSContract("Decisoes")
    c.open()
    c.plan()
    assert len(c.state.decisions) >= 1
    assert "transition" in c.state.decisions[0]["action"]


def test_opus_010_opus_execute_pipeline():
    """Funcao de conveniencia opus_execute_pipeline funciona"""
    def open_handler(state, ctx):
        state.artifacts["custom_open"] = "feito"
    def seal_handler(state, val):
        state.artifacts["custom_seal"] = "selado"

    result = opus_execute_pipeline(
        "Pipeline automatico",
        open_fn=open_handler,
        seal_fn=seal_handler,
    )
    assert result["report"]["status"] == "COMPLETED"
    assert result["report"]["phases_executed"] == ["open", "plan", "unfold", "seal"]


def test_opus_011_unfold_without_plan_raises():
    """UNFOLD sem PLAN deve levantar erro"""
    c = OPUSContract("Erro")
    c.open()
    import pytest
    with pytest.raises(RuntimeError, match="sem PLAN"):
        c.unfold()


def test_opus_012_get_report():
    """Relatorio OPUS contem todas as informacoes"""
    c = OPUSContract("Relatorio")
    c.open()
    c.plan()
    c.unfold()
    c.seal()
    report = c.get_report()
    assert report["status"] == "COMPLETED"
    assert report["contract_id"] == c.state.id
    assert len(report["phases_executed"]) == 4
