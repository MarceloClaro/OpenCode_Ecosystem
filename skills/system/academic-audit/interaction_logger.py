#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
InteractionLogger v1.0 — Registro Caixa Branca de Todas as Interações
======================================================================
Sistema imutável (append-only JSONL) que registra cada interação
usuário-sistema com contexto completo, timestamp, rastreabilidade
de tokens e auditoria acadêmica.

Princípios:
  1. Imutabilidade: registros são append-only, nunca modificados
  2. Completeza: cada interação captura estado completo (query, response, routing, tokens)
  3. Rastreabilidade: timestamps UTC-3, session_id único, cadeia de decisões
  4. Privacidade: logs são locais, nunca enviados externamente
  5. Integridade: hash SHA-256 de cada entrada para verificação

Formato JSONL:
  {"type": "interaction", "session_id": "...", "timestamp": "...", "query": "...",
   "response_summary": "...", "routing": {...}, "tokens": {...}, "hash": "..."}

Uso:
  from interaction_logger import InteractionLogger
  logger = InteractionLogger()
  logger.log_query(query="PIB do Brasil", response=result, routing=intent)
"""

from __future__ import annotations

import hashlib
import json
import threading
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# ── Constantes ──────────────────────────────────────────────────────────

LOG_DIR = Path(__file__).parent.parent.parent.parent / ".evolve" / "audit-logs"
BRAZIL_TZ = timezone.utc  # UTC-3 na prática via localtime
LOG_FORMAT_VERSION = "1.0.0"

# ── Dataclasses ─────────────────────────────────────────────────────────


@dataclass
class RoutingInfo:
    """Informações de roteamento do DataOrchestrator."""
    domain: str = ""
    source: str = ""
    confidence: float = 0.0
    fallback_used: bool = False
    fallback_chain: list[str] = field(default_factory=list)


@dataclass
class TokenMetrics:
    """Métricas de consumo de tokens."""
    estimated_input: int = 0
    estimated_output: int = 0
    context_size: int = 200_000
    efficiency_ratio: float = 0.0  # output/input
    level: int = 1  # 1=Magnum, 2=Standard, 3=Short


@dataclass
class InteractionRecord:
    """Registro completo de uma interação."""
    type: str = "interaction"
    session_id: str = ""
    interaction_id: str = ""
    timestamp: str = ""
    query: str = ""
    response_summary: str = ""
    routing: RoutingInfo = field(default_factory=RoutingInfo)
    tokens: TokenMetrics = field(default_factory=TokenMetrics)
    pipeline_stage: str = ""  # SEEKER, MASWOS, PhD_Auditor, etc.
    decision_path: list[str] = field(default_factory=list)
    paradigm: str = ""  # Positivista, Interpretativista, etc.
    hash: str = ""

    def compute_hash(self) -> str:
        """Calcula hash SHA-256 do registro para integridade."""
        content = json.dumps({
            "session_id": self.session_id,
            "interaction_id": self.interaction_id,
            "timestamp": self.timestamp,
            "query": self.query,
            "routing_domain": self.routing.domain,
        }, sort_keys=True)
        return hashlib.sha256(content.encode()).hexdigest()[:16]


# ── Logger ──────────────────────────────────────────────────────────────


class InteractionLogger:
    """Logger caixa branca de interações usuário-sistema.

    Thread-safe. Append-only. JSONL formatado.
    """

    _instance: InteractionLogger | None = None
    _lock = threading.Lock()

    def __new__(cls) -> InteractionLogger:
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._initialized = True
        self.session_id = self._generate_session_id()
        self.interaction_count = 0
        self.paradigm = ""
        self.level = 1
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        self._log_file = LOG_DIR / f"session-{self.session_id}.jsonl"
        self._index: list[str] = []  # interaction_ids para busca rápida
        self._start_session()

    def _generate_session_id(self) -> str:
        """Gera ID de sessão único: SESSION-YYYYMMDD-HHMMSS-XXXX."""
        ts = datetime.now(BRAZIL_TZ).strftime("%Y%m%d-%H%M%S")
        short = uuid.uuid4().hex[:4].upper()
        return f"SESSION-{ts}-{short}"

    def _start_session(self) -> None:
        """Registra início da sessão."""
        record = {
            "type": "session_start",
            "session_id": self.session_id,
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            "version": LOG_FORMAT_VERSION,
            "paradigm": self.paradigm,
            "level": self.level,
        }
        self._write_record(record)

    def set_paradigm(self, paradigm: str) -> None:
        """Define paradigma epistemológico da sessão."""
        self.paradigm = paradigm
        self._write_record({
            "type": "paradigm_set",
            "session_id": self.session_id,
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            "paradigm": paradigm,
        })

    def set_level(self, level: int) -> None:
        """Define nível de publicação (1=Magnum, 2=Standard, 3=Short)."""
        self.level = level

    def log_query(
        self,
        query: str,
        response_summary: str = "",
        routing: RoutingInfo | None = None,
        tokens: TokenMetrics | None = None,
        pipeline_stage: str = "",
        decision_path: list[str] | None = None,
    ) -> InteractionRecord:
        """Registra uma interação completa.

        Args:
            query: Query do usuário
            response_summary: Resumo da resposta (primeiros 200 chars)
            routing: Informações de roteamento
            tokens: Métricas de tokens
            pipeline_stage: Estágio do pipeline (SEEKER, MASWOS, etc.)
            decision_path: Cadeia de decisões tomadas

        Returns:
            InteractionRecord com hash de integridade
        """
        self.interaction_count += 1
        interaction_id = f"INT-{self.interaction_count:04d}"

        record = InteractionRecord(
            type="interaction",
            session_id=self.session_id,
            interaction_id=interaction_id,
            timestamp=datetime.now(BRAZIL_TZ).isoformat(),
            query=query,
            response_summary=response_summary[:200],
            routing=routing or RoutingInfo(),
            tokens=tokens or TokenMetrics(level=self.level),
            pipeline_stage=pipeline_stage,
            decision_path=decision_path or [],
            paradigm=self.paradigm,
        )
        record.hash = record.compute_hash()

        self._write_record(asdict(record))
        self._index.append(interaction_id)
        return record

    def log_decision(
        self,
        decision: str,
        rationale: str = "",
        context: str = "",
    ) -> None:
        """Registra uma decisão do pipeline."""
        self._write_record({
            "type": "decision",
            "session_id": self.session_id,
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            "interaction_id": f"INT-{self.interaction_count:04d}",
            "decision": decision,
            "rationale": rationale,
            "context": context,
            "stage": context,
        })

    def log_error(
        self,
        error_type: str,
        message: str,
        stack_trace: str = "",
    ) -> None:
        """Registra um erro."""
        self._write_record({
            "type": "error",
            "session_id": self.session_id,
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            "interaction_id": f"INT-{self.interaction_count:04d}",
            "error_type": error_type,
            "message": message,
            "stack_trace": stack_trace[:500],
        })

    def log_artifact(
        self,
        artifact_type: str,
        artifact_path: str,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Registra criação de artefato (artigo, figura, tabela, etc.)."""
        self._write_record({
            "type": "artifact",
            "session_id": self.session_id,
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            "artifact_type": artifact_type,
            "artifact_path": artifact_path,
            "metadata": metadata or {},
        })

    def close_session(self) -> dict[str, Any]:
        """Fecha sessão e retorna resumo."""
        summary = {
            "type": "session_end",
            "session_id": self.session_id,
            "timestamp": datetime.now(BRAZIL_TZ).isoformat(),
            "total_interactions": self.interaction_count,
            "paradigm": self.paradigm,
            "level": self.level,
            "log_file": str(self._log_file),
        }
        self._write_record(summary)
        return summary

    def _write_record(self, record: dict[str, Any]) -> None:
        """Escreve registro no arquivo JSONL de forma thread-safe."""
        with self._lock:
            line = json.dumps(record, ensure_ascii=False) + "\n"
            with open(self._log_file, "a", encoding="utf-8") as f:
                f.write(line)

    def get_stats(self) -> dict[str, Any]:
        """Retorna estatísticas da sessão atual."""
        return {
            "session_id": self.session_id,
            "interactions": self.interaction_count,
            "paradigm": self.paradigm,
            "level": self.level,
            "log_file": str(self._log_file),
            "size_bytes": self._log_file.stat().st_size if self._log_file.exists() else 0,
        }

    @staticmethod
    def list_sessions() -> list[dict[str, Any]]:
        """Lista todas as sessões registradas."""
        sessions = []
        if not LOG_DIR.exists():
            return sessions
        for f in sorted(LOG_DIR.glob("session-*.jsonl"), reverse=True):
            try:
                # Lê primeira linha para metadados
                with open(f, encoding="utf-8") as fh:
                    first_line = json.loads(fh.readline())
                sessions.append({
                    "session_id": first_line.get("session_id", f.stem),
                    "timestamp": first_line.get("timestamp", ""),
                    "paradigm": first_line.get("paradigm", ""),
                    "file": f.name,
                    "size_kb": round(f.stat().st_size / 1024, 1),
                })
            except Exception:
                sessions.append({"session_id": f.stem, "file": f.name})
        return sessions

    @staticmethod
    def load_session(session_id: str) -> list[dict[str, Any]]:
        """Carrega todos os registros de uma sessão."""
        log_file = LOG_DIR / f"{session_id}.jsonl"
        if not log_file.exists():
            # Tenta match parcial
            matches = list(LOG_DIR.glob(f"*{session_id[-8:]}*"))
            if matches:
                log_file = matches[0]
            else:
                return []

        records = []
        with open(log_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
        return records


# ── Singleton accessor ──────────────────────────────────────────────────

def get_logger() -> InteractionLogger:
    """Obtém instância singleton do logger."""
    return InteractionLogger()
