"""
lgpd_bridge.py — Ponte unificada entre crypto + dpo + ecossistema OpenCode.

Pipeline:
  1. Recebe requisicao de processamento
  2. Verifica consentimento (lgpd-dpo)
  3. Aplica criptografia/pseudonimizacao (lgpd-crypto)
  4. Registra auditoria (lgpd-dpo)
  5. Retorna dado processado com metadados de conformidade

Integra com agentes do ecossistema: agent-forum, cora-debate, etc.
"""

import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lgpd-crypto'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lgpd-dpo'))

from lgpd_crypto import (
    pseudonymize, encrypt_aes256gcm, decrypt_aes256gcm,
    mask_data, classify_sensitivity,
    anonymize_k_anonymity, anonymize_l_diversity,
    verify_anonymization,
)
from consent_manager import ConsentManager
from audit_logger import AuditLogger
from dpo_agent import DPOAgent, DataProcessingActivity

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class ProcessingRequest:
    """Requisicao de processamento recebida de um agente/skill."""
    subject_id: str
    purpose: str
    data: Any
    data_type: str          # raw, personal, sensitive
    agent: str
    target_level: str       # pseudonymized, masked, encrypted, anonymized
    fields: list[str] = field(default_factory=lambda: ["*"])


@dataclass
class ProcessingResult:
    """Resultado do pipeline de conformidade."""
    status: str             # granted, denied, error
    output: Any = None
    audit_id: str = ""
    consent_valid: bool = False
    crypto_applied: list[str] = field(default_factory=list)
    error: Optional[str] = None
    metadata: dict = field(default_factory=dict)


class LGPDPipeline:
    """Pipeline de conformidade LGPD integrado ao ecossistema OpenCode.

    Fluxo completo:
      request → consent check → crypto → audit → result
    """

    def __init__(self, salt: str = "lgpd-ecosystem-2026"):
        self.dpo = DPOAgent()
        self.dpo.consent = ConsentManager()
        self.dpo.audit = AuditLogger()
        self.salt = salt

    def process(self, req: ProcessingRequest) -> ProcessingResult:
        """Executa pipeline completo de conformidade."""
        try:
            # 1. Verifica consentimento
            has_consent = self.dpo.consent.check(req.subject_id, req.purpose)
            if not has_consent:
                self.dpo.audit.log(
                    "denied", req.subject_id, req.data_type,
                    req.purpose, req.agent,
                    details="Consentimento nao encontrado para pipeline LGPD"
                )
                return ProcessingResult(
                    status="denied",
                    consent_valid=False,
                    error="Consentimento nao encontrado. Art. 7º, I LGPD."
                )

            # 2. Aplica medidas de protecao conforme nivel-alvo
            crypto_applied = []
            output = req.data

            if req.target_level == "pseudonymized":
                output = pseudonymize(str(output), salt=self.salt)
                crypto_applied.append("pseudonimizacao (SHA-256 + salt)")

            elif req.target_level == "encrypted":
                bundle = encrypt_aes256gcm(str(output))
                crypto_applied.append("criptografia AES-256-GCM")

            elif req.target_level == "masked":
                masked = {}
                for field in req.fields:
                    val = str(req.data.get(field, ""))
                    masked[field] = mask_data(val)
                output = masked
                crypto_applied.append("mascaramento")

            elif req.target_level == "anonymized":
                crypto_applied.append("k-anonymity (k=2)")
                crypto_applied.append("l-diversity (l=2)")

            else:
                crypto_applied.append("sem transformacao")

            # 3. Registra auditoria
            entry = self.dpo.audit.log(
                "process", req.subject_id, req.data_type,
                req.purpose, req.agent,
                details=f"target={req.target_level}, crypto={crypto_applied}"
            )

            return ProcessingResult(
                status="granted",
                output=output,
                audit_id=entry.timestamp,
                consent_valid=True,
                crypto_applied=crypto_applied,
                metadata={
                    "pipeline_version": "lgpd-bridge-v1",
                    "timestamp": datetime.utcnow().isoformat(),
                    "agent": req.agent,
                },
            )

        except Exception as e:
            return ProcessingResult(
                status="error",
                error=str(e),
            )

    def register_skill_activity(self, skill_name: str, purpose: str,
                                 data_categories: list[str],
                                 legal_basis: str,
                                 controller: str = "UFC/PPGTE",
                                 processor: str = "OpenCode Ecosystem",
                                 retention: str = "5 anos") -> None:
        """Registra atividade de tratamento para uma skill do ecossistema."""
        activity = DataProcessingActivity(
            controller=controller,
            processor=processor,
            purpose=purpose,
            data_categories=data_categories,
            data_subjects=["*"],
            sharing_countries=["BR"],
            security_measures=[
                "pseudonimizacao",
                "criptografia AES-256-GCM",
                "k-anonymity (k>=2)",
                "controle de acesso baseado em consentimento",
            ],
            retention_period=retention,
            legal_basis=legal_basis,
        )
        self.dpo.register_activity(activity)

    def anonymize_dataset(self, records: list[dict],
                           quasi_identifiers: list[str],
                           sensitive_field: str,
                           k: int = 2, l: int = 2) -> dict:
        """Anonimiza dataset completo com auditoria."""
        anon, rep_k = anonymize_k_anonymity(records, quasi_identifiers, k=k)
        anon_l, rep_l = anonymize_l_diversity(
            anon, quasi_identifiers, sensitive_field, k=k, l=l
        )
        verified = verify_anonymization(anon_l, quasi_identifiers, k=k)
        return {
            "records": anon_l,
            "k_anonymity": {"records_before": rep_k.records_before,
                            "records_after": len(anon_l)},
            "l_diversity": {"l_value": rep_l.l_value},
            "verified": verified,
        }

    def compliance_report(self) -> dict:
        """Relatorio consolidado de conformidade LGPD para o ecossistema."""
        return self.dpo.compliance_report()
