"""Automation Governance Architect Engine -- Rule-based risk assessment and approval chains."""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field


_RISK_ORDER = {"low": 0, "medium": 1, "high": 2, "critical": 3}


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def order(self) -> int:
        return _RISK_ORDER[self.value]


class RuleAction(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    FLAG = "flag"
    ESCALATE = "escalate"


@dataclass
class GovernanceRule:
    name: str
    condition_field: str
    condition_operator: str
    condition_value: object
    action: RuleAction

    @property
    def is_blocking(self) -> bool:
        return self.action in (RuleAction.REJECT, RuleAction.ESCALATE)

    def evaluate(self, context: dict) -> bool:
        value = context.get(self.condition_field)
        if value is None:
            return False
        ops = {
            ">": lambda a, b: a > b,
            "<": lambda a, b: a < b,
            ">=": lambda a, b: a >= b,
            "<=": lambda a, b: a <= b,
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            "in": lambda a, b: a in b,
            "contains": lambda a, b: b in str(a),
        }
        op_func = ops.get(self.condition_operator)
        if op_func is None:
            return False
        try:
            return op_func(value, self.condition_value)
        except (TypeError, ValueError):
            return False


@dataclass
class ApprovalStep:
    role: str
    required: bool = True

    @property
    def is_mandatory(self) -> bool:
        return self.required


@dataclass
class ApprovalChain:
    name: str
    steps: list[ApprovalStep] = field(default_factory=list)

    @property
    def mandatory_steps(self) -> int:
        return sum(1 for s in self.steps if s.required)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    def validate_completion(self, completed_roles: set[str]) -> tuple[bool, list[str]]:
        missing = []
        for step in self.steps:
            if step.required and step.role not in completed_roles:
                missing.append(step.role)
        return len(missing) == 0, missing


@dataclass
class GovernanceEngine:
    rules: list[GovernanceRule] = field(default_factory=list)
    approval_chains: dict[str, ApprovalChain] = field(default_factory=dict)

    @property
    def rule_count(self) -> int:
        return len(self.rules)

    @property
    def chain_count(self) -> int:
        return len(self.approval_chains)

    def assess_risk(self, context: dict) -> tuple[RiskLevel, list[str]]:
        triggered = []
        max_risk = RiskLevel.LOW
        for rule in self.rules:
            if rule.evaluate(context):
                triggered.append(rule.name)
                if rule.action == RuleAction.REJECT:
                    return RiskLevel.CRITICAL, triggered
                if rule.action == RuleAction.ESCALATE and max_risk.order < RiskLevel.HIGH.order:
                    max_risk = RiskLevel.HIGH
                if rule.action == RuleAction.FLAG and max_risk.order < RiskLevel.MEDIUM.order:
                    max_risk = RiskLevel.MEDIUM
        return max_risk, triggered

    def add_rule(self, rule: GovernanceRule) -> None:
        self.rules.append(rule)

    def add_chain(self, chain: ApprovalChain) -> None:
        self.approval_chains[chain.name] = chain

    def evaluate_approval(self, chain_name: str, completed_roles: set[str]) -> tuple[bool, list[str]]:
        chain = self.approval_chains.get(chain_name)
        if chain is None:
            return False, [f"Cadeia '{chain_name}' nao encontrada"]
        return chain.validate_completion(completed_roles)

    def validate_automation(self, context: dict, chain_name: str, completed_roles: set[str]) -> dict:
        risk, triggered = self.assess_risk(context)
        approved, missing = self.evaluate_approval(chain_name, completed_roles)
        return {
            "risk_level": risk.value,
            "triggered_rules": triggered,
            "approval_approved": approved,
            "missing_approvals": missing,
            "can_proceed": risk != RiskLevel.CRITICAL and approved,
        }
