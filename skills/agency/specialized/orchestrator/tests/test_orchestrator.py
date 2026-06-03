"""CTs para Orchestrator Engine -- 4 testes criticos de pipeline."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from orchestrator_engine import Pipeline, Stage, Task, TaskState


def test_ct1_happy_path():
    """CT-01: Pipeline completo -- todas as tarefas passam sem retry."""
    results = []

    def success_action():
        results.append("ok")
        return True

    pipeline = Pipeline(
        name="Test Pipeline",
        stages=[
            Stage(name="Stage 1", tasks=[
                Task(name="Task 1.1", action=success_action),
                Task(name="Task 1.2", action=success_action),
            ]),
            Stage(name="Stage 2", tasks=[
                Task(name="Task 2.1", action=success_action),
            ]),
        ],
    )

    report = pipeline.run()

    assert report["passed"] == 3
    assert report["failed"] == 0
    assert report["pending"] == 0
    assert report["complete"] is True
    assert len(results) == 3


def test_ct2_retry_logic():
    """CT-02: Logica de retry -- tarefa falha 2x e passa na 3a tentativa."""
    attempts = []

    def flaky_action():
        attempts.append(1)
        return len(attempts) >= 3

    task = Task(name="Flaky Task", action=flaky_action, max_retries=3)
    stage = Stage(name="Retry Stage", tasks=[task])
    pipeline = Pipeline(name="Retry Test", stages=[stage])

    pipeline.run()

    assert task.state == TaskState.PASSED
    assert task.retry_count == 2
    assert len(attempts) == 3


def test_ct3_max_retries_exceeded():
    """CT-03: Tarefa excede max_retries e falha permanentemente."""
    def failing_action():
        return False

    task = Task(name="Failing Task", action=failing_action, max_retries=2)
    stage = Stage(name="Fail Stage", tasks=[task])
    pipeline = Pipeline(name="Fail Test", stages=[stage])

    report = pipeline.run()

    assert task.state == TaskState.FAILED
    assert task.retry_count == 2
    assert task.can_retry is False
    assert report["failed"] == 1
    assert report["complete"] is False


def test_ct4_pipeline_status_report():
    """CT-04: Relatorio de status reflete estado real do pipeline."""
    def pass_action():
        return True

    def fail_action():
        return False

    pipeline = Pipeline(
        name="Status Test",
        stages=[
            Stage(name="S1", tasks=[
                Task(name="Pass 1", action=pass_action),
                Task(name="Fail 1", action=fail_action, max_retries=0),
            ]),
            Stage(name="S2", tasks=[
                Task(name="Pass 2", action=pass_action),
            ]),
        ],
    )

    report = pipeline.run()

    assert report["pipeline"] == "Status Test"
    assert report["total_tasks"] == 3
    assert report["passed"] == 1
    assert report["failed"] == 1
    assert report["pending"] == 1
    assert report["current_stage"] == 0
    assert report["complete"] is False
