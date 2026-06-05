# -*- coding: utf-8 -*-
# SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
# Toda resposta ao usuário DEVE ser em português do Brasil formal.
# Contexto em chinês para eficiência de tokens (densidade +40%%).
# Modelo: big-pickle (OpenCode Zen, 200K ctx, 128K out, gratuito)

#!/usr/bin/env python3
"""
MCP Self-Organization - TMA v4.0

MCPs se auto-organizam e negociam capacidades dinamicamente.

Capacidades:
- Descoberta automática de MCPs
- Negociação de capacidades
- Formação dinâmica de equipes
- Balanceamento de carga
- Fallback inteligente

Author: TMA Autonomy Team
Version: 4.0
Date: 2026-04-14
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional, Any
from enum import Enum
from datetime import datetime
import hashlib
import random


class MCPType(Enum):
    """Tipos de MCP"""
    FILESYSTEM = "filesystem"
    WEB_SEARCH = "web_search"
    DATABASE = "database"
    CODE_EXECUTION = "code_execution"
    LLM_INFERENCE = "llm_inference"
    MEMORY = "memory"
    UNKNOWN = "unknown"


class HealthStatus(Enum):
    """Status de saúde do MCP"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    OFFLINE = "offline"


@dataclass
class Capability:
    """Capacidade de um MCP"""
    name: str
    description: str
    cost: float  # 0-1, custo computacional
    latency: float  # ms
    reliability: float  # 0-1
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "cost": self.cost,
            "latency": self.latency,
            "reliability": self.reliability
        }


@dataclass
class MCPAgent:
    """Agente MCP com capacidades e saúde"""
    id: str
    mcp_type: MCPType
    capabilities: List[Capability] = field(default_factory=list)
    health_score: float = 1.0  # 0-1
    load: float = 0.0  # 0-1
    last_heartbeat: str = field(default_factory=lambda: datetime.now().isoformat())
    requests_processed: int = 0
    errors: int = 0
    
    @property
    def status(self) -> HealthStatus:
        """Determinar status de saúde"""
        if self.health_score >= 0.8:
            return HealthStatus.HEALTHY
        elif self.health_score >= 0.5:
            return HealthStatus.DEGRADED
        elif self.health_score > 0:
            return HealthStatus.UNHEALTHY
        else:
            return HealthStatus.OFFLINE
    
    @property
    def availability(self) -> float:
        """Disponibilidade (0-1)"""
        if self.status == HealthStatus.HEALTHY:
            return 1.0 - self.load
        elif self.status == HealthStatus.DEGRADED:
            return (1.0 - self.load) * 0.7
        elif self.status == HealthStatus.UNHEALTHY:
            return (1.0 - self.load) * 0.3
        else:
            return 0.0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "type": self.mcp_type.value,
            "capabilities": [c.to_dict() for c in self.capabilities],
            "health_score": self.health_score,
            "load": self.load,
            "status": self.status.value,
            "availability": self.availability,
            "requests_processed": self.requests_processed,
            "errors": self.errors
        }


@dataclass
class ServiceContract:
    """Contrato de serviço entre MCPs"""
    provider_id: str
    consumer_id: str
    capability: str
    sla_latency: float  # ms
    sla_reliability: float  # 0-1
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "provider": self.provider_id,
            "consumer": self.consumer_id,
            "capability": self.capability,
            "sla_latency": self.sla_latency,
            "sla_reliability": self.sla_reliability,
            "created_at": self.created_at
        }


# ============================================================================
# MCP SELF-ORGANIZATION
# ============================================================================

