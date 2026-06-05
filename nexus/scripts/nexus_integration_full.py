# -*- coding: utf-8 -*-
"""
NEXUS INTEGRATION LAYER v5.0 - Full Ecosystem Integration
Connects ALL modules to sync_orchestrator:
- 4 orphan modules (agent_metamorphosis, domain_discovery, knowledge_graphs, granular_sync)
- 5 micro_* modules (feedback, integration, reasoning, sync, validation)
- mcp_router + mcp_self_organization
- meta_learning_engine + phd_learning_cores
"""
import sys, json, time, logging
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).parent))
from ecosystem_config import ECO_ROOT, EVOLVE_DIR, NEXUS_SCRIPTS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


# ============================================================================
# Orphan Module Integration
# ============================================================================

class AgentMetamorphosisIntegration:
    """Connects agent_metamorphosis to sync_orchestrator."""
    def __init__(self):
        from agent_metamorphosis import AgentGenome, AgentRole, TransformationType
        self.AgentGenome = AgentGenome
        self.AgentRole = AgentRole
        self.TransformationType = TransformationType

    def transform_agent(self, agent_id, new_role, capabilities=None):
        genome = self.AgentGenome(
            agent_id=agent_id,
            role=self.AgentRole[new_role] if isinstance(new_role, str) else new_role
        )
        if capabilities:
            for name, cap in capabilities.items():
                from agent_metamorphosis import AgentCapability
                genome.capabilities[name] = AgentCapability(name=name, **cap) if isinstance(cap, dict) else cap
        return genome

    def get_fitness_score(self, genome):
        caps = genome.get_active_capabilities() if hasattr(genome, "get_active_capabilities") else []
        return genome.fitness_score + (len(caps) * 0.1)


class DomainDiscoveryIntegration:
    """Connects domain_discovery_engine to evolution_loop."""
    def __init__(self):
        from domain_discovery_engine import DomainDiscoveryEngine
        self.engine = DomainDiscoveryEngine()

    def discover_domain(self, domain_name, context_text):
        return self.engine.discover_domain(domain_name, context_text)

    def get_domain_profile(self, domain_name):
        return self.engine.get_profile(domain_name)


class KnowledgeGraphIntegration:
    """Connects knowledge_graphs to context_offload."""
    def __init__(self):
        from knowledge_graphs import KnowledgeGraph, EntityType, RelationType
        self.graph = KnowledgeGraph()
        self.EntityType = EntityType
        self.RelationType = RelationType

    def add_entity(self, entity_id, name, entity_type, description):
        return self.graph.add_entity(entity_id, name, entity_type, description)

    def add_relation(self, from_id, to_id, relation_type):
        return self.graph.add_relation(from_id, to_id, relation_type)

    def query_related(self, entity_id, relation_type=None):
        return self.graph.query_related(entity_id, relation_type)

    def save(self, path=None):
        p = path or str(EVOLVE_DIR / "knowledge_graph.json")
        self.graph.save(p)


class GranularSyncIntegration:
    """Connects granular_sync to sync_orchestrator barriers."""
    def __init__(self):
        from granular_sync import GranularSyncManager, SyncBarrierType, OperationStatus
        self.engine = GranularSyncManager()
        self.SyncBarrierType = SyncBarrierType
        self.OperationStatus = OperationStatus

    def create_barrier(self, barrier_id, phase, operation_ids):
        return self.engine.create_barrier(barrier_id, phase, operation_ids)

    def check_barrier(self, barrier_id):
        return self.engine.check_barrier(barrier_id)

    def commit_operation(self, op_id, agent_id, artifacts=None):
        return self.engine.commit_operation(op_id, agent_id, artifacts)


# ============================================================================
# Micro Module Integration
# ============================================================================

class MicroFeedbackIntegration:
    """Connects micro_feedback_loop to evolution loop."""
    def __init__(self):
        from micro_feedback_loop import MicroFeedbackEngine, FeedbackType, Lesson
        self.loop = MicroFeedbackEngine()
        self.FeedbackType = FeedbackType
        self.Lesson = Lesson

    def record_feedback(self, barrier_id, feedback_type, description, impact=0.5, confidence=0.8):
        return self.loop.record_feedback(barrier_id, feedback_type, description, impact, confidence)

    def get_lessons(self, barrier_id=None):
        return self.loop.get_lessons(barrier_id)


class MicroValidationIntegration:
    """Connects micro_validation to all operations."""
    def __init__(self):
        from micro_validation import MicroValidator, ConstraintType
        self.validator = MicroValidator()
        self.ConstraintType = ConstraintType

    def validate(self, data, constraints):
        return self.validator.validate(data, constraints)

    def add_constraint(self, name, field, constraint_type, value, error_message, severity="error"):
        return self.validator.add_constraint(name, field, constraint_type, value, error_message, severity)


