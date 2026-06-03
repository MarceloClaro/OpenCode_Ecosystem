"""Blockchain Security Auditor Engine -- Smart contract vulnerability detection."""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field


class VulnSeverity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass
class Vulnerability:
    vuln_id: str
    title: str
    severity: VulnSeverity
    description: str
    affected_lines: list[int] = field(default_factory=list)
    recommendation: str = ""

    @property
    def is_critical_or_high(self) -> bool:
        return self.severity in (VulnSeverity.CRITICAL, VulnSeverity.HIGH)

    @property
    def risk_score(self) -> int:
        scores = {
            VulnSeverity.CRITICAL: 10,
            VulnSeverity.HIGH: 7,
            VulnSeverity.MEDIUM: 4,
            VulnSeverity.LOW: 2,
            VulnSeverity.INFO: 0,
        }
        return scores.get(self.severity, 0)

    @property
    def needs_immediate_action(self) -> bool:
        return self.severity == VulnSeverity.CRITICAL


@dataclass
class ContractAudit:
    contract_name: str
    contract_address: str = ""
    language: str = "solidity"
    vulnerabilities: list[Vulnerability] = field(default_factory=list)

    @property
    def total_findings(self) -> int:
        return len(self.vulnerabilities)

    @property
    def critical_count(self) -> int:
        return sum(1 for v in self.vulnerabilities if v.severity == VulnSeverity.CRITICAL)

    @property
    def aggregate_risk_score(self) -> float:
        if not self.vulnerabilities:
            return 0.0
        return round(sum(v.risk_score for v in self.vulnerabilities) / len(self.vulnerabilities), 1)

    @property
    def severity_breakdown(self) -> dict[str, int]:
        result: dict[str, int] = {}
        for v in self.vulnerabilities:
            result[v.severity.value] = result.get(v.severity.value, 0) + 1
        return result

    @property
    def is_safe(self) -> bool:
        return all(v.severity in (VulnSeverity.LOW, VulnSeverity.INFO) for v in self.vulnerabilities)

    def add_finding(self, vuln: Vulnerability) -> None:
        self.vulnerabilities.append(vuln)

    def generate_report(self) -> dict:
        return {
            "contract": self.contract_name,
            "address": self.contract_address,
            "language": self.language,
            "total_findings": self.total_findings,
            "critical": self.critical_count,
            "risk_score": self.aggregate_risk_score,
            "severity_breakdown": self.severity_breakdown,
            "findings": [
                {
                    "id": v.vuln_id,
                    "title": v.title,
                    "severity": v.severity.value,
                    "risk_score": v.risk_score,
                }
                for v in self.vulnerabilities
            ],
        }


KNOWN_PATTERNS: dict[str, dict] = {
    "reentrancy": {
        "severity": VulnSeverity.CRITICAL,
        "title": "Reentrancy Attack",
        "description": "External call antes de atualizacao de estado -- vulneravel a reentrancia",
        "recommendation": "Seguir padrao Checks-Effects-Interactions ou usar ReentrancyGuard",
    },
    "unchecked_call": {
        "severity": VulnSeverity.HIGH,
        "title": "Unchecked External Call",
        "description": "Chamada externa sem verificacao de retorno",
        "recommendation": "Verificar valor de retorno da chamada externa",
    },
    "overflow": {
        "severity": VulnSeverity.MEDIUM,
        "title": "Integer Overflow/Underflow",
        "description": "Operacao aritmetica sem protecao contra overflow",
        "recommendation": "Usar SafeMath ou Solidity >=0.8.0",
    },
    "tx_origin": {
        "severity": VulnSeverity.HIGH,
        "title": "tx.origin Authentication",
        "description": "Uso de tx.origin para autenticacao -- vulneravel a phishing",
        "recommendation": "Substituir tx.origin por msg.sender",
    },
    "timestamp": {
        "severity": VulnSeverity.LOW,
        "title": "Block Timestamp Manipulation",
        "description": "Dependencia de block.timestamp para logica critica",
        "recommendation": "Evitar block.timestamp para aleatoriedade ou logica de valor",
    },
}


PATTERN_HEURISTICS: dict[str, list[str]] = {
    "reentrancy": [".call{value:", ".call{ value:", "msg.sender.call"],
    "unchecked_call": ["address.call(", ".call("],
    "overflow": [" + ", " - ", " * ", " / "],
    "tx_origin": ["tx.origin"],
    "timestamp": ["block.timestamp", "now"],
}


def scan_patterns(contract_name: str, code: str) -> ContractAudit:
    audit = ContractAudit(contract_name=contract_name)
    code_lower = code.lower()
    for i, (pattern_key, pattern_data) in enumerate(KNOWN_PATTERNS.items()):
        heuristics = PATTERN_HEURISTICS.get(pattern_key, [])
        matched = False
        for h in heuristics:
            if h.lower() in code_lower:
                matched = True
                break
        if matched:
            audit.add_finding(Vulnerability(
                vuln_id=f"BSA-{i + 1:03d}",
                title=pattern_data["title"],
                severity=pattern_data["severity"],
                description=pattern_data["description"],
                recommendation=pattern_data["recommendation"],
            ))
    return audit