class MCPSelfOrganization:
    """
    Sistema de Auto-Organização de MCPs.
    
    MCPs se descobrem, negociam e formam equipes dinamicamente.
    """
    
    def __init__(self):
        self.mcps: Dict[str, MCPAgent] = {}
        self.contracts: List[ServiceContract] = []
        self.teams: Dict[str, List[str]] = {}  # task_id -> [mcp_ids]
        self.discovery_log: List[Dict] = []
        self.negotiation_log: List[Dict] = []
        
    # ========================================================================
    # DISCOVERY
    # ========================================================================
    
    def register_mcp(self, mcp: MCPAgent) -> None:
        """Registrar novo MCP no sistema"""
        self.mcps[mcp.id] = mcp
        
        self.discovery_log.append({
            "timestamp": datetime.now().isoformat(),
            "event": "mcp_registered",
            "mcp_id": mcp.id,
            "mcp_type": mcp.mcp_type.value,
            "capabilities": [c.name for c in mcp.capabilities]
        })
    
    def discover_mcps(self, capability_needed: str) -> List[str]:
        """Descobrir MCPs que têm determinada capacidade"""
        
        capable_mcps = []
        
        for mcp_id, mcp in self.mcps.items():
            # Verificar se MCP tem capacidade
            has_capability = any(
                c.name == capability_needed for c in mcp.capabilities
            )
            
            if has_capability and mcp.availability > 0:
                capable_mcps.append(mcp_id)
        
        self.discovery_log.append({
            "timestamp": datetime.now().isoformat(),
            "event": "capability_discovery",
            "capability": capability_needed,
            "found_mcps": capable_mcps,
            "count": len(capable_mcps)
        })
        
        return capable_mcps
    
    def discover_all_mcps(self) -> List[str]:
        """Descobrir todos os MCPs disponíveis"""
        return list(self.mcps.keys())
    
    # ========================================================================
    # NEGOTIATION
    # ========================================================================
    
    def negotiate_contract(self, provider_id: str, consumer_id: str,
                          capability: str, required_latency: float,
                          required_reliability: float) -> Optional[ServiceContract]:
        """
        Negociar contrato entre dois MCPs.
        
        Verifica se provider pode atender SLA do consumer.
        """
        
        if provider_id not in self.mcps or consumer_id not in self.mcps:
            return None
        
        provider = self.mcps[provider_id]
        
        # Verificar se provider tem capacidade
        capability_obj = None
        for c in provider.capabilities:
            if c.name == capability:
                capability_obj = c
                break
        
        if not capability_obj:
            return None
        
        # Verificar se pode atender SLA
        can_meet_latency = capability_obj.latency <= required_latency
        can_meet_reliability = capability_obj.reliability >= required_reliability
        
        if can_meet_latency and can_meet_reliability:
            contract = ServiceContract(
                provider_id=provider_id,
                consumer_id=consumer_id,
                capability=capability,
                sla_latency=required_latency,
                sla_reliability=required_reliability
            )
            
            self.contracts.append(contract)
            
            self.negotiation_log.append({
                "timestamp": datetime.now().isoformat(),
                "event": "contract_agreed",
                "provider": provider_id,
                "consumer": consumer_id,
                "capability": capability,
                "sla_latency": required_latency,
                "sla_reliability": required_reliability
            })
            
            return contract
        else:
            self.negotiation_log.append({
                "timestamp": datetime.now().isoformat(),
                "event": "contract_rejected",
                "provider": provider_id,
                "consumer": consumer_id,
                "capability": capability,
                "reason": "Cannot meet SLA"
            })
            
            return None
    
    # ========================================================================
    # TEAM FORMATION
    # ========================================================================
    
    def form_team(self, task_id: str, required_capabilities: List[str]) -> List[str]:
        """
        Formar equipe de MCPs para executar tarefa.
        
        Seleciona melhor MCP para cada capacidade necessária.
        """
        
        team = []
        
        for capability in required_capabilities:
            # Descobrir MCPs com capacidade
            capable_mcps = self.discover_mcps(capability)
            
            if not capable_mcps:
                # Fallback: não há MCP disponível
                continue
            
            # Selecionar melhor MCP (maior disponibilidade)
            best_mcp = max(
                capable_mcps,
                key=lambda mcp_id: self.mcps[mcp_id].availability
            )
            
            team.append(best_mcp)
        
        # Registrar equipe
        self.teams[task_id] = team
        
        return team
    
    def get_team(self, task_id: str) -> List[str]:
        """Obter equipe para tarefa"""
        return self.teams.get(task_id, [])
    
    # ========================================================================
    # LOAD BALANCING
    # ========================================================================
    
    def update_load(self, mcp_id: str, load: float) -> None:
        """Atualizar carga de MCP"""
        if mcp_id in self.mcps:
            self.mcps[mcp_id].load = max(0.0, min(1.0, load))
    
    def rebalance_load(self) -> Dict[str, float]:
        """
        Rebalancear carga entre MCPs.
        
        Move tarefas de MCPs sobrecarregados para ociosos.
        """
        
        rebalance_actions = {}
        
        # Identificar MCPs sobrecarregados (load > 0.8)
        overloaded = [
            mcp_id for mcp_id, mcp in self.mcps.items()
            if mcp.load > 0.8
        ]
        
        # Identificar MCPs ociosos (load < 0.3)
        underutilized = [
            mcp_id for mcp_id, mcp in self.mcps.items()
            if mcp.load < 0.3
        ]
        
        # Rebalancear
        for overloaded_id in overloaded:
            if not underutilized:
                break
            
            underutilized_id = underutilized.pop()
            
            # Transferir 20% da carga
            transfer = self.mcps[overloaded_id].load * 0.2
            
            self.mcps[overloaded_id].load -= transfer
            self.mcps[underutilized_id].load += transfer
            
            rebalance_actions[f"{overloaded_id}->{underutilized_id}"] = transfer
        
        return rebalance_actions
    
    # ========================================================================
    # HEALTH MONITORING
    # ========================================================================
    
    def update_health(self, mcp_id: str, success: bool) -> None:
        """Atualizar saúde de MCP baseado em sucesso/falha"""
        if mcp_id not in self.mcps:
            return
        
        mcp = self.mcps[mcp_id]
        mcp.requests_processed += 1
        
        if success:
            # Aumentar health score
            mcp.health_score = min(1.0, mcp.health_score + 0.01)
        else:
            # Diminuir health score
            mcp.health_score = max(0.0, mcp.health_score - 0.05)
            mcp.errors += 1
        
        mcp.last_heartbeat = datetime.now().isoformat()
    
    def get_healthy_mcps(self) -> List[str]:
        """Obter MCPs saudáveis"""
        return [
            mcp_id for mcp_id, mcp in self.mcps.items()
            if mcp.status == HealthStatus.HEALTHY
        ]
    
    # ========================================================================
    # FALLBACK STRATEGY
    # ========================================================================
    
    def get_fallback_mcps(self, primary_mcp_id: str,
                         capability: str) -> List[str]:
        """
        Obter MCPs alternativos para fallback.
        
        Retorna lista de MCPs que podem substituir o primário.
        """
        
        fallbacks = []
        
        for mcp_id, mcp in self.mcps.items():
            if mcp_id == primary_mcp_id:
                continue
            
            # Verificar se tem capacidade
            has_capability = any(
                c.name == capability for c in mcp.capabilities
            )
            
            if has_capability and mcp.availability > 0:
                fallbacks.append(mcp_id)
        
        # Ordenar por disponibilidade
        fallbacks.sort(
            key=lambda mcp_id: self.mcps[mcp_id].availability,
            reverse=True
        )
        
        return fallbacks
    
    # ========================================================================
    # REPORTING
    # ========================================================================
    
    def generate_organization_report(self) -> Dict:
        """Gerar relatório de organização"""
        
        total_mcps = len(self.mcps)
        healthy_mcps = len(self.get_healthy_mcps())
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_mcps": total_mcps,
            "healthy_mcps": healthy_mcps,
            "health_percentage": (healthy_mcps / total_mcps * 100) if total_mcps > 0 else 0,
            "mcps": {mcp_id: mcp.to_dict() for mcp_id, mcp in self.mcps.items()},
            "teams": self.teams,
            "contracts": [c.to_dict() for c in self.contracts],
            "total_requests": sum(mcp.requests_processed for mcp in self.mcps.values()),
            "total_errors": sum(mcp.errors for mcp in self.mcps.values()),
            "discovery_events": len(self.discovery_log),
            "negotiation_events": len(self.negotiation_log)
        }
    
    def generate_mcp_report(self, mcp_id: str) -> Optional[Dict]:
        """Gerar relatório de MCP específico"""
        if mcp_id not in self.mcps:
            return None
        
        mcp = self.mcps[mcp_id]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "mcp": mcp.to_dict(),
            "contracts_as_provider": [
                c.to_dict() for c in self.contracts
                if c.provider_id == mcp_id
            ],
            "contracts_as_consumer": [
                c.to_dict() for c in self.contracts
                if c.consumer_id == mcp_id
            ]
        }


