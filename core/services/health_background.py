# -*- coding: utf-8 -*-
"""
core/services/health_background.py — Health Background Monitor + Webhook Notifications.

Implementa a SPEC-084 (R41): servico de monitoramento em background que
executa health checks periodicos, registra historico time-series e notifica
webhooks configurados quando a saude do ecossistema degrada.

Camadas:
  1. HealthSnapshot         → Dataclass de snapshot de saude
  2. HealthHistoryLogger    → Persistencia time-series em JSONL
  3. WebhookConfig + WebhookNotifier → Notificacao HTTP
  4. HealthBackgroundService → Scheduler em background (threading)

Uso:
    service = HealthBackgroundService(interval_minutes=5)
    service.start()
    # ... sistema opera ...
    service.stop()

Dependencias: threading, json, urllib (stdlib apenas)
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# ════════════════════════════════════════════════════════════
# Camada 1: HealthSnapshot
# ════════════════════════════════════════════════════════════

@dataclass
class HealthSnapshot:
    """Snapshot completo da saude do ecossistema em um instante."""

    timestamp: str
    health_pct: float
    avg_response_ms: float
    unhealthy_count: int
    unhealthy_engines: list[str] = field(default_factory=list)
    engine_details: list[dict] = field(default_factory=list)


# ════════════════════════════════════════════════════════════
# Camada 2: HealthHistoryLogger
# ════════════════════════════════════════════════════════════

class HealthHistoryLogger:
    """Registra historico time-series de snapshots de saude em JSONL.

    Formato: JSON Lines (append-only), uma linha por snapshot.
    Cada linha contem todos os campos de HealthSnapshot serializados.

    Args:
        log_dir: Diretorio para o arquivo health_history.jsonl
        max_entries: Numero maximo de entradas antes de trim()
    """

    HISTORY_FILENAME = "health_history.jsonl"

    def __init__(self, log_dir: str | Path | None = None, max_entries: int = 1000):
        self._log_dir = Path(log_dir) if log_dir else Path.cwd()
        self._log_dir.mkdir(parents=True, exist_ok=True)
        self._path = self._log_dir / self.HISTORY_FILENAME
        self._max_entries = max_entries
        self._lock = threading.Lock()

    # ── API publica ─────────────────────────────────────────

    def append(self, snapshot: HealthSnapshot) -> None:
        """Adiciona um snapshot ao historico (thread-safe)."""
        with self._lock:
            line = json.dumps(asdict(snapshot), ensure_ascii=False)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(line + "\n")

    def get_history(self, hours: int = 24) -> list[HealthSnapshot]:
        """Retorna snapshots das ultimas N horas."""
        cutoff = time.time() - (hours * 3600)
        all_snapshots = self._read_all()
        return [s for s in all_snapshots if self._parse_timestamp(s.timestamp) >= cutoff]

    def get_trend(self) -> str:
        """Retorna tendencia com base nos ultimos 5 snapshots.

        Returns:
            "improving" se health_pct crescente
            "degrading" se health_pct decrescente
            "stable" caso contrario
        """
        snapshots = self._read_all()[-5:]
        if len(snapshots) < 2:
            return "stable"

        pcts = [s.health_pct for s in snapshots]
        diffs = [pcts[i + 1] - pcts[i] for i in range(len(pcts) - 1)]
        avg_diff = sum(diffs) / len(diffs)

        if avg_diff > 1.0:
            return "improving"
        elif avg_diff < -1.0:
            return "degrading"
        return "stable"

    def get_summary(self) -> dict:
        """Resumo do historico."""
        all_snapshots = self._read_all()
        if not all_snapshots:
            return {"total": 0, "trend": "stable", "avg_health": 0.0}

        avg_health = sum(s.health_pct for s in all_snapshots) / len(all_snapshots)
        return {
            "total": len(all_snapshots),
            "trend": self.get_trend(),
            "avg_health": round(avg_health, 1),
            "last_health": all_snapshots[-1].health_pct,
        }

    def trim(self, max_entries: int | None = None) -> int:
        """Remove entradas excedentes. Retorna quantas foram removidas."""
        target = max_entries or self._max_entries
        with self._lock:
            all_snapshots = self._read_all()
            if len(all_snapshots) <= target:
                return 0

            removed = len(all_snapshots) - target
            kept = all_snapshots[-target:]

            # Reescreve o arquivo com apenas as mantidas
            with open(self._path, "w", encoding="utf-8") as f:
                for snap in kept:
                    f.write(json.dumps(asdict(snap), ensure_ascii=False) + "\n")
            return removed

    # ── Metodos internos ─────────────────────────────────────

    def _read_all(self) -> list[HealthSnapshot]:
        """Le todas as entradas do arquivo JSONL."""
        if not self._path.exists() or self._path.stat().st_size == 0:
            return []
        snapshots = []
        with open(self._path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    snapshots.append(HealthSnapshot(**data))
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning("Entrada invalida no health_history: %s", e)
        return snapshots

    @staticmethod
    def _parse_timestamp(ts: str) -> float:
        """Converte timestamp ISO para epoch."""
        try:
            dt = datetime.fromisoformat(ts)
            return dt.timestamp()
        except (ValueError, TypeError):
            return 0.0


# ════════════════════════════════════════════════════════════
# Camada 3: WebhookConfig + WebhookNotifier
# ════════════════════════════════════════════════════════════

@dataclass
class WebhookConfig:
    """Configuracao de um webhook para notificacao de eventos de saude.

    Attributes:
        url: URL do webhook (HTTP POST)
        events: Lista de eventos que disparam este webhook
                ("warning", "alert", "critical", "recovery")
        timeout_s: Timeout em segundos para a requisicao HTTP
        retry_count: Numero de tentativas adicionais em caso de falha
        enabled: Se o webhook esta ativo
    """

    url: str
    events: list[str] = field(default_factory=lambda: ["warning", "alert", "critical", "recovery"])
    timeout_s: float = 5.0
    retry_count: int = 1
    enabled: bool = True


class WebhookNotifier:
    """Notifica webhooks configurados sobre eventos de saude.

    Nao bloqueia o scheduler. Falhas de webhook sao registradas em log
    mas nao propagam excecoes.

    Args:
        configs: Lista de WebhookConfig
    """

    def __init__(self, configs: list[WebhookConfig] | None = None):
        self._configs = configs or []
        self._total_attempts = 0
        self._total_success = 0
        self._total_failures = 0

    # ── API publica ─────────────────────────────────────────

    def send_event(
        self,
        event: str,
        snapshot: HealthSnapshot,
        previous: HealthSnapshot | None,
    ) -> int:
        """Envia evento para todos os webhooks configurados para este tipo.

        Args:
            event: Tipo do evento ("warning", "alert", "critical", "recovery")
            snapshot: Snapshot atual de saude
            previous: Snapshot anterior (opcional)

        Returns:
            Numero de webhooks configurados para este evento
        """
        matching = [c for c in self._configs if c.enabled and event in c.events]
        if not matching:
            return 0

        payload = self._build_payload(event, snapshot, previous)

        for config in matching:
            self._attempt_send(config, payload)

        return len(matching)

    def _build_payload(
        self,
        event: str,
        snapshot: HealthSnapshot,
        previous: HealthSnapshot | None,
    ) -> dict:
        """Constroi payload JSON para o webhook."""
        payload = {
            "event": event,
            "timestamp": snapshot.timestamp,
            "health_pct": snapshot.health_pct,
            "avg_response_ms": snapshot.avg_response_ms,
            "unhealthy_count": snapshot.unhealthy_count,
            "unhealthy_engines": snapshot.unhealthy_engines,
            "previous_pct": previous.health_pct if previous else None,
            "trend": "degrading" if previous and snapshot.health_pct < previous.health_pct else "stable",
        }
        return payload

    def health(self) -> dict:
        """Estatisticas de entrega dos webhooks."""
        return {
            "total_attempts": self._total_attempts,
            "total_success": self._total_success,
            "total_failures": self._total_failures,
            "configs_count": len(self._configs),
        }

    # ── Metodos internos ─────────────────────────────────────

    def _attempt_send(self, config: WebhookConfig, payload: dict) -> bool:
        """Tenta enviar payload para uma URL, com retry."""
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            config.url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        attempts = 1 + config.retry_count
        for attempt in range(attempts):
            self._total_attempts += 1
            try:
                with urllib.request.urlopen(req, timeout=config.timeout_s) as resp:
                    self._total_success += 1
                    return True
            except (urllib.error.URLError, urllib.error.HTTPError, OSError) as e:
                self._total_failures += 1
                if attempt < attempts - 1:
                    logger.warning(
                        "Webhook %s falhou (tentativa %d/%d): %s. Retentando...",
                        config.url, attempt + 1, attempts, e,
                    )
                    time.sleep(2.0)
                else:
                    logger.error(
                        "Webhook %s falhou apos %d tentativas: %s",
                        config.url, attempts, e,
                    )
        return False


# ════════════════════════════════════════════════════════════
# Camada 4: HealthBackgroundService
# ════════════════════════════════════════════════════════════

class HealthBackgroundService:
    """Servico de monitoramento de saude em background.

    Executa health checks periodicos em uma thread separada, registra
    historico e notifica webhooks quando a saude degrada.

    Args:
        interval_minutes: Intervalo entre health checks (default: 5)
        webhook_configs: Lista de WebhookConfig para notificacao
        history: HealthHistoryLogger (criado automaticamente se None)
    """

    def __init__(
        self,
        interval_minutes: int = 5,
        webhook_configs: list[WebhookConfig] | None = None,
        history: HealthHistoryLogger | None = None,
    ):
        self.interval_minutes = interval_minutes
        self._webhook_configs = webhook_configs or []
        self._notifier = WebhookNotifier(self._webhook_configs)
        self._history = history or HealthHistoryLogger()
        self._timer: threading.Timer | None = None
        self._running = False
        self._last_check: HealthSnapshot | None = None
        self._total_checks = 0
        self._lock = threading.Lock()

    # ── API publica ─────────────────────────────────────────

    def start(self) -> None:
        """Inicia o scheduler em background."""
        if self._running:
            logger.warning("HealthBackgroundService ja esta em execucao")
            return

        self._running = True
        self._schedule_next()
        logger.info(
            "HealthBackgroundService iniciado (intervalo=%d min)",
            self.interval_minutes,
        )

    def stop(self) -> None:
        """Para o scheduler em background."""
        self._running = False
        if self._timer:
            self._timer.cancel()
            self._timer = None
        logger.info("HealthBackgroundService parado")

    def status(self) -> dict:
        """Retorna estado atual do servico."""
        with self._lock:
            return {
                "running": self._running,
                "interval_minutes": self.interval_minutes,
                "last_check": self._last_check.timestamp if self._last_check else None,
                "last_health_pct": self._last_check.health_pct if self._last_check else None,
                "total_checks": self._total_checks,
                "webhook_configs": len(self._webhook_configs),
            }

    def check_now(self) -> HealthSnapshot:
        """Executa um health check imediato.

        Tenta importar HealthMonitor do auto-repair (SPEC-083).
        Se nao estiver disponivel, cria um snapshot com base no
        que for possivel verificar.

        Returns:
            HealthSnapshot com o resultado do health check
        """
        return self._perform_check()

    # ── Metodos internos ─────────────────────────────────────

    def _schedule_next(self) -> None:
        """Agenda a proxima execucao do ciclo."""
        if not self._running:
            return
        interval_seconds = self.interval_minutes * 60
        self._timer = threading.Timer(interval_seconds, self._run_cycle)
        self._timer.daemon = True
        self._timer.start()

    def _run_cycle(self) -> None:
        """Executa um ciclo completo de health check."""
        try:
            current = self._perform_check()
            previous = self._last_check

            # Registra no historico
            self._history.append(current)

            # Avalia alertas
            event = self._evaluate_alert(current, previous)
            if event:
                self._notifier.send_event(event, current, previous)
                if event in ("alert", "critical"):
                    logger.warning(
                        "Health %s: %.1f%% (unhealthy: %s)",
                        event, current.health_pct, current.unhealthy_engines,
                    )

            # Atualiza estado
            with self._lock:
                self._last_check = current
                self._total_checks += 1

        except Exception as e:
            logger.error("Erro no ciclo de health check: %s", e)
        finally:
            self._schedule_next()

    def _perform_check(self) -> HealthSnapshot:
        """Executa o health check real.

        Tenta usar HealthMonitor do auto-repair (SPEC-083).
        Se indisponivel, retorna snapshot basico.
        """
        try:
            # Tenta importar HealthMonitor do auto-repair
            import sys as _sys
            _repair_path = (
                Path(__file__).resolve().parent.parent.parent
                / "skills" / "research" / "cross-paradigm-reasoning"
            )
            _sys.path.insert(0, str(_repair_path))
            from autonomous_self_repair import HealthMonitor  # type: ignore

            hm = HealthMonitor()
            hb = hm.heartbeat()

            return HealthSnapshot(
                timestamp=hb["timestamp"],
                health_pct=float(hb["health_pct"]),
                avg_response_ms=float(hb.get("avg_response_time_ms", 0)),
                unhealthy_count=int(hb.get("unhealthy", 0)),
                unhealthy_engines=[
                    name
                    for name, check in hb.get("checks", {}).items()
                    if isinstance(check, dict) and not check.get("available", True)
                ],
                engine_details=list(hb.get("checks", {}).values()),
            )
        except (ImportError, AttributeError, KeyError) as e:
            logger.debug("HealthMonitor indisponivel: %s. Usando fallback.", e)
            return self._fallback_check()

    def _fallback_check(self) -> HealthSnapshot:
        """Health check fallback quando HealthMonitor nao esta disponivel."""
        ts = datetime.now(timezone.utc).isoformat()

        # Verifica engines pelo importlib
        unhealthy = []
        engines_to_check = [
            ("z3", "z3"),
            ("sympy", "sympy"),
        ]
        details = []
        for name, mod_name in engines_to_check:
            available = self._check_import(mod_name)
            details.append({"name": name, "available": available})
            if not available:
                unhealthy.append(name)

        health_pct = round(
            ((len(engines_to_check) - len(unhealthy)) / max(len(engines_to_check), 1)) * 100,
            1,
        )

        return HealthSnapshot(
            timestamp=ts,
            health_pct=health_pct,
            avg_response_ms=0.0,
            unhealthy_count=len(unhealthy),
            unhealthy_engines=unhealthy,
            engine_details=details,
        )

    @staticmethod
    def _check_import(module_name: str) -> bool:
        """Verifica se um modulo Python pode ser importado."""
        import importlib
        import sys
        try:
            importlib.import_module(module_name)
            return True
        except ImportError:
            return False

    def _evaluate_alert(
        self,
        current: HealthSnapshot,
        previous: HealthSnapshot | None,
    ) -> str | None:
        """Avalia se o snapshot atual dispara um alerta.

        Hierarquia: normal → warning (<90) → alert (<80) → critical (<70) → recovery (>=90 apos alerta)

        Args:
            current: Snapshot atual
            previous: Snapshot anterior (opcional)

        Returns:
            String do tipo de evento ou None se saudavel
        """
        # Recovery: voltou a ficar saudavel apos estar degradado
        if previous and current.health_pct >= 90 and previous.health_pct < 90:
            return "recovery"

        # Critical: abaixo de 70
        if current.health_pct < 70:
            return "critical"

        # Alert: abaixo de 80
        if current.health_pct < 80:
            return "alert"

        # Warning: abaixo de 90
        if current.health_pct < 90:
            return "warning"

        # Normal: sem alerta
        return None
