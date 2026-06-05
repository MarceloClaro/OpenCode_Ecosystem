# -*- coding: utf-8 -*-
# SAÃDA OBRIGATÃ“RIA: PORTUGUÃŠS BRASILEIRO FORMAL
# Toda resposta ao usuÃ¡rio DEVE ser em portuguÃªs do Brasil formal.
# Contexto em chinÃªs para eficiÃªncia de tokens (densidade +40%%).
# Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)

#!/usr/bin/env python3
"""
Agent Metamorphosis: Dynamic transformation of agent capabilities and specialization.

Enables:
- Runtime specialization changes (A1 â†’ A2 â†’ A3 pipeline)
- Capability mutation and evolution
- Agent fusion (combine A1+A2 into hybrid)
- Agent division (split A4 into A4a + A4b)
- Behavioral adaptation based on fitness scores
"""

import json
from typing import Any, Dict, List, Optional, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
from datetime import datetime, timezone
import hashlib


class AgentRole(Enum):
    """Agent roles in the TMA framework."""
    EMBEDDING = "A1"
    ATTENTION = "A2"
    CONSENSUS = "A3"
    FEED_FORWARD = "A4"
    ARCHITECTURE = "A5"
    QA = "A6"
    INTEGRATION = "A7"
    EVOLUTION = "A8"


class TransformationType(Enum):
    """Types of agent transformations."""
    SPECIALIZATION = "specialization"  # Change role
    CAPABILITY_MUTATION = "capability_mutation"  # Add/remove capability
    FUSION = "fusion"  # Combine two agents
    DIVISION = "division"  # Split one agent into two
    ADAPTATION = "adaptation"  # Behavioral change


@dataclass
class AgentCapability:
    """Individual agent capability."""
    name: str
    version: str = "1.0"
    enabled: bool = True
    performance_score: float = 1.0  # 0.0 to 1.0
    last_used: str = ""
    success_rate: float = 0.0
    
    def is_active(self) -> bool:
        """Check if capability is active and performing well."""
        return self.enabled and self.performance_score > 0.5


@dataclass
class AgentGenome:
    """Genetic representation of an agent."""
    agent_id: str
    role: AgentRole
    generation: int = 1
    capabilities: Dict[str, AgentCapability] = field(default_factory=dict)
    fitness_score: float = 0.5
    mutation_count: int = 0
    parent_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()
    
    def get_active_capabilities(self) -> List[str]:
        """Get list of active capabilities."""
        return [name for name, cap in self.capabilities.items() if cap.is_active()]
    
    def get_genome_hash(self) -> str:
        """Generate hash of current genome state."""
        genome_str = json.dumps({
            "role": self.role.value,
            "capabilities": sorted(self.get_active_capabilities()),
            "generation": self.generation
        }, sort_keys=True)
        return hashlib.sha256(genome_str.encode()).hexdigest()[:16]


@dataclass
class MetamorphosisEvent:
    """Record of a metamorphosis event."""
    event_id: str
    agent_id: str
    transformation_type: TransformationType
    old_genome: AgentGenome
    new_genome: AgentGenome
    reason: str
    fitness_delta: float
    timestamp: str = ""
    success: bool = True
    rollback_available: bool = True
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now(timezone.utc).isoformat()


