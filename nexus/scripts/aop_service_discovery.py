#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent Orchestration Protocol (AOP) - Service Discovery and Task Queue
"""
import asyncio, logging, time, uuid
from enum import Enum
from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from collections import defaultdict

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class QueuedTask:
    task_id: str
    agent_name: str
    input_data: Any
    status: TaskStatus = TaskStatus.PENDING
    priority: int = 0
    retries: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    result: Optional[Any] = None
    error: Optional[str] = None

@dataclass
class AgentRegistration:
    name: str
    description: str
    handler: Callable
    max_workers: int = 1
    timeout: int = 60
    queue_enabled: bool = True
    max_queue_size: int = 1000

class TaskQueue:
    def __init__(self, max_workers=1, processing_timeout=60, retry_delay=1.0):
        self.max_workers = max_workers
        self.processing_timeout = processing_timeout
        self.retry_delay = retry_delay
        self.tasks = []
        self.task_map = {}
        self.active_workers = 0

    def enqueue(self, task):
        self.tasks.append(task)
        self.task_map[task.task_id] = task
        self.tasks.sort(key=lambda t: t.priority, reverse=True)
        return task.task_id

    def dequeue(self):
        for i, task in enumerate(self.tasks):
            if task.status == TaskStatus.PENDING:
                task.status = TaskStatus.PROCESSING
                task.started_at = time.time()
                self.tasks.pop(i)
                return task
        return None

    def get_stats(self):
        stats = defaultdict(int)
        for task in self.tasks:
            stats[task.status.value] += 1
        return {"total_queued": len(self.tasks), "status_counts": dict(stats),
                "active_workers": self.active_workers, "max_workers": self.max_workers}

class AOPServer:
    def __init__(self, server_name, description="AOP Agent Server", port=8000,
                 verbose=False, queue_enabled=True, max_workers_per_agent=1,
                 max_queue_size_per_agent=1000, processing_timeout=60, retry_delay=1.0):
        self.server_name = server_name
        self.description = description
        self.port = port
        self.verbose = verbose
        self.queue_enabled = queue_enabled
        self.max_workers_per_agent = max_workers_per_agent
        self.max_queue_size_per_agent = max_queue_size_per_agent
        self.processing_timeout = processing_timeout
        self.retry_delay = retry_delay
        self.agents = {}
        self.queues = {}
        self.task_history = []

    def add_agent(self, name, description, handler, max_workers=None, timeout=60, max_retries=3):
        max_workers = max_workers or self.max_workers_per_agent
        self.agents[name] = AgentRegistration(name=name, description=description,
            handler=handler, max_workers=max_workers, timeout=timeout)
        if self.queue_enabled:
            self.queues[name] = TaskQueue(max_workers=max_workers,
                processing_timeout=timeout, retry_delay=self.retry_delay)

    def add_agents_batch(self, agents):
        for ad in agents:
            self.add_agent(name=ad["name"], description=ad.get("description", ""),
                handler=ad["handler"], max_workers=ad.get("max_workers"),
                timeout=ad.get("timeout", 60))

    def submit_task(self, agent_name, input_data, priority=0, max_retries=3):
        if agent_name not in self.agents:
            raise ValueError(f"Agent not found: {agent_name}")
        task = QueuedTask(task_id=str(uuid.uuid4()), agent_name=agent_name,
            input_data=input_data, priority=priority, max_retries=max_retries)
        if self.queue_enabled:
            queue = self.queues[agent_name]
            if len(queue.tasks) >= self.max_queue_size_per_agent:
                raise ValueError(f"Queue full for agent {agent_name}")
            queue.enqueue(task)
        else:
            task.status = TaskStatus.PROCESSING
            task.started_at = time.time()
            try:
                task.result = self.agents[agent_name].handler(input_data)
                task.status = TaskStatus.COMPLETED
                task.completed_at = time.time()
            except Exception as e:
                task.error = str(e)
                task.status = TaskStatus.FAILED
                task.completed_at = time.time()
        self.task_history.append(task)
        return task.task_id

    def get_task_status(self, task_id):
        for task in self.task_history:
            if task.task_id == task_id:
                return {"task_id": task.task_id, "agent_name": task.agent_name,
                    "status": task.status.value, "priority": task.priority,
                    "retries": task.retries, "result": task.result, "error": task.error}
        return None

    def get_server_stats(self):
        return {"server_name": self.server_name, "registered_agents": len(self.agents),
                "total_tasks": len(self.task_history)}

    def discover_agents(self):
        return [{"name": reg.name, "description": reg.description,
                "max_workers": reg.max_workers, "timeout": reg.timeout,
                "queue_enabled": self.queue_enabled} for reg in self.agents.values()]