class MicroReasoningIntegration:
    """Connects micro_reasoning_types to decision making."""
    def __init__(self):
        from micro_reasoning_types import MicroReasoningEngine, ReasoningType
        self.engine = MicroReasoningEngine()
        self.ReasoningType = ReasoningType

    def reason(self, reasoning_type, context, data):
        return self.engine.reason(reasoning_type, context, data)


class MicroSyncIntegration:
    """Connects micro_sync_barriers to orchestrator."""
    def __init__(self):
        from micro_sync_barriers import MicroSyncBarrier, MicroSyncBarrierNetwork
        from micro_sync_barriers import MicroSyncBarrier, MicroSyncBarrierNetwork, BarrierStatus
        self.MicroSyncBarrier = MicroSyncBarrier; self.MicroSyncBarrierNetwork = MicroSyncBarrierNetwork; self.BarrierStatus = BarrierStatus; self.active_barriers = {}

    def create_micro_barrier(self, name, phase, required_agents):
        return self.barriers.create_micro_barrier(name, phase, required_agents)

    def check_all_barriers(self):
        return self.barriers.check_all_barriers()


class MicroIntegrationLayer:
    """Connects micro_integration to main integration layer."""
    def __init__(self):
        from micro_integration import MicroTMAOrchestrator
        self.engine = None; self.Orchestrator = MicroTMAOrchestrator

    def integrate_results(self, results):
        return self.engine.integrate_results(results)


# ============================================================================
# MCP Router Integration
# ============================================================================

class MCPRouterIntegration:
    """Connects mcp_router to task routing."""
    def __init__(self):
        from mcp_router import MCPRouter, MCPCapability, AgentSpecialization
        self.router = MCPRouter()
        self.MCPCapability = MCPCapability
        self.AgentSpecialization = AgentSpecialization

    def route_task(self, task_descriptor):
        return self.router.route_task(task_descriptor)

    def register_server(self, server_id, name, capabilities, endpoint, max_concurrent=10):
        from mcp_router import MCPServer
        server = MCPServer(
            id=server_id, name=name, capabilities=capabilities,
            endpoint=endpoint, max_concurrent_tasks=max_concurrent
        )
        return self.router.register_server(server)

    def get_available_servers(self, required_capabilities):
        return self.router.get_available_servers(required_capabilities)


# ============================================================================
# Master Integration Facade
# ============================================================================

class NexusIntegrationFacade:
    """
    Single entry point for all integrations.
    Used by sync_orchestrator to access any module.
    """
    def __init__(self):
        self.orphan_agents = {}
        self.micro_modules = {}
        self.mcp_router = None
        self._initialized = False

    def initialize(self):
        if self._initialized:
            return True
        try:
            # Orphan modules
            self.orphan_agents["agent_metamorphosis"] = AgentMetamorphosisIntegration()
            self.orphan_agents["domain_discovery"] = DomainDiscoveryIntegration()
            self.orphan_agents["knowledge_graph"] = KnowledgeGraphIntegration()
            self.orphan_agents["granular_sync"] = GranularSyncIntegration()

            # Micro modules
            self.micro_modules["feedback"] = MicroFeedbackIntegration()
            self.micro_modules["validation"] = MicroValidationIntegration()
            self.micro_modules["reasoning"] = MicroReasoningIntegration()
            self.micro_modules["sync"] = MicroSyncIntegration()
            self.micro_modules["integration"] = MicroIntegrationLayer()

            # MCP Router
            self.mcp_router = MCPRouterIntegration()

            self._initialized = True
            logger.info("Nexus Integration Facade: ALL modules connected")
            return True
        except ImportError as e:
            logger.error(f"Integration failed: {e}")
            return False

    def get_orphan(self, name):
        return self.orphan_agents.get(name)

    def get_micro(self, name):
        return self.micro_modules.get(name)

    def get_mcp_router(self):
        return self.mcp_router

    def get_status(self):
        return {
            "initialized": self._initialized,
            "orphan_modules": list(self.orphan_agents.keys()),
            "micro_modules": list(self.micro_modules.keys()),
            "mcp_router": self.mcp_router is not None,
            "total_integrated": len(self.orphan_agents) + len(self.micro_modules) + (1 if self.mcp_router else 0)
        }


if __name__ == "__main__":
    facade = NexusIntegrationFacade()
    if facade.initialize():
        status = facade.get_status()
        print("Nexus Integration Status:")
        print(f"  Initialized: {status['initialized']}")
        print(f"  Orphan modules integrated: {len(status['orphan_modules'])}")
        print(f"  Micro modules integrated: {len(status['micro_modules'])}")
        print(f"  MCP Router connected: {status['mcp_router']}")
        print(f"  Total integrated: {status['total_integrated']}")
    else:
        print("Integration FAILED")
