"""Orchestrator Engine -- Pipeline task management with state machine and retry logic."""

from __future__ import annotations

from enum import Enum
from dataclasses import dataclass, field
from typing import Callable


class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class Task:
    name: str
    action: Callable[[], bool]
    retry_count: int = 0
    max_retries: int = 3
    state: TaskState = TaskState.PENDING
    error_message: str = ""

    @property
    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries

    @property
    def is_terminal(self) -> bool:
        return self.state in (TaskState.PASSED, TaskState.FAILED, TaskState.SKIPPED)


@dataclass
class Stage:
    name: str
    tasks: list[Task] = field(default_factory=list)

    @property
    def all_passed(self) -> bool:
        return all(t.state == TaskState.PASSED for t in self.tasks)

    @property
    def has_failures(self) -> bool:
        return any(t.state == TaskState.FAILED for t in self.tasks)


@dataclass
class Pipeline:
    name: str
    stages: list[Stage] = field(default_factory=list)

    @property
    def current_stage_index(self) -> int:
        for i, stage in enumerate(self.stages):
            if not stage.all_passed:
                return i
        return len(self.stages)

    @property
    def is_complete(self) -> bool:
        return all(s.all_passed for s in self.stages)

    @property
    def status_report(self) -> dict:
        total = sum(len(s.tasks) for s in self.stages)
        passed = sum(1 for s in self.stages for t in s.tasks if t.state == TaskState.PASSED)
        failed = sum(1 for s in self.stages for t in s.tasks if t.state == TaskState.FAILED)
        pending = sum(1 for s in self.stages for t in s.tasks if t.state == TaskState.PENDING)
        return {
            "pipeline": self.name,
            "total_tasks": total,
            "passed": passed,
            "failed": failed,
            "pending": pending,
            "complete": self.is_complete,
            "current_stage": self.current_stage_index,
        }

    def execute_task(self, task: Task) -> None:
        task.state = TaskState.RUNNING
        try:
            success = task.action()
        except Exception as exc:
            success = False
            task.error_message = str(exc)

        if success:
            task.state = TaskState.PASSED
        else:
            task.retry_count += 1
            if task.can_retry:
                task.state = TaskState.PENDING
            else:
                task.state = TaskState.FAILED

    def run(self) -> dict:
        for stage in self.stages:
            for task in stage.tasks:
                while task.state in (TaskState.PENDING, TaskState.RUNNING):
                    self.execute_task(task)
                    if task.state == TaskState.FAILED:
                        break
                if stage.has_failures:
                    break
            if stage.has_failures:
                break
        return self.status_report
