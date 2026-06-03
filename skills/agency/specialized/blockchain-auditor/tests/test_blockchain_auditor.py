"""CTs para Blockchain Auditor Engine -- 4 testes criticos de auditoria de contratos."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from blockchain_auditor_engine import (
    Vulnerability, VulnSeverity, ContractAudit, scan_patterns, KNOWN_PATTERNS,
)


def test_ct1_vulnerability_risk_score():
    """CT-01: Scores de risco refletem severidade corretamente."""
    critical = Vulnerability(vuln_id="V-001", title="Reentrancy", severity=VulnSeverity.CRITICAL, description="Reentrancy attack")
    high = Vulnerability(vuln_id="V-002", title="tx.origin", severity=VulnSeverity.HIGH, description="tx.origin auth")
    medium = Vulnerability(vuln_id="V-003", title="Overflow", severity=VulnSeverity.MEDIUM, description="Integer overflow")
    low = Vulnerability(vuln_id="V-004", title="Timestamp", severity=VulnSeverity.LOW, description="Block timestamp")
    info = Vulnerability(vuln_id="V-005", title="Style", severity=VulnSeverity.INFO, description="Code style")

    assert critical.risk_score == 10
    assert high.risk_score == 7
    assert medium.risk_score == 4
    assert low.risk_score == 2
    assert info.risk_score == 0
    assert critical.is_critical_or_high is True
    assert info.is_critical_or_high is False
    assert critical.needs_immediate_action is True


def test_ct2_aggregate_risk_score():
    """CT-02: Score de risco agregado calcula media ponderada."""
    audit = ContractAudit(contract_name="Vault.sol")
    audit.add_finding(Vulnerability(vuln_id="V-001", title="R", severity=VulnSeverity.CRITICAL, description=""))
    audit.add_finding(Vulnerability(vuln_id="V-002", title="T", severity=VulnSeverity.HIGH, description=""))
    audit.add_finding(Vulnerability(vuln_id="V-003", title="O", severity=VulnSeverity.MEDIUM, description=""))

    assert audit.total_findings == 3
    assert audit.critical_count == 1
    assert audit.aggregate_risk_score == 7.0  # (10 + 7 + 4) / 3 = 7.0
    assert audit.is_safe is False


def test_ct3_pattern_scanning():
    """CT-03: Scanner detecta padroes conhecidos em codigo Solidity."""
    vulnerable_code = '''
    function withdraw(uint amount) public {
        require(balances[msg.sender] >= amount);
        (bool success, ) = msg.sender.call{value: amount}("");
        balances[msg.sender] -= amount;
    }
    '''

    audit = scan_patterns("Vault.sol", vulnerable_code)
    assert audit.total_findings > 0


def test_ct4_report_generation():
    """CT-04: Relatorio de auditoria contem todos os campos obrigatorios."""
    audit = ContractAudit(
        contract_name="TokenSwap.sol",
        contract_address="0x1234...abcd",
        language="solidity",
    )
    audit.add_finding(Vulnerability(
        vuln_id="BSA-001",
        title="Reentrancy Attack",
        severity=VulnSeverity.CRITICAL,
        description="External call antes de atualizacao de estado",
        affected_lines=[42, 43, 44],
        recommendation="Seguir Checks-Effects-Interactions",
    ))
    audit.add_finding(Vulnerability(
        vuln_id="BSA-002",
        title="Unchecked External Call",
        severity=VulnSeverity.HIGH,
        description="Chamada externa sem verificacao de retorno",
        affected_lines=[67],
        recommendation="Verificar retorno da chamada",
    ))

    report = audit.generate_report()

    assert report["contract"] == "TokenSwap.sol"
    assert report["address"] == "0x1234...abcd"
    assert report["total_findings"] == 2
    assert report["critical"] == 1
    assert len(report["findings"]) == 2
    assert report["severity_breakdown"]["critical"] == 1
    assert report["severity_breakdown"]["high"] == 1
    assert report["risk_score"] == 8.5  # (10 + 7) / 2
