"""
consent_manager.py — Gerenciamento de consentimento LGPD.

Tipos de consentimento:
- EXPLICITO: Aceitacao ativa (checkbox, assinatura) - Art. 8º, §1º
- TACITO: Por omissao (apos comunicacao) - Art. 8º, §4º
- LEGITIMO: Interesse legitimo (sem consentimento) - Art. 10º
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import json


@dataclass
class ConsentRecord:
    """Registro de consentimento individual."""
    data_subject_id: str
    purpose: str
    scope: list[str]
    consent_type: str  # explicito, tacito, legitimo
    status: str        # active, revoked, expired
    granted_at: str
    expires_at: Optional[str] = None
    revoked_at: Optional[str] = None
    evidence: Optional[str] = None
    metadata: dict = field(default_factory=dict)

    def is_valid(self) -> bool:
        """Verifica se o consentimento esta ativo e valido."""
        if self.status != "active":
            return False
        if self.expires_at:
            exp = datetime.fromisoformat(self.expires_at)
            if datetime.utcnow() > exp:
                return False
        return True


class ConsentManager:
    """Gerenciador de consentimentos LGPD.

    Gerencia ciclo de vida: concessao → auditoria → revogacao.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.records: list[ConsentRecord] = []
        self.storage_path = storage_path

    def grant(
        self,
        subject_id: str,
        purpose: str,
        scope: list[str],
        consent_type: str = "explicito",
        expires_in_days: Optional[int] = None,
        evidence: Optional[str] = None,
    ) -> ConsentRecord:
        """Registra consentimento explicito."""
        expires_at = None
        if expires_in_days:
            expires_at = (datetime.utcnow() + timedelta(days=expires_in_days)).isoformat()

        record = ConsentRecord(
            data_subject_id=subject_id,
            purpose=purpose,
            scope=scope,
            consent_type=consent_type,
            status="active",
            granted_at=datetime.utcnow().isoformat(),
            expires_at=expires_at,
            evidence=evidence,
        )
        self.records.append(record)
        return record

    def revoke(self, subject_id: str, purpose: str) -> bool:
        """Revoga consentimento ativo para proposito especifico."""
        for record in self.records:
            if (record.data_subject_id == subject_id
                    and record.purpose == purpose
                    and record.status == "active"):
                record.status = "revoked"
                record.revoked_at = datetime.utcnow().isoformat()
                return True
        return False

    def check(self, subject_id: str, purpose: str) -> bool:
        """Verifica se consentimento esta ativo para proposito."""
        return any(
            r.data_subject_id == subject_id
            and r.purpose == purpose
            and r.is_valid()
            for r in self.records
        )

    def list_by_subject(self, subject_id: str) -> list[ConsentRecord]:
        """Retorna todos os consentimentos de um titular."""
        return [r for r in self.records if r.data_subject_id == subject_id]

    def list_by_purpose(self, purpose: str) -> list[ConsentRecord]:
        """Retorna todos os consentimentos para um proposito."""
        return [r for r in self.records if r.purpose == purpose]

    def revoke_all(self, subject_id: str) -> int:
        """Revoga todos os consentimentos de um titular (Art. 8º, §5º)."""
        count = 0
        for record in self.records:
            if record.data_subject_id == subject_id and record.status == "active":
                record.status = "revoked"
                record.revoked_at = datetime.utcnow().isoformat()
                count += 1
        return count

    def report(self) -> dict:
        """Relatorio estatistico de consentimentos."""
        total = len(self.records)
        active = sum(1 for r in self.records if r.status == "active")
        revoked = sum(1 for r in self.records if r.status == "revoked")
        expired = sum(1 for r in self.records if r.status == "expired")
        return {
            "total": total,
            "active": active,
            "revoked": revoked,
            "expired": expired,
            "subjects": len({r.data_subject_id for r in self.records}),
        }

    def export_json(self, path: str) -> None:
        """Exporta registros para JSON."""
        data = []
        for r in self.records:
            d = {
                "data_subject_id": r.data_subject_id,
                "purpose": r.purpose,
                "scope": r.scope,
                "consent_type": r.consent_type,
                "status": r.status,
                "granted_at": r.granted_at,
                "expires_at": r.expires_at,
                "revoked_at": r.revoked_at,
                "evidence": r.evidence,
            }
            data.append(d)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_json(self, path: str) -> int:
        """Carrega registros de JSON. Retorna quantidade carregada."""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for d in data:
            self.records.append(ConsentRecord(**d))
        return len(data)