# ============================================================================
# EXEMPLO DE USO
# ============================================================================

if __name__ == "__main__":
    org = MCPSelfOrganization()
    
    print("=" * 80)
    print("MCP Self-Organization v4.0")
    print("=" * 80)
    
    # Criar MCPs
    print("\n1. REGISTERING MCPs")
    
    filesystem_mcp = MCPAgent(
        id="mcp-fs-001",
        mcp_type=MCPType.FILESYSTEM,
        capabilities=[
            Capability("read_file", "Read file from filesystem", 0.1, 50, 0.99),
            Capability("write_file", "Write file to filesystem", 0.15, 100, 0.98)
        ]
    )
    
    web_search_mcp = MCPAgent(
        id="mcp-web-001",
        mcp_type=MCPType.WEB_SEARCH,
        capabilities=[
            Capability("search", "Search the web", 0.3, 500, 0.95),
            Capability("fetch", "Fetch web page", 0.2, 300, 0.90)
        ]
    )
    
    llm_mcp = MCPAgent(
        id="mcp-llm-001",
        mcp_type=MCPType.LLM_INFERENCE,
        capabilities=[
            Capability("infer", "Run LLM inference", 0.5, 1000, 0.99),
            Capability("batch", "Batch inference", 0.4, 2000, 0.98)
        ]
    )
    
    org.register_mcp(filesystem_mcp)
    org.register_mcp(web_search_mcp)
    org.register_mcp(llm_mcp)
    
    print(f"   Registered {len(org.mcps)} MCPs")
    
    # Descobrir MCPs
    print("\n2. DISCOVERING MCPs")
    
    search_capable = org.discover_mcps("search")
    print(f"   MCPs with 'search' capability: {search_capable}")
    
    # Negociar contrato
    print("\n3. NEGOTIATING CONTRACTS")
    
    contract = org.negotiate_contract(
        provider_id="mcp-web-001",
        consumer_id="mcp-llm-001",
        capability="search",
        required_latency=600,
        required_reliability=0.90
    )
    
    if contract:
        print(f"   Contract agreed: {contract.provider_id} -> {contract.consumer_id}")
    
    # Formar equipe
    print("\n4. FORMING TEAMS")
    
    team = org.form_team(
        task_id="task-001",
        required_capabilities=["search", "infer", "write_file"]
    )
    
    print(f"   Team for task-001: {team}")
    
    # Atualizar carga
    print("\n5. LOAD BALANCING")
    
    org.update_load("mcp-fs-001", 0.9)
    org.update_load("mcp-web-001", 0.2)
    
    rebalance = org.rebalance_load()
    print(f"   Rebalance actions: {rebalance}")
    
    # Atualizar saúde
    print("\n6. HEALTH MONITORING")
    
    org.update_health("mcp-fs-001", True)
    org.update_health("mcp-web-001", False)
    
    healthy = org.get_healthy_mcps()
    print(f"   Healthy MCPs: {healthy}")
    
    # Fallback
    print("\n7. FALLBACK STRATEGY")
    
    fallbacks = org.get_fallback_mcps("mcp-web-001", "search")
    print(f"   Fallback MCPs for 'search': {fallbacks}")
    
    # Relatório
    print("\n" + "=" * 80)
    print("ORGANIZATION REPORT")
    print("=" * 80)
    report = org.generate_organization_report()
    print(json.dumps(report, indent=2, default=str))
