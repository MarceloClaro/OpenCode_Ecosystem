"""
Testes do TaskQueue (core/task_queue.py)

Cobre:
- start / stop
- enqueue com diferentes prioridades
- Execucao de tarefas (COMPLETED)
- Tarefas que falham (FAILED)
- cancel() de tarefa pendente
- get_task / get_tasks com filtro
- pending_count, running_count, is_running
- Prioridades: LOW, NORMAL, HIGH, CRITICAL
- Context manager (async with)
"""

import asyncio

import pytest

from core.task_queue import TaskQueue, TaskPriority, TaskStatus


@pytest.fixture
def queue():
    """TaskQueue com 2 workers."""
    q = TaskQueue(max_concurrent=2)
    return q


class TestTaskQueueLifecycle:
    """Testa ciclo de vida da fila."""

    @pytest.mark.asyncio
    async def test_start_and_stop(self, queue):
        assert queue.is_running is False
        await queue.start()
        assert queue.is_running is True
        assert queue.running_count == 0
        await queue.stop()
        assert queue.is_running is False

    @pytest.mark.asyncio
    async def test_double_start(self, queue):
        await queue.start()
        await queue.start()  # Nao deve crashar
        assert queue.is_running is True
        await queue.stop()

    @pytest.mark.asyncio
    async def test_context_manager(self, queue):
        async with queue:
            assert queue.is_running is True
        assert queue.is_running is False

    @pytest.mark.asyncio
    async def test_stop_cancels_pending(self, queue):
        await queue.start()
        # Enfileira tarefas que nunca executam (worker parado)
        for i in range(10):
            await queue.enqueue(f"task_{i}", lambda: asyncio.sleep(10))
        await queue.stop(cancel_pending=True)
        # Todas as pendentes devem estar CANCELLED
        cancelled = queue.get_tasks(status=TaskStatus.CANCELLED)
        assert len(cancelled) == 10


class TestTaskQueueExecution:
    """Testa execucao de tarefas."""

    @pytest.mark.asyncio
    async def test_simple_task(self, queue):
        async with queue:
            task_id = await queue.enqueue("simple", lambda: asyncio.sleep(0.01))
            await asyncio.sleep(0.05)
            task = queue.get_task(task_id)
            assert task is not None
            assert task.status == TaskStatus.COMPLETED
            assert task.name == "simple"

    @pytest.mark.asyncio
    async def test_task_with_result(self, queue):
        async def compute():
            await asyncio.sleep(0.01)
            return 42

        async with queue:
            task_id = await queue.enqueue("compute", compute)
            await asyncio.sleep(0.05)
            task = queue.get_task(task_id)
            assert task.status == TaskStatus.COMPLETED
            assert task.result == 42

    @pytest.mark.asyncio
    async def test_task_failure(self, queue):
        async def will_fail():
            await asyncio.sleep(0.01)
            raise ValueError("ops")

        async with queue:
            task_id = await queue.enqueue("failing", will_fail)
            await asyncio.sleep(0.05)
            task = queue.get_task(task_id)
            assert task.status == TaskStatus.FAILED
            assert task.error is not None
            assert "ValueError" in task.error

    @pytest.mark.asyncio
    async def test_multiple_tasks(self, queue):
        results = []

        async def worker(n):
            await asyncio.sleep(0.01)
            results.append(n)

        async with queue:
            ids = []
            for i in range(5):
                tid = await queue.enqueue(f"w{i}", lambda n=i: worker(n))
                ids.append(tid)
            await asyncio.sleep(0.1)
            assert len(results) == 5
            assert sorted(results) == [0, 1, 2, 3, 4]


class TestTaskQueuePriorities:
    """Testa ordenacao por prioridade."""

    @pytest.mark.asyncio
    async def test_priority_order(self, queue):
        execution_order = []

        async def make_task(n):
            async def task():
                execution_order.append(n)
                await asyncio.sleep(0.01)
            return task

        async with queue:
            await queue.enqueue("low", await make_task(1), priority=TaskPriority.LOW)
            await queue.enqueue("high", await make_task(2), priority=TaskPriority.HIGH)
            await queue.enqueue("critical", await make_task(3), priority=TaskPriority.CRITICAL)
            await queue.enqueue("normal", await make_task(4), priority=TaskPriority.NORMAL)
            await asyncio.sleep(0.1)

        # CRITICAL deve executar primeiro, depois HIGH, NORMAL, LOW
        assert execution_order[0] == 3  # CRITICAL

    @pytest.mark.asyncio
    async def test_priority_enum_values(self):
        assert TaskPriority.LOW.value == 0
        assert TaskPriority.NORMAL.value == 50
        assert TaskPriority.HIGH.value == 100
        assert TaskPriority.CRITICAL.value == 200


class TestTaskQueueManagement:
    """Testa gerenciamento de tarefas."""

    @pytest.mark.asyncio
    async def test_cancel_pending_task(self, queue):
        async with queue:
            task_id = await queue.enqueue("cancelable", lambda: asyncio.sleep(10))
            assert queue.cancel(task_id) is True
            task = queue.get_task(task_id)
            assert task.status == TaskStatus.CANCELLED

    @pytest.mark.asyncio
    async def test_cancel_running_task(self, queue):
        """Cancelar tarefa em execucao nao tem efeito (so PENDING)."""
        async with queue:
            task_id = await queue.enqueue("quick", lambda: asyncio.sleep(0.01))
            await asyncio.sleep(0.02)
            # Ja completou, cancel deve retornar False
            assert queue.cancel(task_id) is False

    @pytest.mark.asyncio
    async def test_get_tasks_filter_by_status(self, queue):
        async with queue:
            await queue.enqueue("a", lambda: asyncio.sleep(0.01))
            await queue.enqueue("b", lambda: asyncio.sleep(0.01))
            await asyncio.sleep(0.05)
            completed = queue.get_tasks(status=TaskStatus.COMPLETED)
            assert len(completed) == 2

    @pytest.mark.asyncio
    async def test_counts(self, queue):
        assert queue.pending_count == 0
        async with queue:
            await queue.enqueue("a", lambda: asyncio.sleep(10))
            assert queue.pending_count == 1


class TestTaskQueueEdgeCases:
    """Casos extremos."""

    @pytest.mark.asyncio
    async def test_get_nonexistent_task(self, queue):
        task = queue.get_task("nonexistent")
        assert task is None

    @pytest.mark.asyncio
    async def test_task_timing(self, queue):
        async with queue:
            tid = await queue.enqueue("timed", lambda: asyncio.sleep(0.01))
            await asyncio.sleep(0.05)
            task = queue.get_task(tid)
            assert task.created_at is not None
            assert task.started_at is not None
            assert task.completed_at is not None
            assert task.started_at >= task.created_at
            assert task.completed_at >= task.started_at
