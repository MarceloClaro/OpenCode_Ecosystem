"""Compliance Auditor Engine -- Gap assessment, control tracking, evidence management."""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime


class Severity(Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ControlStatus(Enum):
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    NOT_APPLICABLE = "not_applicable"


@dataclass
class Finding:
    control_id: str
    severity: Severity
    description: str
    remediation: str
    status: ControlStatus = ControlStatus.NON_COMPLIANT
    evidence: list[str] = field(default_factory=list)
    remediation_deadline: datetime | None = None

    @property
    def is_critical(self) -> bool:
        return self.severity == Severity.CRITICAL

    @property
    def has_evidence(self) -> bool:
        return len(self.evidence) > 0

    @property
    def is_resolved(self) -> bool:
        return self.status == ControlStatus.COMPLIANT


@dataclass
class Control:
    control_id: str
    domain: str
    description: str
    status: ControlStatus = ControlStatus.NON_COMPLIANT
    findings: list[Finding] = field(default_factory=list)

    @property
    def open_findings(self) -> list[Finding]:
        return [f for f in self.findings if not f.is_resolved]

    @property
    def critical_count(self) -> int:
        return sum(1 for f in self.findings if f.is_critical)

    @property
    def severity_score(self) -> int:
        weights = {Severity.CRITICAL: 10, Severity.HIGH: 7, Severity.MEDIUM: 4, Severity.LOW: 2}
        return sum(weights.get(f.severity, 0) for f in self.open_findings)


@dataclass
class ComplianceFramework:
    name: str
    version: str
    controls: list[Control] = field(default_factory=list)

    @property
    def total_controls(self) -> int:
        return len(self.controls)

    @property
    def compliant_controls(self) -> int:
        return sum(1 for c in self.controls if c.status == ControlStatus.COMPLIANT)

    @property
    def readiness_score(self) -> float:
        if not self.controls:
            return 100.0
        applicable = [c for c in self.controls if c.status != ControlStatus.NOT_APPLICABLE]
        if not applicable:
            return 100.0
        compliant = sum(1 for c in applicable if c.status == ControlStatus.COMPLIANT)
        return round((compliant / len(applicable)) * 100, 1)

    @property
    def total_open_findings(self) -> int:
        return sum(len(c.open_findings) for c in self.controls)

    @property
    def risk_summary(self) -> dict:
        findings = [f for c in self.controls for f in c.findings if not f.is_resolved]
        return {
            "critical": sum(1 for f in findings if f.severity == Severity.CRITICAL),
            "high": sum(1 for f in findings if f.severity == Severity.HIGH),
            "medium": sum(1 for f in findings if f.severity == Severity.MEDIUM),
            "low": sum(1 for f in findings if f.severity == Severity.LOW),
            "total": len(findings),
        }

    def add_evidence(self, control_id: str, finding_desc: str, evidence: str) -> bool:
        for control in self.controls:
            if control.control_id == control_id:
                for finding in control.findings:
                    if finding.description == finding_desc:
                        finding.evidence.append(evidence)
                        return True
        return False
