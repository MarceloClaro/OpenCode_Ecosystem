"""
Testes dos Servicos (core/services/)

Cobre:
- ServiceRegistry: register, resolve, is_registered, list_services, count
- ServiceRegistry: singleton get_service_registry, reset
- EvolutionService: record_round, rounds, latest_round, best_score, average_score
- EvolutionService: historico limitado (max_history)
- HealthService: report_health, get_health, get_all_health
- HealthService: thresholds (healthy, attention, alert, critical)
- HealthService: summary, average_score, contadores
"""

import pytest

from core.services import (
    ServiceRegistry,
    get_service_registry,
    reset_service_registry,
)
from core.services.evolution import EvolutionService, EvolutionRound
from core.services.health import HealthService, ComponentHealth


# ═══════════════════════════════════════════════════════════════════
# ServiceRegistry
# ═══════════════════════════════════════════════════════════════════


class TestServiceRegistry:
    """Testa o registro centralizado de servicos."""

    @pytest.fixture(autouse=True)
    def reset(self):
        reset_service_registry()
        yield
        reset_service_registry()

    def test_register_and_resolve(self):
        registry = get_service_registry()
        service = {"name": "test-service"}
        registry.register("test", service)
        resolved = registry.resolve("test")
        assert resolved is service

    def test_resolve_nonexistent(self):
        registry = get_service_registry()
        with pytest.raises(Exception):
            registry.resolve("no-such")

    def test_is_registered(self):
        registry = get_service_registry()
        assert registry.is_registered("foo") is False
        registry.register("foo", "bar")
        assert registry.is_registered("foo") is True

    def test_list_services(self):
        registry = get_service_registry()
        registry.register("alpha", 1)
        registry.register("beta", 2)
        services = registry.list_services()
        assert "alpha" in services
        assert "beta" in services

    def test_count(self):
        registry = get_service_registry()
        assert registry.count == 0
        registry.register("a", 1)
        assert registry.count == 1
        registry.register("b", 2)
        assert registry.count == 2

    def test_singleton(self):
        reset_service_registry()
        r1 = get_service_registry()
        r2 = get_service_registry()
        assert r1 is r2

    def test_reset(self):
        reset_service_registry()
        r1 = get_service_registry()
        reset_service_registry()
        r2 = get_service_registry()
        assert r1 is not r2

    def test_repr(self):
        registry = get_service_registry()
        registry.register("svc", "value")
        r = repr(registry)
        assert "ServiceRegistry" in r
        assert "svc" in r


# ═══════════════════════════════════════════════════════════════════
# EvolutionService
# ═══════════════════════════════════════════════════════════════════


class TestEvolutionService:
    """Testa o servico de evolucao."""

    @pytest.fixture
    def evo(self):
        return EvolutionService(max_history=5)

    def test_initial_state(self, evo):
        assert evo.rounds == []
        assert evo.latest_round is None
        assert evo.best_score == 0.0
        assert evo.average_score == 0.0

    def test_record_round(self, evo):
        rec = evo.record_round(1, "skill-a", 85.0, ["insight1"])
        assert isinstance(rec, EvolutionRound)
        assert rec.round_number == 1
        assert rec.skill_name == "skill-a"
        assert rec.score == 85.0
        assert rec.insights == ["insight1"]

    def test_latest_round(self, evo):
        evo.record_round(1, "a", 80.0)
        evo.record_round(2, "b", 90.0)
        assert evo.latest_round.round_number == 2
        assert evo.latest_round.skill_name == "b"

    def test_best_score(self, evo):
        evo.record_round(1, "a", 70.0)
        evo.record_round(2, "b", 95.0)
        evo.record_round(3, "c", 85.0)
        assert evo.best_score == 95.0

    def test_average_score(self, evo):
        evo.record_round(1, "a", 80.0)
        evo.record_round(2, "b", 90.0)
        assert evo.average_score == 85.0

    def test_max_history(self, evo):
        for i in range(10):
            evo.record_round(i, f"skill-{i}", float(i * 10))
        assert len(evo.rounds) == 5
        assert evo.rounds[0].round_number == 5  # Primeiro foi expulso

    def test_rounds_immutable_copy(self, evo):
        evo.record_round(1, "a", 90.0)
        rounds = evo.rounds
        rounds.clear()
        assert len(evo.rounds) == 1  # Interno nao foi afetado

    def test_record_without_insights(self, evo):
        rec = evo.record_round(1, "a", 75.0)
        assert rec.insights == []

    def test_repr(self, evo):
        evo.record_round(1, "test", 85.0)
        r = repr(evo)
        assert "EvolutionService" in r
        assert "rounds=1" in r


# ═══════════════════════════════════════════════════════════════════
# HealthService
# ═══════════════════════════════════════════════════════════════════


class TestHealthService:
    """Testa o servico de health check."""

    @pytest.fixture
    def health(self):
        return HealthService()

    def test_report_healthy(self, health):
        h = health.report_health("core", 98.0)
        assert h.status == "healthy"
        assert h.score == 98.0
        assert h.name == "core"

    def test_report_attention(self, health):
        h = health.report_health("module-x", 88.0)
        assert h.status == "attention"

    def test_report_alert(self, health):
        h = health.report_health("module-y", 75.0)
        assert h.status == "alert"

    def test_report_critical(self, health):
        h = health.report_health("module-z", 50.0)
        assert h.status == "critical"

    def test_get_health(self, health):
        health.report_health("core", 95.0)
        h = health.get_health("core")
        assert h is not None
        assert h.name == "core"
        assert h.score == 95.0

    def test_get_health_nonexistent(self, health):
        assert health.get_health("no-such") is None

    def test_get_all_health(self, health):
        health.report_health("a", 90.0)
        health.report_health("b", 80.0)
        all_h = health.get_all_health()
        assert len(all_h) == 2
        assert "a" in all_h
        assert "b" in all_h

    def test_summary(self, health):
        health.report_health("core", 98.0)
        health.report_health("module-x", 85.0)
        s = health.summary()
        assert s["total"] == 2
        assert s["healthy"] == 1
        assert s["attention"] == 1

    def test_average_score(self, health):
        assert health.average_score == 0.0
        health.report_health("a", 90.0)
        health.report_health("b", 70.0)
        assert health.average_score == 80.0

    def test_counters(self, health):
        health.report_health("a", 98.0)  # healthy
        health.report_health("b", 88.0)  # attention
        health.report_health("c", 75.0)  # alert
        health.report_health("d", 50.0)  # critical
        assert health.healthy_count == 1
        assert health.attention_count == 1
        assert health.alert_count == 1
        assert health.critical_count == 1

    def test_report_with_details(self, health):
        details = {"last_check_ok": True, "response_time_ms": 45}
        h = health.report_health("api", 95.0, details=details)
        assert h.details == details

    def test_report_updates_existing(self, health):
        health.report_health("core", 95.0)
        health.report_health("core", 70.0)
        h = health.get_health("core")
        assert h.score == 70.0
        assert h.status == "alert"

    def test_repr(self, health):
        health.report_health("test", 90.0)
        r = repr(health)
        assert "HealthService" in r
        assert "components=1" in r

    def test_empty_summary(self, health):
        s = health.summary()
        assert s["total"] == 0
        assert s["average_score"] == 0.0
