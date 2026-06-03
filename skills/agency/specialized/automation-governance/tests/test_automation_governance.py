"""CTs para Automation Governance Engine -- 4 testes criticos de governanca."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from automation_governance_engine import (
    RiskLevel, RuleAction, GovernanceRule, ApprovalStep,
    ApprovalChain, GovernanceEngine,
)


def test_ct1_rule_evaluation():
    """CT-01: Regras avaliam contexto e disparam acoes corretas."""
    rule = GovernanceRule(
        name="budget_limit",
        condition_field="amount",
        condition_operator=">",
        condition_value=10000,
        action=RuleAction.ESCALATE,
    )

    assert rule.evaluate({"amount": 50000}) is True
    assert rule.evaluate({"amount": 5000}) is False
    assert rule.evaluate({}) is False
    assert rule.is_blocking is True


def test_ct2_risk_assessment_pipeline():
    """CT-02: Pipeline de avaliacao de risco com multiplas regras."""
    engine = GovernanceEngine()
    engine.add_rule(GovernanceRule("high_value", "amount", ">", 50000, RuleAction.REJECT))
    engine.add_rule(GovernanceRule("sensitive_data", "data_type", "==", "PII", RuleAction.ESCALATE))
    engine.add_rule(GovernanceRule("new_vendor", "vendor_status", "==", "new", RuleAction.FLAG))

    risk, triggered = engine.assess_risk({"amount": 2000, "data_type": "PII", "vendor_status": "new"})
    assert risk == RiskLevel.HIGH
    assert "sensitive_data" in triggered
    assert "new_vendor" in triggered

    risk, triggered = engine.assess_risk({"amount": 100000, "data_type": "logs"})
    assert risk == RiskLevel.CRITICAL
    assert "high_value" in triggered


def test_ct3_approval_chain_validation():
    """CT-03: Validacao de cadeia de aprovacao verifica roles obrigatorios."""
    chain = ApprovalChain(
        name="procurement",
        steps=[
            ApprovalStep(role="manager", required=True),
            ApprovalStep(role="finance", required=True),
            ApprovalStep(role="compliance", required=True),
            ApprovalStep(role="legal", required=False),
        ],
    )

    assert chain.mandatory_steps == 3
    assert chain.step_count == 4

    ok, missing = chain.validate_completion({"manager", "finance", "compliance"})
    assert ok is True
    assert missing == []

    ok, missing = chain.validate_completion({"manager"})
    assert ok is False
    assert "finance" in missing
    assert "compliance" in missing

    ok, missing = chain.validate_completion({"manager", "finance", "compliance", "legal"})
    assert ok is True


def test_ct4_end_to_end_governance():
    """CT-04: Validacao completa de automacao com risco e aprovacao."""
    engine = GovernanceEngine()
    engine.add_rule(GovernanceRule("pii_check", "contains_pii", "==", True, RuleAction.ESCALATE))
    engine.add_rule(GovernanceRule("budget_cap", "budget", ">", 100000, RuleAction.REJECT))
    engine.add_chain(ApprovalChain("deploy", [
        ApprovalStep(role="dev_lead", required=True),
        ApprovalStep(role="sec_ops", required=True),
    ]))

    result = engine.validate_automation(
        context={"contains_pii": False, "budget": 50000},
        chain_name="deploy",
        completed_roles={"dev_lead", "sec_ops"},
    )
    assert result["risk_level"] == "low"
    assert result["can_proceed"] is True

    result = engine.validate_automation(
        context={"contains_pii": True, "budget": 50000},
        chain_name="deploy",
        completed_roles={"dev_lead"},
    )
    assert result["risk_level"] == "high"
    assert result["can_proceed"] is False
    assert "sec_ops" in result["missing_approvals"]

    result = engine.validate_automation(
        context={"contains_pii": False, "budget": 200000},
        chain_name="deploy",
        completed_roles={"dev_lead", "sec_ops"},
    )
    assert result["risk_level"] == "critical"
    assert result["can_proceed"] is False
