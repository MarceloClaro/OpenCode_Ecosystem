# -*- coding: utf-8 -*-
"""
nexus/scripts/mcp_router.py (refatorado) - DI via Container.
Mantém API original inalterada para compatibilidade retroativa.
"""

import json
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from core.container import Container

from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timezone


class MCPCapability(Enum):
    FILESYSTEM = "filesystem"
    WEB_SEARCH = "web_search"
    DATABASE = "database"
    CODE_EXECUTION = "code_execution"
    LLM_INFERENCE = "llm_inference"
    MEMORY = "memory"
    NOTIFICATION = "notification"
    CUSTOM = "custom"


class AgentSpecialization(Enum):
    EMBEDDING = "A1"
    ATTENTION = "A2"
    CONSENSUS = "A3"
    FEED_FORWARD = "A4"
    ARCHITECTURE = "A5"
    QA = "A6"
    INTEGRATION = "A7"
    EVOLUTION = "A8"


@dataclass
class MCPServer:
    id: str
    name: str
    capabilities: List[MCPCapability]
    endpoint: str
    max_concurrent_tasks: int
    current_load: int = 0
    health_score: float = 1.0
    last_heartbeat: str = ""

    def is_available(self) -> bool:
        return (
            self.health_score > 0.5 and
            self.current_load < self.max_concurrent_tasks
        )

    def can_handle(self, capabilities: List[MCPCapability]) -> bool:
        return all(cap in self.capabilities for cap in capabilities)


@dataclass
class TaskDescriptor:
    id: str
    agent_id: str
    phase: str
    required_capabilities: List[MCPCapability]
    priority: int = 1
    estimated_duration_ms: int = 0
    dependencies: List[str] = None  # type: ignore[assignment]
    context: Dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.context is None:
            self.context = {}


@dataclass
class RoutingDecision:
    task_id: str
    mcp_server_id: str
    agent_id: str
    confidence: float
    rationale: str
    alternative_servers: List[str]
    sync_barrier_required: bool
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class MCPRouter:
    def __init__(self, container=None):
        self._container = container
        self.mcp_servers: Dict[str, MCPServer] = {}
        self.routing_history: List[RoutingDecision] = []
        self.agent_specializations = {spec.value: spec.name for spec in AgentSpecialization}

    @classmethod
    def from_container(cls, container: 'Container') -> 'MCPRouter':
        """Factory: cria MCPRouter resolvendo deps do Container."""
        return cls(container=container)

    def register_mcp(self, server: MCPServer) -> None:
        self.mcp_servers[server.id] = server

    def route_task(self, task: TaskDescriptor) -> RoutingDecision:
        capable_servers = [
            server for server in self.mcp_servers.values()
            if server.can_handle(task.required_capabilities) and server.is_available()
        ]

        if not capable_servers:
            raise RuntimeError(
                f"No available MCP servers for task {task.id} "
                f"requiring {[c.value for c in task.required_capabilities]}"
            )

        scores = []
        for server in capable_servers:
            score = self._score_server(server, task)
            scores.append((server, score))

        scores.sort(key=lambda x: x[1], reverse=True)
        best_server = scores[0][0]
        confidence = scores[0][1]

        sync_barrier_needed = self._needs_sync_barrier(task, best_server)

        alternative_servers = [s[0].id for s in scores[1:3]]
        decision = RoutingDecision(
            task_id=task.id,
            mcp_server_id=best_server.id,
            agent_id=task.agent_id,
            confidence=confidence,
            rationale=self._build_rationale(task, best_server, scores),
            alternative_servers=alternative_servers,
            sync_barrier_required=sync_barrier_needed
        )

        self.routing_history.append(decision)
        return decision

    def _score_server(self, server: MCPServer, task: TaskDescriptor) -> float:
        health_score = server.health_score * 0.4
        load_factor = (1.0 - (server.current_load / server.max_concurrent_tasks)) * 0.3
        agent_spec = self.agent_specializations.get(task.agent_id, "")
        spec_match = 0.2 if agent_spec in server.name.lower() else 0.1
        priority_boost = (task.priority / 5.0) * 0.1
        return health_score + load_factor + spec_match + priority_boost

    def _needs_sync_barrier(self, task: TaskDescriptor, server: MCPServer) -> bool:
        has_dependencies = len(task.dependencies) > 0
        is_critical = task.priority >= 4
        is_state_changing = MCPCapability.DATABASE in task.required_capabilities
        return has_dependencies or is_critical or is_state_changing

    def _build_rationale(
        self,
        task: TaskDescriptor,
        selected_server: MCPServer,
        all_scores: List[Tuple[MCPServer, float]]
    ) -> str:
        top_score = all_scores[0][1]
        second_score = all_scores[1][1] if len(all_scores) > 1 else 0
        return (
            f"Selected {selected_server.name} (score: {top_score:.2f}) for {task.phase} phase. "
            f"Health: {selected_server.health_score:.1%}, Load: {selected_server.current_load}/"
            f"{selected_server.max_concurrent_tasks}. "
            f"Margin over next option: {(top_score - second_score):.2f}. "
            f"Requires sync barrier: {self._needs_sync_barrier(task, selected_server)}"
        )

    def update_server_load(self, server_id: str, delta: int) -> None:
        if server_id in self.mcp_servers:
            self.mcp_servers[server_id].current_load = max(
                0,
                self.mcp_servers[server_id].current_load + delta
            )

    def update_server_health(self, server_id: str, health_score: float) -> None:
        if server_id in self.mcp_servers:
            self.mcp_servers[server_id].health_score = max(0.0, min(1.0, health_score))

    def get_routing_report(self) -> Dict[str, Any]:
        if not self.routing_history:
            return {"total_routes": 0, "servers": {}}

        server_stats = {}
        for server in self.mcp_servers.values():
            routed_tasks = [r for r in self.routing_history if r.mcp_server_id == server.id]
            server_stats[server.id] = {
                "name": server.name,
                "tasks_routed": len(routed_tasks),
                "current_load": server.current_load,
                "health_score": server.health_score,
                "avg_confidence": (
                    sum(r.confidence for r in routed_tasks) / len(routed_tasks)
                    if routed_tasks else 0.0
                )
            }

        return {
            "total_routes": len(self.routing_history),
            "servers": server_stats,
            "avg_confidence": sum(r.confidence for r in self.routing_history) / len(self.routing_history)
        }

    def export_routing_log(self, filepath: str) -> None:
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_routes": len(self.routing_history),
            "routes": [asdict(r) for r in self.routing_history],
            "servers": {
                sid: asdict(server) for sid, server in self.mcp_servers.items()
            }
        }
        with open(filepath, "w") as f:
            json.dump(log_data, f, indent=2)


def register_mcp_router_di() -> None:
    """Registra MCPRouter no Container (chamar apos initialize_core)."""
    from core.container import Container
    if not Container.instance().is_registered('mcp_router'):
        Container.instance().register('mcp_router', MCPRouter.from_container(Container.instance()))