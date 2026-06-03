"""Workflow Architect Engine -- Workflow tree mapping with handoff contracts."""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field


class StepOutcome(Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    VALIDATION_ERROR = "validation_error"
    CONFLICT = "conflict"


@dataclass
class HandoffContract:
    source: str
    target: str
    endpoint: str
    payload_schema: dict
    success_response: dict
    timeout_seconds: int = 30

    @property
    def is_rest(self) -> bool:
        return self.endpoint.startswith("POST") or self.endpoint.startswith("GET")

    @property
    def schema_keys(self) -> set:
        return set(self.payload_schema.keys())


@dataclass
class Step:
    name: str
    actor: str
    action: str
    timeout_seconds: int = 30
    outcomes: dict[StepOutcome, str] = field(default_factory=dict)
    cleanup: list[str] = field(default_factory=list)

    @property
    def has_failure_path(self) -> bool:
        return (StepOutcome.FAILURE in self.outcomes or
                StepOutcome.TIMEOUT in self.outcomes or
                StepOutcome.VALIDATION_ERROR in self.outcomes)

    @property
    def requires_cleanup(self) -> bool:
        return len(self.cleanup) > 0


@dataclass
class WorkflowTree:
    name: str
    version: str
    trigger: str
    steps: list[Step] = field(default_factory=list)
    handoffs: list[HandoffContract] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    @property
    def has_cleanup(self) -> bool:
        return any(s.requires_cleanup for s in self.steps)

    @property
    def covered_outcomes(self) -> dict:
        result: dict[str, int] = {}
        for step in self.steps:
            for outcome in step.outcomes:
                key = outcome.value
                result[key] = result.get(key, 0) + 1
        return result

    @property
    def is_complete(self) -> bool:
        for step in self.steps:
            if StepOutcome.SUCCESS not in step.outcomes:
                return False
        return len(self.steps) > 0

    def add_step(self, step: Step) -> None:
        self.steps.append(step)

    def add_handoff(self, handoff: HandoffContract) -> None:
        self.handoffs.append(handoff)

    def validate_handoffs(self) -> list[str]:
        errors = []
        names = {h.source for h in self.handoffs} | {h.target for h in self.handoffs}
        for step in self.steps:
            if step.actor not in names and self.steps:
                continue
        if not self.handoffs and len(self.steps) > 1:
            errors.append("Multi-step workflow sem contratos de handoff definidos")
        return errors
