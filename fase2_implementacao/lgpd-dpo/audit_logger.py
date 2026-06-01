"""
audit_logger.py — Registro de operacoes de tratamento (LGPD Art. 37).

Mantem log imutavel de todas as operacoes com dados pessoais
para auditoria e prestacao de contas a ANPD.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import json


@dataclass
class AuditEntry:
    """Entrada unica de auditoria."""
    timestamp: str
    operation: str          # collect, process, store, share, delete, anonymize
    data_subject_id: str
    data_type: str          # personal, sensitive, pseudonymized, anonymized
    purpose: str
    agent: str              # skill/agente que executou
    details: str = ""
    consent_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class AuditLogger:
    """Logger imutavel de operacoes de tratamento (Art. 37)."""

    def __init__(self):
        self.entries: list[AuditEntry] = []

    def log(self, operation: str, subject_id: str, data_type: str,
            purpose: str, agent: str, details: str = "",
            consent_id: Optional[str] = None) -> AuditEntry:
        """Registra uma operacao de tratamento no log."""
        entry = AuditEntry(
            timestamp=datetime.utcnow().isoformat(),
            operation=operation,
            data_subject_id=subject_id,
            data_type=data_type,
            purpose=purpose,
            agent=agent,
            details=details,
            consent_id=consent_id,
        )
        self.entries.append(entry)
        return entry

    def query(self, subject_id: Optional[str] = None,
              operation: Optional[str] = None,
              purpose: Optional[str] = None,
              since: Optional[str] = None,
              limit: int = 100) -> list[AuditEntry]:
        """Consulta entradas de auditoria com filtros."""
        results = self.entries
        if subject_id:
            results = [e for e in results if e.data_subject_id == subject_id]
        if operation:
            results = [e for e in results if e.operation == operation]
        if purpose:
            results = [e for e in results if e.purpose == purpose]
        if since:
            results = [e for e in results if e.timestamp >= since]
        return results[-limit:]

    def count_by_operation(self) -> dict[str, int]:
        """Contagem de operacoes por tipo."""
        counts: dict[str, int] = {}
        for e in self.entries:
            counts[e.operation] = counts.get(e.operation, 0) + 1
        return counts

    def count_by_subject(self) -> dict[str, int]:
        """Contagem de operacoes por titular."""
        counts: dict[str, int] = {}
        for e in self.entries:
            counts[e.data_subject_id] = counts.get(e.data_subject_id, 0) + 1
        return counts

    def export_json(self, path: str) -> None:
        """Exporta log para JSON."""
        data = []
        for e in self.entries:
            d = {
                "timestamp": e.timestamp,
                "operation": e.operation,
                "data_subject_id": e.data_subject_id,
                "data_type": e.data_type,
                "purpose": e.purpose,
                "agent": e.agent,
                "details": e.details,
                "consent_id": e.consent_id,
            }
            data.append(d)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def report(self) -> dict:
        """Relatorio consolidado de auditoria."""
        return {
            "total_operations": len(self.entries),
            "by_operation": self.count_by_operation(),
            "total_subjects": len(self.count_by_subject()),
            "agents": list(set(e.agent for e in self.entries)),
        }
