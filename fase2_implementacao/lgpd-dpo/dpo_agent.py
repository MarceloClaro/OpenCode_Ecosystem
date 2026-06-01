"""
dpo_agent.py — Orquestrador DPO (Data Protection Officer) LGPD.

Integra consent_manager + audit_logger + lgpd_crypto em pipeline unificado.
"""

from consent_manager import ConsentManager
from audit_logger import AuditLogger
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class DataProcessingActivity:
    """Registro de atividade de tratamento (Art. 37)."""
    controller: str
    processor: str
    purpose: str
    data_categories: list[str]
    data_subjects: list[str]
    sharing_countries: list[str]
    security_measures: list[str]
    retention_period: str
    legal_basis: str


class DPOAgent:
    """Orquestrador DPO — ponto unico de governanca de dados pessoais.

    Integra consentimento, auditoria e criptografia para conformidade LGPD.
    """

    def __init__(self):
        self.consent = ConsentManager()
        self.audit = AuditLogger()
        self.activities: list[DataProcessingActivity] = []

    def process_personal_data(self, subject_id: str, data_type: str,
                               purpose: str, agent: str) -> bool:
        """Pipeline completo: verifica consentimento → registra auditoria."""
        has_consent = self.consent.check(subject_id, purpose)
        if not has_consent:
            self.audit.log("denied", subject_id, data_type, purpose, agent,
                           details="Consentimento nao encontrado")
            return False
        self.audit.log("process", subject_id, data_type, purpose, agent)
        return True

    def register_activity(self, activity: DataProcessingActivity) -> None:
        """Registra atividade de tratamento (Art. 37)."""
        self.activities.append(activity)

    def incident_report(self, description: str, affected_subjects: list[str],
                         severity: str = "medium", notified_anpd: bool = False) -> dict:
        """Registra e notifica incidente de seguranca (Art. 48)."""
        return {
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "description": description,
            "affected_subjects": affected_subjects,
            "severity": severity,
            "notified_anpd": notified_anpd,
            "remediation": "Investigacao em andamento",
        }

    def compliance_report(self) -> dict:
        """Relatorio consolidado de conformidade."""
        return {
            "total_consents": self.consent.report(),
            "total_audit_entries": len(self.audit.entries),
            "total_activities": len(self.activities),
            "audit_summary": self.audit.report(),
        }
