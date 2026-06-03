"""CTs para Workflow Architect Engine -- 4 testes criticos de arvore de workflow."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from workflow_architect_engine import Step, StepOutcome, HandoffContract, WorkflowTree


def test_ct1_workflow_completeness_check():
    """CT-01: Workflow incompleto detectado quando passo sem success path."""
    tree = WorkflowTree(
        name="User Signup",
        version="1.0",
        trigger="POST /auth/register",
        steps=[
            Step(
                name="Validate Input",
                actor="API Gateway",
                action="Validar payload e CSRF token",
                outcomes={
                    StepOutcome.SUCCESS: "STEP 2",
                    StepOutcome.VALIDATION_ERROR: "Return 400",
                },
            ),
            Step(
                name="Create User",
                actor="Auth Service",
                action="Inserir usuario no banco",
                outcomes={
                    StepOutcome.FAILURE: "ABORT_CLEANUP",
                },
            ),
        ],
    )

    assert tree.step_count == 2
    assert tree.is_complete is False  # Step 2 lacks success path
    assert tree.has_cleanup is False


def test_ct2_handoff_contract_validation():
    """CT-02: Contratos de handoff validam schemas e endpoints."""
    handoff = HandoffContract(
        source="API Gateway",
        target="Auth Service",
        endpoint="POST /api/v1/auth/register",
        payload_schema={"email": "str", "password": "str", "name": "str"},
        success_response={"user_id": "str", "token": "str"},
        timeout_seconds=10,
    )

    assert handoff.is_rest is True
    assert handoff.schema_keys == {"email", "password", "name"}
    assert handoff.timeout_seconds == 10


def test_ct3_full_workflow_tree():
    """CT-03: Arvore de workflow completa com todos os branches."""
    tree = WorkflowTree(
        name="Order Checkout",
        version="2.1",
        trigger="POST /orders/checkout",
        steps=[
            Step(
                name="Validate Cart",
                actor="Order Service",
                action="Verificar itens e estoque",
                timeout_seconds=5,
                outcomes={
                    StepOutcome.SUCCESS: "STEP 2",
                    StepOutcome.VALIDATION_ERROR: "Return 400",
                    StepOutcome.TIMEOUT: "Retry x2, then ABORT",
                },
                cleanup=["Revert stock reservation"],
            ),
            Step(
                name="Process Payment",
                actor="Payment Service",
                action="Capturar pagamento via gateway",
                timeout_seconds=30,
                outcomes={
                    StepOutcome.SUCCESS: "STEP 3",
                    StepOutcome.FAILURE: "ABORT_CLEANUP",
                    StepOutcome.TIMEOUT: "Flag para revisao manual",
                },
                cleanup=["Void payment authorization"],
            ),
            Step(
                name="Confirm Order",
                actor="Order Service",
                action="Marcar pedido como confirmado",
                outcomes={
                    StepOutcome.SUCCESS: "COMPLETE",
                    StepOutcome.CONFLICT: "Return 409",
                },
            ),
        ],
        handoffs=[
            HandoffContract("Order Service", "Payment Service", "POST /payments/capture", {"order_id": "str", "amount": "float"}, {"payment_id": "str"}, 30),
            HandoffContract("Payment Service", "Order Service", "POST /orders/confirm", {"order_id": "str", "payment_id": "str"}, {"status": "str"}, 10),
        ],
    )

    assert tree.step_count == 3
    assert tree.is_complete is True
    assert tree.has_cleanup is True
    assert len(tree.handoffs) == 2

    outcomes = tree.covered_outcomes
    assert outcomes["success"] == 3
    assert "failure" in outcomes
    assert "timeout" in outcomes


def test_ct4_missing_handoff_detection():
    """CT-04: Workflow multi-step sem handoffs gera aviso."""
    tree = WorkflowTree(
        name="Data Pipeline",
        version="1.0",
        trigger="Cron Job",
        steps=[
            Step(name="Extract", actor="ETL Service", action="Extrair dados", outcomes={StepOutcome.SUCCESS: "STEP 2"}),
            Step(name="Transform", actor="ETL Service", action="Transformar dados", outcomes={StepOutcome.SUCCESS: "STEP 3"}),
            Step(name="Load", actor="DB Service", action="Carregar dados", outcomes={StepOutcome.SUCCESS: "COMPLETE"}),
        ],
    )

    errors = tree.validate_handoffs()
    assert len(errors) > 0