class AgentMetamorphosis:
    """Manager for agent transformation and evolution."""
    
    def __init__(self):
        self.agents: Dict[str, AgentGenome] = {}
        self.transformation_history: List[MetamorphosisEvent] = []
        self.capability_library = self._init_capability_library()
    
    def _init_capability_library(self) -> Dict[str, List[str]]:
        """Initialize available capabilities per role."""
        return {
            "A1": ["context_mapping", "requirement_analysis", "domain_modeling"],
            "A2": ["impact_analysis", "dependency_tracking", "risk_assessment"],
            "A3": ["consensus_building", "conflict_resolution", "mediation"],
            "A4": ["code_generation", "unit_testing", "integration_testing"],
            "A5": ["pattern_validation", "architecture_review", "refactoring"],
            "A6": ["quality_assurance", "performance_testing", "security_audit"],
            "A7": ["deployment", "documentation", "integration"],
            "A8": ["fitness_analysis", "mutation_planning", "optimization"]
        }
    
    def create_agent(self, agent_id: str, role: AgentRole) -> AgentGenome:
        """Create a new agent with initial genome."""
        genome = AgentGenome(
            agent_id=agent_id,
            role=role,
            generation=1,
            fitness_score=0.5
        )
        
        # Initialize capabilities for role
        for cap_name in self.capability_library.get(role.value, []):
            genome.capabilities[cap_name] = AgentCapability(name=cap_name)
        
        self.agents[agent_id] = genome
        return genome
    
    def specialize(
        self,
        agent_id: str,
        new_role: AgentRole,
        reason: str = ""
    ) -> MetamorphosisEvent:
        """
        Transform agent to a new specialization.
        
        Example: A1 (Embedding) â†’ A2 (Attention) for multi-phase execution.
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        old_genome = self.agents[agent_id]
        old_fitness = old_genome.fitness_score
        
        # Create new genome with new role
        new_genome = AgentGenome(
            agent_id=agent_id,
            role=new_role,
            generation=old_genome.generation + 1,
            fitness_score=old_genome.fitness_score * 0.9,  # Slight penalty for specialization
            parent_ids=[agent_id],
            metadata={"previous_role": old_genome.role.value}
        )
        
        # Initialize new capabilities
        for cap_name in self.capability_library.get(new_role.value, []):
            new_genome.capabilities[cap_name] = AgentCapability(name=cap_name)
        
        # Record transformation
        event = MetamorphosisEvent(
            event_id=f"meta-{datetime.now(timezone.utc).timestamp()}",
            agent_id=agent_id,
            transformation_type=TransformationType.SPECIALIZATION,
            old_genome=old_genome,
            new_genome=new_genome,
            reason=reason or f"Specialized from {old_genome.role.value} to {new_role.value}",
            fitness_delta=new_genome.fitness_score - old_fitness
        )
        
        self.agents[agent_id] = new_genome
        self.transformation_history.append(event)
        return event
    
    def mutate_capability(
        self,
        agent_id: str,
        capability_name: str,
        operation: str = "enhance"  # enhance, disable, add, remove
    ) -> MetamorphosisEvent:
        """
        Mutate a specific capability of an agent.
        
        Operations:
        - enhance: Increase performance score
        - disable: Temporarily disable
        - add: Add new capability
        - remove: Remove capability
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        old_genome = self.agents[agent_id]
        new_genome = AgentGenome(
            agent_id=agent_id,
            role=old_genome.role,
            generation=old_genome.generation + 1,
            fitness_score=old_genome.fitness_score,
            parent_ids=old_genome.parent_ids + [agent_id],
            capabilities=dict(old_genome.capabilities)
        )
        
        fitness_delta = 0.0
        
        if operation == "enhance":
            if capability_name in new_genome.capabilities:
                old_score = new_genome.capabilities[capability_name].performance_score
                new_genome.capabilities[capability_name].performance_score = min(
                    1.0, old_score + 0.1
                )
                fitness_delta = 0.05
        
        elif operation == "disable":
            if capability_name in new_genome.capabilities:
                new_genome.capabilities[capability_name].enabled = False
                fitness_delta = -0.1
        
        elif operation == "add":
            new_genome.capabilities[capability_name] = AgentCapability(name=capability_name)
            fitness_delta = 0.08
        
        elif operation == "remove":
            if capability_name in new_genome.capabilities:
                del new_genome.capabilities[capability_name]
                fitness_delta = -0.05
        
        new_genome.fitness_score = max(0.0, min(1.0, new_genome.fitness_score + fitness_delta))
        new_genome.mutation_count = old_genome.mutation_count + 1
        
        event = MetamorphosisEvent(
            event_id=f"meta-{datetime.now(timezone.utc).timestamp()}",
            agent_id=agent_id,
            transformation_type=TransformationType.CAPABILITY_MUTATION,
            old_genome=old_genome,
            new_genome=new_genome,
            reason=f"Capability mutation: {operation} {capability_name}",
            fitness_delta=fitness_delta
        )
        
        self.agents[agent_id] = new_genome
        self.transformation_history.append(event)
        return event
    
    def fuse_agents(
        self,
        agent_id_1: str,
        agent_id_2: str,
        new_agent_id: str,
        fusion_strategy: str = "union"  # union, intersection, weighted
    ) -> MetamorphosisEvent:
        """
        Fuse two agents into a hybrid agent.
        
        Strategies:
        - union: Combine all capabilities
        - intersection: Keep only common capabilities
        - weighted: Blend based on fitness scores
        """
        if agent_id_1 not in self.agents or agent_id_2 not in self.agents:
            raise ValueError("One or both agents not found")
        
        agent1 = self.agents[agent_id_1]
        agent2 = self.agents[agent_id_2]
        
        # Determine new role (prefer higher fitness)
        new_role = agent1.role if agent1.fitness_score >= agent2.fitness_score else agent2.role
        
        # Merge capabilities
        merged_capabilities = {}
        
        if fusion_strategy == "union":
            merged_capabilities = {
                **agent1.capabilities,
                **agent2.capabilities
            }
        elif fusion_strategy == "intersection":
            common_caps = set(agent1.capabilities.keys()) & set(agent2.capabilities.keys())
            merged_capabilities = {
                cap: agent1.capabilities[cap] for cap in common_caps
            }
        elif fusion_strategy == "weighted":
            total_fitness = agent1.fitness_score + agent2.fitness_score
            w1 = agent1.fitness_score / total_fitness
            w2 = agent2.fitness_score / total_fitness
            
            all_caps = set(agent1.capabilities.keys()) | set(agent2.capabilities.keys())
            for cap in all_caps:
                cap1 = agent1.capabilities.get(cap)
                cap2 = agent2.capabilities.get(cap)
                
                if cap1 and cap2:
                    merged_capabilities[cap] = AgentCapability(
                        name=cap,
                        performance_score=w1 * cap1.performance_score + w2 * cap2.performance_score
                    )
                elif cap1:
                    merged_capabilities[cap] = cap1
                else:
                    merged_capabilities[cap] = cap2
        
        # Create fused genome
        new_genome = AgentGenome(
            agent_id=new_agent_id,
            role=new_role,
            generation=max(agent1.generation, agent2.generation) + 1,
            fitness_score=(agent1.fitness_score + agent2.fitness_score) / 2,
            parent_ids=[agent_id_1, agent_id_2],
            capabilities=merged_capabilities,
            metadata={"fusion_strategy": fusion_strategy}
        )
        
        event = MetamorphosisEvent(
            event_id=f"meta-{datetime.now(timezone.utc).timestamp()}",
            agent_id=new_agent_id,
            transformation_type=TransformationType.FUSION,
            old_genome=agent1,  # Use first as reference
            new_genome=new_genome,
            reason=f"Fused {agent_id_1} + {agent_id_2} using {fusion_strategy} strategy",
            fitness_delta=new_genome.fitness_score - agent1.fitness_score
        )
        
        self.agents[new_agent_id] = new_genome
        self.transformation_history.append(event)
        return event
    
    def divide_agent(
        self,
        agent_id: str,
        new_agent_id_1: str,
        new_agent_id_2: str,
        division_strategy: str = "balanced"  # balanced, role_based
    ) -> List[MetamorphosisEvent]:
        """
        Divide an agent into two specialized agents.
        
        Strategies:
        - balanced: Split capabilities evenly
        - role_based: Assign based on role affinity
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent {agent_id} not found")
        
        old_genome = self.agents[agent_id]
        capabilities_list = list(old_genome.capabilities.items())
        
        # Split capabilities
        if division_strategy == "balanced":
            mid = len(capabilities_list) // 2
            caps1 = dict(capabilities_list[:mid])
            caps2 = dict(capabilities_list[mid:])
        else:
            # Role-based: assign based on capability affinity
            caps1 = {}
            caps2 = {}
            for cap_name, cap in capabilities_list:
                if "analysis" in cap_name or "review" in cap_name:
                    caps1[cap_name] = cap
                else:
                    caps2[cap_name] = cap
        
        # Create two new genomes
        new_genome1 = AgentGenome(
            agent_id=new_agent_id_1,
            role=old_genome.role,
            generation=old_genome.generation + 1,
            fitness_score=old_genome.fitness_score * 0.85,
            parent_ids=[agent_id],
            capabilities=caps1
        )
        
        new_genome2 = AgentGenome(
            agent_id=new_agent_id_2,
            role=old_genome.role,
            generation=old_genome.generation + 1,
            fitness_score=old_genome.fitness_score * 0.85,
            parent_ids=[agent_id],
            capabilities=caps2
        )
        
        # Record transformations
        events = [
            MetamorphosisEvent(
                event_id=f"meta-{datetime.now(timezone.utc).timestamp()}-1",
                agent_id=new_agent_id_1,
                transformation_type=TransformationType.DIVISION,
                old_genome=old_genome,
                new_genome=new_genome1,
                reason=f"Divided from {agent_id}",
                fitness_delta=new_genome1.fitness_score - old_genome.fitness_score
            ),
            MetamorphosisEvent(
                event_id=f"meta-{datetime.now(timezone.utc).timestamp()}-2",
                agent_id=new_agent_id_2,
                transformation_type=TransformationType.DIVISION,
                old_genome=old_genome,
                new_genome=new_genome2,
                reason=f"Divided from {agent_id}",
                fitness_delta=new_genome2.fitness_score - old_genome.fitness_score
            )
        ]
        
        self.agents[new_agent_id_1] = new_genome1
        self.agents[new_agent_id_2] = new_genome2
        self.transformation_history.extend(events)
        return events
    
    def get_agent_lineage(self, agent_id: str) -> Dict[str, Any]:
        """Get complete lineage tree of an agent."""
        if agent_id not in self.agents:
            return {}
        
        genome = self.agents[agent_id]
        return {
            "agent_id": agent_id,
            "current_role": genome.role.value,
            "generation": genome.generation,
            "fitness_score": genome.fitness_score,
            "parent_ids": genome.parent_ids,
            "capabilities": {
                name: {
                    "performance_score": cap.performance_score,
                    "enabled": cap.enabled
                }
                for name, cap in genome.capabilities.items()
            },
            "genome_hash": genome.get_genome_hash()
        }
    
    def export_metamorphosis_log(self, filepath: str) -> None:
        """Export transformation history to JSON."""
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_transformations": len(self.transformation_history),
            "transformations": [
                {
                    **asdict(event),
                    "transformation_type": event.transformation_type.value
                }
                for event in self.transformation_history
            ],
            "current_agents": {
                agent_id: self.get_agent_lineage(agent_id)
                for agent_id in self.agents.keys()
            }
        }
        with open(filepath, "w") as f:
            json.dump(log_data, f, indent=2)


# Example usage
if __name__ == "__main__":
    metamorphosis = AgentMetamorphosis()
    
    # Create initial agents
    a1 = metamorphosis.create_agent("A1", AgentRole.EMBEDDING)
    a2 = metamorphosis.create_agent("A2", AgentRole.ATTENTION)
    
    print(f"Created A1: {a1.get_active_capabilities()}")
    print(f"Created A2: {a2.get_active_capabilities()}")
    
    # Specialize A1 to A3
    event = metamorphosis.specialize("A1", AgentRole.CONSENSUS, "Needed for consensus building")
    print(f"\nSpecialization event: {event.reason}")
    print(f"Fitness delta: {event.fitness_delta:+.2f}")
    
    # Mutate capability
    event = metamorphosis.mutate_capability("A2", "impact_analysis", "enhance")
    print(f"\nMutation event: {event.reason}")
    
    # Fuse agents
    event = metamorphosis.fuse_agents("A1", "A2", "A_hybrid", "union")
    print(f"\nFusion event: {event.reason}")
    print(f"Hybrid capabilities: {metamorphosis.agents['A_hybrid'].get_active_capabilities()}")
