"""
core/task_queue.py — Fila de Tarefas Assíncronas com Prioridade e DI.

Gerencia execução concorrente de tarefas com suporte a:
- Prioridades (LOW, NORMAL, HIGH, CRITICAL)
- Concorrência limitada (max_concurrent)
- Status tracking (PENDING → RUNNING → COMPLETED/FAILED)
- Worker pool automatizado
- Integração com IEventBus (publica eventos de tarefa)

Uso com DI (novo):
    container = Container.instance()
    queue = TaskQueue(container=container, max_concurrent=4)
    await queue.start()
    task_id = await queue.enqueue("processar", minha_coro)
    await queue.stop()

Uso legado (compatível):
    queue = TaskQueue(max_concurrent=4)
    await queue.start()
    task_id = await queue.enqueue("processar", minha_coro)
"""

from __future__ import annotations

import asyncio
import enum
import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Optional
from core.interfaces import ITaskQueue

logger = logging.getLogger(__name__)


class TaskPriority(enum.IntEnum):
    """Níveis de prioridade para tarefas."""
    LOW = 0
    NORMAL = 50
    HIGH = 100
    CRITICAL = 200


class TaskStatus(enum.Enum):
    """Estados possíveis de uma tarefa."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Representa uma tarefa na fila.

    Attributes:
        id: Identificador único (12 hex chars).
        name: Nome descritivo da tarefa.
        priority: Nível de prioridade.
        status: Estado atual.
        created_at: Timestamp de criação.
        started_at: Timestamp de início da execução.
        completed_at: Timestamp de conclusão.
        error: Mensagem de erro se falhou.
        result: Valor retornado pela corotina.
    """
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    name: str = ""
    priority: TaskPriority = TaskPriority.NORMAL
    status: TaskStatus = TaskStatus.PENDING
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    error: Optional[str] = None
    result: Any = None


class TaskQueue(ITaskQueue):
    """Fila de tarefas assíncronas com worker pool e suporte a DI.

    Args:
        max_concurrent: Número máximo de workers simultâneos.
        container: Container DI opcional para resolver event_bus.
        on_task_complete: Callback opcional invoked em cada tarefa completada.
    """

    def __init__(
        self,
        max_concurrent: int = 4,
        container: Any = None,
        on_task_complete: Optional[Callable[[str, Any], None]] = None,
    ) -> None:
        self._max_concurrent = max_concurrent
        self._container = container
        self._on_task_complete = on_task_complete
        self._queue: asyncio.PriorityQueue[tuple[int, str, Callable[[], Coroutine]]] = (
            asyncio.PriorityQueue()
        )
        self._tasks: dict[str, Task] = {}
        self._workers: list[asyncio.Task[None]] = []
        self._running = False

        if container is not None and not container.is_registered('task_queue'):
            container.register('task_queue', self)

    async def start(self) -> None:
        """Inicia o worker pool."""
        if self._running:
            logger.warning("TaskQueue already running")
            return
        self._running = True
        for i in range(self._max_concurrent):
            worker = asyncio.create_task(self._worker_loop(i))
            self._workers.append(worker)
        logger.info("TaskQueue started with %d workers", self._max_concurrent)

    async def stop(self, cancel_pending: bool = False) -> None:
        """Para o worker pool.

        Args:
            cancel_pending: Se True, cancela tarefas pendentes.
        """
        self._running = False
        for w in self._workers:
            w.cancel()
        await asyncio.gather(*self._workers, return_exceptions=True)
        self._workers.clear()

        if cancel_pending:
            while not self._queue.empty():
                try:
                    _, task_id, _ = self._queue.get_nowait()
                    if task_id in self._tasks:
                        self._tasks[task_id].status = TaskStatus.CANCELLED
                except asyncio.QueueEmpty:
                    break

        logger.info("TaskQueue stopped")

    async def enqueue(
        self,
        name: str,
        coro_fn: Callable[[], Coroutine[Any, Any, Any]],
        priority: TaskPriority = TaskPriority.NORMAL,
    ) -> str:
        """Adiciona uma tarefa à fila.

        Args:
            name: Nome descritivo.
            coro_fn: Função assíncrona a executar (sem args).
            priority: Prioridade da tarefa.

        Returns:
            ID da tarefa criada.
        """
        task = Task(name=name, priority=priority)
        self._tasks[task.id] = task
        # Prioridade negativa: asyncio.PriorityQueue ordena do menor para o maior
        await self._queue.put((-priority.value, task.id, coro_fn))
        logger.debug("Enqueued task %s (%s) at priority %s", task.id[:8], name, priority.name)
        return task.id

    def get_task(self, task_id: str) -> Optional[Task]:
        """Retorna uma tarefa pelo ID."""
        return self._tasks.get(task_id)

    def get_tasks(self, status: Optional[TaskStatus] = None) -> list[Task]:
        """Lista tarefas, opcionalmente filtradas por status."""
        if status:
            return [t for t in self._tasks.values() if t.status == status]
        return list(self._tasks.values())

    def cancel(self, task_id: str) -> bool:
        """Cancela uma tarefa pendente."""
        task = self._tasks.get(task_id)
        if task and task.status == TaskStatus.PENDING:
            task.status = TaskStatus.CANCELLED
            return True
        return False

    @property
    def pending_count(self) -> int:
        return self._queue.qsize()

    @property
    def running_count(self) -> int:
        return sum(1 for t in self._tasks.values() if t.status == TaskStatus.RUNNING)

    @property
    def is_running(self) -> bool:
        return self._running

    # --- Interno ---

    async def _worker_loop(self, worker_id: int) -> None:
        """Loop principal do worker."""
        logger.debug("Worker %d started", worker_id)
        while self._running:
            try:
                _, task_id, coro_fn = await asyncio.wait_for(
                    self._queue.get(), timeout=1.0
                )
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break

            task = self._tasks.get(task_id)
            if task is None or task.status == TaskStatus.CANCELLED:
                continue

            task.status = TaskStatus.RUNNING
            task.started_at = time.time()

            # Publica evento de inicio se event_bus disponivel
            try:
                eb = self._container.resolve('event_bus') if self._container else None
                if eb:
                    await eb.publish('task.started', {'task_id': task.id, 'name': task.name})
            except Exception:
                pass

            try:
                result = await coro_fn()
                task.status = TaskStatus.COMPLETED
                task.result = result
                logger.debug("Task %s (%s) completed", task.id[:8], task.name)

                if self._on_task_complete:
                    self._on_task_complete(task.id, task.result)
                try:
                    eb = self._container.resolve('event_bus') if self._container else None
                    if eb:
                        await eb.publish('task.completed', {'task_id': task.id, 'name': task.name, 'result': result})
                except Exception:
                    pass

            except asyncio.CancelledError:
                task.status = TaskStatus.CANCELLED
            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = f"{type(e).__name__}: {e}"
                logger.error("Task %s (%s) failed: %s", task.id[:8], task.name, e)
                try:
                    eb = self._container.resolve('event_bus') if self._container else None
                    if eb:
                        await eb.publish('task.failed', {'task_id': task.id, 'name': task.name, 'error': task.error})
                except Exception:
                    pass
            finally:
                task.completed_at = time.time()

        logger.debug("Worker %d stopped", worker_id)

    async def __aenter__(self) -> TaskQueue:
        await self.start()
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.stop()
