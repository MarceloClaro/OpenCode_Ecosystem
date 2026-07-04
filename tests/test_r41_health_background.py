#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes TDD — R41: Health Background Monitor + Webhook (SPEC-084)
==================================================================
20 CTs validando HealthSnapshot, HealthHistoryLogger, WebhookNotifier,
HealthBackgroundService e integracao.

SAIDA OBRIGATORIA: PORTUGUES BRASILEIRO FORMAL
"""

import json
import os
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ajusta path para import do modulo sendo testado
_BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_BASE / "core" / "services"))

from health_background import (
    HealthSnapshot,
    HealthHistoryLogger,
    WebhookConfig,
    WebhookNotifier,
    HealthBackgroundService,
)


# ────────────────────────────────────────────────────────────
# Helpers
# ────────────────────────────────────────────────────────────

def _make_snapshot(
    health_pct: float = 100.0,
    unhealthy: int = 0,
    engines: list[str] | None = None,
) -> HealthSnapshot:
    """Cria HealthSnapshot para testes."""
    from datetime import datetime, timezone
    return HealthSnapshot(
        timestamp=datetime.now(timezone.utc).isoformat(),
        health_pct=health_pct,
        avg_response_ms=12.34,
        unhealthy_count=unhealthy,
        unhealthy_engines=engines or [],
        engine_details=[],
    )


def _count_history_lines(path: Path) -> int:
    """Conta linhas nao vazias em um arquivo JSONL."""
    if not path.exists():
        return 0
    text = path.read_text(encoding="utf-8").strip()
    return len([l for l in text.split("\n") if l.strip()])


# ════════════════════════════════════════════════════════════
# 5.1 HealthSnapshot (CT-01 a CT-02)
# ════════════════════════════════════════════════════════════

def test_snapshot_creation():
    """CT-01: HealthSnapshot deve criar com todos os campos obrigatorios."""
    ts = "2026-07-04T03:00:00Z"
    snap = HealthSnapshot(
        timestamp=ts,
        health_pct=95.5,
        avg_response_ms=15.3,
        unhealthy_count=1,
        unhealthy_engines=["z3"],
        engine_details=[{"name": "z3", "available": False}],
    )
    assert snap.timestamp == ts
    assert snap.health_pct == 95.5
    assert snap.avg_response_ms == 15.3
    assert snap.unhealthy_count == 1
    assert snap.unhealthy_engines == ["z3"]
    assert len(snap.engine_details) == 1


def test_snapshot_defaults():
    """CT-02: HealthSnapshot deve aceitar listas vazias como default."""
    snap = HealthSnapshot(
        timestamp="2026-07-04T03:00:00Z",
        health_pct=100.0,
        avg_response_ms=0.0,
        unhealthy_count=0,
    )
    assert snap.unhealthy_engines == []
    assert snap.engine_details == []


# ════════════════════════════════════════════════════════════
# 5.2 HealthHistoryLogger (CT-03 a CT-07)
# ════════════════════════════════════════════════════════════

def test_history_append():
    """CT-03: append() deve adicionar entrada ao JSONL."""
    with tempfile.TemporaryDirectory() as tmp:
        log = HealthHistoryLogger(log_dir=tmp)
        snap = _make_snapshot()
        log.append(snap)
        assert _count_history_lines(Path(tmp) / "health_history.jsonl") == 1


def test_history_get_history():
    """CT-04: get_history() deve retornar entradas recentes."""
    with tempfile.TemporaryDirectory() as tmp:
        log = HealthHistoryLogger(log_dir=tmp)
        log.append(_make_snapshot(health_pct=100.0))
        log.append(_make_snapshot(health_pct=95.0))
        log.append(_make_snapshot(health_pct=90.0))

        history = log.get_history(hours=24)
        assert len(history) == 3
        assert all(isinstance(h, HealthSnapshot) for h in history)
        assert history[0].health_pct == 100.0
        assert history[-1].health_pct == 90.0


def test_history_get_trend_improving():
    """CT-05: health_pct crescente deve retornar 'improving'."""
    with tempfile.TemporaryDirectory() as tmp:
        log = HealthHistoryLogger(log_dir=tmp)
        log.append(_make_snapshot(health_pct=70.0))
        log.append(_make_snapshot(health_pct=85.0))
        log.append(_make_snapshot(health_pct=95.0))
        assert log.get_trend() == "improving"


def test_history_get_trend_degrading():
    """CT-06: health_pct decrescente deve retornar 'degrading'."""
    with tempfile.TemporaryDirectory() as tmp:
        log = HealthHistoryLogger(log_dir=tmp)
        log.append(_make_snapshot(health_pct=100.0))
        log.append(_make_snapshot(health_pct=85.0))
        log.append(_make_snapshot(health_pct=75.0))
        assert log.get_trend() == "degrading"


def test_history_trim():
    """CT-07: trim() deve remover entradas excedentes."""
    with tempfile.TemporaryDirectory() as tmp:
        log = HealthHistoryLogger(log_dir=tmp, max_entries=5)
        for i in range(10):
            log.append(_make_snapshot(health_pct=float(100 - i)))
        removed = log.trim(max_entries=3)
        assert removed > 0
        remaining = log.get_history(hours=24 * 365)
        assert len(remaining) <= 3


# ════════════════════════════════════════════════════════════
# 5.3 WebhookNotifier (CT-08 a CT-11)
# ════════════════════════════════════════════════════════════

def test_webhook_send_event_no_config():
    """CT-08: Sem webhooks configurados, send_event() deve retornar 0 (sem erro)."""
    notifier = WebhookNotifier(configs=[])
    snap = _make_snapshot()
    sent = notifier.send_event("warning", snap, None)
    assert sent == 0


def test_webhook_build_payload():
    """CT-10: build_payload() deve conter campos obrigatorios."""
    notifier = WebhookNotifier(configs=[])
    snap = _make_snapshot(health_pct=75.0, unhealthy=2, engines=["z3", "sympy"])
    previous = _make_snapshot(health_pct=90.0)
    payload = notifier._build_payload("alert", snap, previous)

    assert payload["event"] == "alert"
    assert payload["timestamp"] == snap.timestamp
    assert payload["health_pct"] == 75.0
    assert "unhealthy_engines" in payload
    assert payload["previous_pct"] == 90.0
    assert "trend" in payload


def test_webhook_send_event():
    """CT-09: Com config valido, send_event() deve tentar envio."""
    config = WebhookConfig(
        url="http://localhost:0/webhook-test",
        events=["warning", "alert", "critical", "recovery"],
    )
    notifier = WebhookNotifier(configs=[config])
    snap = _make_snapshot(health_pct=85.0)
    # Nao deve lancar excecao mesmo com URL invalida
    sent = notifier.send_event("warning", snap, None)
    assert sent >= 0  # pode ser 0 se conexao falhar, mas sem exception


def test_webhook_health():
    """CT-11: health() deve retornar estatisticas de entrega."""
    notifier = WebhookNotifier(configs=[])
    h = notifier.health()
    assert "total_attempts" in h
    assert "total_success" in h
    assert "total_failures" in h
    assert "configs_count" in h
    assert h["configs_count"] == 0


# ════════════════════════════════════════════════════════════
# 5.4 HealthBackgroundService (CT-12 a CT-18)
# ════════════════════════════════════════════════════════════

def test_service_init_default():
    """CT-12: HealthBackgroundService deve inicializar com interval=5, sem webhooks."""
    service = HealthBackgroundService()
    assert service.interval_minutes == 5
    assert service._webhook_configs == []
    assert service._running is False


def test_service_init_custom():
    """CT-13: HealthBackgroundService deve aceitar parametros customizados."""
    config = WebhookConfig(url="http://example.com/hook", events=["critical"])
    service = HealthBackgroundService(interval_minutes=10, webhook_configs=[config])
    assert service.interval_minutes == 10
    assert len(service._webhook_configs) == 1
    assert service._webhook_configs[0].url == "http://example.com/hook"


def test_service_start_stop():
    """CT-14: start() e stop() devem controlar estado corretamente."""
    service = HealthBackgroundService(interval_minutes=60)  # intervalo longo
    assert not service._running

    service.start()
    assert service._running
    assert service._timer is not None

    service.stop()
    assert not service._running


def test_service_check_now():
    """CT-15: check_now() deve retornar HealthSnapshot valido."""
    service = HealthBackgroundService()
    snap = service.check_now()
    assert isinstance(snap, HealthSnapshot)
    assert 0 <= snap.health_pct <= 100
    assert snap.avg_response_ms >= 0
    assert isinstance(snap.unhealthy_engines, list)


def test_service_status():
    """CT-16: status() deve conter campos esperados."""
    service = HealthBackgroundService()
    st = service.status()
    assert "running" in st
    assert st["running"] is False
    assert "interval_minutes" in st
    assert st["interval_minutes"] == 5
    assert "last_check" in st
    assert "total_checks" in st
    assert st["total_checks"] >= 0


def test_service_evaluate_alert_normal():
    """CT-17: health_pct=100 deve retornar None (sem alerta)."""
    service = HealthBackgroundService()
    current = _make_snapshot(health_pct=100.0)
    previous = _make_snapshot(health_pct=100.0)
    alert = service._evaluate_alert(current, previous)
    assert alert is None


def test_service_evaluate_alert_warning():
    """CT-18: health_pct=85 deve retornar 'warning'."""
    service = HealthBackgroundService()
    current = _make_snapshot(health_pct=85.0)
    previous = _make_snapshot(health_pct=100.0)
    alert = service._evaluate_alert(current, previous)
    assert alert == "warning"


def test_service_evaluate_alert_alert():
    """CT-18b: health_pct=75 deve retornar 'alert'."""
    service = HealthBackgroundService()
    current = _make_snapshot(health_pct=75.0)
    previous = _make_snapshot(health_pct=100.0)
    alert = service._evaluate_alert(current, previous)
    assert alert == "alert"


def test_service_evaluate_alert_critical():
    """CT-18c: health_pct=65 deve retornar 'critical'."""
    service = HealthBackgroundService()
    current = _make_snapshot(health_pct=65.0)
    previous = _make_snapshot(health_pct=100.0)
    alert = service._evaluate_alert(current, previous)
    assert alert == "critical"


def test_service_evaluate_alert_recovery():
    """CT-18d: health_pct>=90 apos <90 deve retornar 'recovery'."""
    service = HealthBackgroundService()
    current = _make_snapshot(health_pct=95.0)
    previous = _make_snapshot(health_pct=85.0)
    alert = service._evaluate_alert(current, previous)
    assert alert == "recovery"


# ════════════════════════════════════════════════════════════
# 5.5 Integracao (CT-19 a CT-20)
# ════════════════════════════════════════════════════════════

def test_integration_heartbeat_to_history():
    """CT-19: check_now() -> history -> get_history() deve funcionar em cadeia."""
    with tempfile.TemporaryDirectory() as tmp:
        service = HealthBackgroundService()
        service._history = HealthHistoryLogger(log_dir=tmp)

        snap = service.check_now()
        service._history.append(snap)

        history = service._history.get_history(hours=24)
        assert len(history) == 1
        assert history[0].health_pct == snap.health_pct


def test_integration_alert_webhook():
    """CT-20: health baixo deve gerar evento de webhook."""
    with tempfile.TemporaryDirectory() as tmp:
        config = WebhookConfig(url="http://localhost:0/test", events=["alert", "critical"])
        notifier = WebhookNotifier(configs=[config])

        # Simula ciclo completo
        current = _make_snapshot(health_pct=70.0, unhealthy=1, engines=["z3"])
        previous = _make_snapshot(health_pct=100.0)

        # Verifica que o payload tem os campos obrigatorios
        payload = notifier._build_payload("alert", current, previous)
        assert payload["event"] == "alert"
        assert payload["health_pct"] == 70.0
        assert payload["previous_pct"] == 100.0
        assert "z3" in payload["unhealthy_engines"]

        # Tenta enviar (nao deve lancar excecao)
        sent = notifier.send_event("alert", current, previous)
        assert sent >= 0


# ════════════════════════════════════════════════════════════
# Execucao direta
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
