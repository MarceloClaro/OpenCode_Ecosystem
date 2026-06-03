"""CTs para Compliance Auditor Engine -- 4 testes criticos de auditoria."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from compliance_auditor_engine import (
    Severity, ControlStatus, Finding, Control, ComplianceFramework,
)


def test_ct1_framework_readiness_score():
    """CT-01: Score de readiness reflete proporcao de controles conformes."""
    framework = ComplianceFramework(
        name="SOC 2 Type II",
        version="2024",
        controls=[
            Control(control_id="CC6.1", domain="Access Control", description="Logical access", status=ControlStatus.COMPLIANT),
            Control(control_id="CC6.2", domain="Access Control", description="User provisioning", status=ControlStatus.COMPLIANT),
            Control(control_id="CC7.1", domain="System Ops", description="Monitoring", status=ControlStatus.PARTIAL),
            Control(control_id="CC7.2", domain="System Ops", description="Incident response", status=ControlStatus.NON_COMPLIANT),
            Control(control_id="CC9.1", domain="Risk", description="Risk assessment", status=ControlStatus.NOT_APPLICABLE),
        ],
    )

    assert framework.total_controls == 5
    assert framework.compliant_controls == 2
    assert framework.readiness_score == 50.0


def test_ct2_finding_severity_tracking():
    """CT-02: Acompanhamento de findings por severidade e evidencias."""
    control = Control(
        control_id="CC6.1",
        domain="Access Control",
        description="Logical access controls",
    )
    control.findings = [
        Finding(
            control_id="CC6.1",
            severity=Severity.CRITICAL,
            description="Credenciais compartilhadas em producao",
            remediation="Criar usuarios IAM individuais com MFA",
        ),
        Finding(
            control_id="CC6.1",
            severity=Severity.HIGH,
            description="Falta revisao trimestral de acessos",
            remediation="Implementar processo de revisao de acessos",
        ),
        Finding(
            control_id="CC6.1",
            severity=Severity.MEDIUM,
            description="Logs de acesso sem alertas",
            remediation="Configurar alertas para acessos anomalos",
        ),
    ]

    assert control.critical_count == 1
    assert control.severity_score == 21  # 10 + 7 + 4
    assert len(control.open_findings) == 3


def test_ct3_evidence_addition():
    """CT-03: Adicao de evidencias a findings resolve gaps."""
    framework = ComplianceFramework(
        name="ISO 27001",
        version="2022",
        controls=[
            Control(
                control_id="A.9.2.1",
                domain="Access Control",
                description="User registration",
                status=ControlStatus.NON_COMPLIANT,
                findings=[
                    Finding(
                        control_id="A.9.2.1",
                        severity=Severity.HIGH,
                        description="Sem processo formal de registro de usuarios",
                        remediation="Documentar e implementar processo",
                    ),
                ],
            ),
        ],
    )

    ok = framework.add_evidence("A.9.2.1", "Sem processo formal de registro de usuarios", "POL-ACCESS-001.pdf")
    assert ok is True

    ok = framework.add_evidence("NONEXISTENT", "desc", "ev.pdf")
    assert ok is False

    finding = framework.controls[0].findings[0]
    assert finding.has_evidence is True
    assert "POL-ACCESS-001.pdf" in finding.evidence


def test_ct4_risk_summary_aggregation():
    """CT-04: Sumario de risco agrega findings de todos os controles."""
    framework = ComplianceFramework(
        name="PCI-DSS",
        version="4.0",
        controls=[
            Control(control_id="PC1", domain="Network", description="Firewall", findings=[
                Finding(control_id="PC1", severity=Severity.CRITICAL, description="Sem firewall", remediation="Instalar"),
                Finding(control_id="PC1", severity=Severity.HIGH, description="Regras muito permissivas", remediation="Restringir"),
            ]),
            Control(control_id="PC2", domain="Data", description="Encryption", findings=[
                Finding(control_id="PC2", severity=Severity.MEDIUM, description="TLS 1.0 ativo", remediation="Desabilitar"),
                Finding(control_id="PC2", severity=Severity.LOW, description="Certificado proximo do vencimento", remediation="Renovar"),
            ]),
        ],
    )

    summary = framework.risk_summary
    assert summary["critical"] == 1
    assert summary["high"] == 1
    assert summary["medium"] == 1
    assert summary["low"] == 1
    assert summary["total"] == 4
    assert framework.total_open_findings == 4
