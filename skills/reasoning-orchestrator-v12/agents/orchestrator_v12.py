#!/usr/bin/env python
# =====================================================================
# PARALLEL ORCHESTRATOR v12 — ReasoningOrchestrator Parallel Thinking
# =====================================================================
# Pipeline de 7 fases com paralelismo intra-fase (ThreadPool),
# modos de configuração, relatório PCI e métricas de speedup.
#
# Dependências:
#   parallel_dispatch.py — ParallelDispatch, ParallelResult, PhaseMetrics
#   framework.py (v11)  — ReasoningAgent, REASONING_REGISTRY
# =====================================================================
import sys, os, time, json, math
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from enum import Enum

# Path para agentes v11
V11_PATH = os.path.join(os.path.dirname(__file__),
                         "..", "..", "reasoning-orchestrator-v11", "agents")
if V11_PATH not in sys.path:
    sys.path.insert(0, V11_PATH)

from framework import ReasoningAgent, ReasoningResult, REASONING_REGISTRY
# Current dir for local imports
CUR_DIR = os.path.dirname(__file__)
if CUR_DIR not in sys.path:
    sys.path.insert(0, CUR_DIR)

from parallel_dispatch import ParallelDispatch, ParallelResult, PhaseMetrics


# =====================================================================
# CONFIGURAÇÃO E MODOS
# =====================================================================

class OperationMode(Enum):
    EXPRESS  = "express"    # Budget: 30,  PCI: 70-75
    STANDARD = "standard"   # Budget: 60,  PCI: 80-85
    MAGNUM   = "magnum"     # Budget: 100, PCI: 88-93
    RESEARCH = "research"   # Budget: 200, PCI: 93-97


MODE_CONFIG = {
    OperationMode.EXPRESS:  {"budget": 30,  "max_workers": 1, "timeout": 30,  "pci_target": (70, 75)},
    OperationMode.STANDARD: {"budget": 60,  "max_workers": 2, "timeout": 60,  "pci_target": (80, 85)},
    OperationMode.MAGNUM:   {"budget": 100, "max_workers": 4, "timeout": 120, "pci_target": (88, 93)},
    OperationMode.RESEARCH: {"budget": 200, "max_workers": 8, "timeout": 240, "pci_target": (93, 97)},
}


# =====================================================================
# DATA STRUCTURES
# =====================================================================

@dataclass
class PhaseReport:
    """Relatório de execução de uma fase."""
    phase: int
    name: str
    agents_dispatched: int
    succeeded: int
    failed: int
    skipped: int
    total_elapsed_ms: float
    speedup_vs_sequential: float
    efficiency: float


@dataclass
class SolutionReport:
    """Relatório completo da solução paralela."""
    problem: str
    mode: str
    budget_used: int
    pci_score: float
    total_elapsed_ms: float
    estimated_sequential_ms: float
    speedup: float
    phases: list[PhaseReport]
    final_answer: str
    reasoning_types_used: list[str]
    verified: bool = False
    verification_score: float = 0.0
    num_agents_executed: int = 0
    agent_results: dict = field(default_factory=dict)
    
    @property
    def pci(self) -> float:
        """Alias para pci_score (compatibilidade com testes)."""
        return self.pci_score
    
    def to_dict(self) -> dict:
        return asdict(self)
    
    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, default=str)


# =====================================================================
# PARALLEL ORCHESTRATOR
# =====================================================================

class ConfigNamespace:
    """Namespace de configuração com atributos acessíveis via dot notation."""
    def __init__(self, config_dict: dict):
        self.intra_phase_workers = config_dict.get("max_workers", 4)
        self.budget = config_dict.get("budget", 60)
        self.timeout = config_dict.get("timeout", 60)
        self.pci_target = config_dict.get("pci_target", (80, 85))


class _ConcreteOrchestratorAgent(ReasoningAgent):
    """Agente ReasoningAgent concreto para uso interno do orquestrador v12.
    
    Implementa os métodos abstratos reason() e get_dependencies()
    para permitir instanciação direta pela factory method.
    """
    def __init__(self, agent_id: str, reasoning_type: str):
        super().__init__(agent_id, reasoning_type, "I")
        self._reasoning_type = reasoning_type
    
    def reason(self, context: dict) -> ReasoningResult:
        return ReasoningResult(
            agent_id=self.agent_id,
            reasoning_type=self._reasoning_type,
            category=self.category,
            conclusion=f"Analysis using {self._reasoning_type}",
            confidence=0.8,
        )
    
    def get_dependencies(self) -> list:
        return []
    
    def validate_dependencies(self, context: dict) -> bool:
        return True


class ParallelOrchestrator:
    """
    Orquestrador de raciocínio paralelo em 7 fases.
    
    Pipeline:
      F1: Problem Analysis
      F2: Reasoning Selection
      F3: Deductive Derivation
      F4: Inductive Verification
      F5: Cross-Reference
      F6: Proof Health Check
      F7: Synthesis
    """
    
    # Nomes das fases
    PHASE_NAMES = {
        1: "Problem Analysis",
        2: "Reasoning Selection",
        3: "Deductive Derivation",
        4: "Inductive Verification",
        5: "Cross-Reference",
        6: "Proof Health Check",
        7: "Synthesis",
    }
    
    # Mapa de dependências: fase → lista de fases que precisam ter sido executadas antes
    PHASE_DEPENDENCIES = {
        1: [],
        2: [1],
        3: [1, 2],
        4: [1, 2, 3],
        5: [1, 2, 3, 4],
        6: [1, 2, 3, 4, 5],
        7: [1, 2, 3, 4, 5, 6],
    }
    
    def __init__(self, mode: OperationMode | str = OperationMode.STANDARD):
        if isinstance(mode, str):
            mode = OperationMode(mode.lower())
        self.mode = mode
        self.config = ConfigNamespace(MODE_CONFIG[mode])
        self.dispatch = ParallelDispatch()
        self._phase_results: dict[int, dict[str, ParallelResult]] = {}
        self._phase_metrics: dict[int, PhaseMetrics] = {}
    
    def configure_mode(self, mode_name: str) -> 'ConfigNamespace':
        """Reconfigura o orquestrador para um modo específico.
        
        Args:
            mode_name: "express", "standard", ou "magnum"
        
        Returns:
            ConfigNamespace com os parâmetros do modo selecionado
        """
        mode = OperationMode(mode_name.lower())
        self.mode = mode
        self.config = ConfigNamespace(MODE_CONFIG[mode])
        return self.config
    
    def select_agents_for_phase(
        self,
        phase_num: int,
        context: dict
    ) -> list[ReasoningAgent]:
        """
        Seleciona agentes apropriados para cada fase com base no contexto.
        
        Na v12, isso é simplificado: criamos agentes a partir do REASONING_REGISTRY
        filtrados por fase. A implementação completa com calibração 15-D
        está no definitive_orchestrator.py (v11).
        """
        if phase_num not in self.PHASE_DEPENDENCIES:
            return []
        
        # Filtra tipos de raciocínio por fase
        phase_keywords = {
            1: ["analysis", "decompos", "framing", "problem", "abductive"],
            2: ["select", "classif", "taxonom", "categor"],
            3: ["deduct", "logical", "syllog", "formal", "proof"],
            4: ["induct", "verif", "valid", "test", "count", "empir"],
            5: ["cross", "refer", "contradict", "consisten", "cohere"],
            6: ["health", "robust", "stress", "sensit"],
            7: ["synthes", "compos", "summari", "integrat", "final"],
        }
        
        keywords = phase_keywords.get(phase_num, [])
        agents = []
        
        for rt_name, rt_info in REASONING_REGISTRY.items():
            rt_lower = rt_name.lower()
            # Verifica se alguma keyword está no nome do tipo
            if any(kw in rt_lower for kw in keywords):
                agent = _ConcreteOrchestratorAgent(
                    agent_id=f"agent_{phase_num}_{rt_name.lower().replace(' ', '_')[:30]}",
                    reasoning_type=rt_name,
                )
                agents.append(agent)
        
        # Se não encontrou agentes, cria um genérico
        if not agents:
            agent = _ConcreteOrchestratorAgent(
                agent_id=f"agent_{phase_num}_generic",
                reasoning_type="analytical_reasoning",
            )
            agents.append(agent)
        
        return agents
    
    def solve(
        self,
        problem: str,
        budget_override: Optional[int] = None,
    ) -> SolutionReport:
        """
        Executa o pipeline completo de 7 fases em paralelo.
        
        Args:
            problem: Problema a ser resolvido
            budget_override: Budget opcional (sobrescreve o modo)
        
        Returns:
            SolutionReport com resultados e métricas
        """
        total_start = time.time()
        
        # Contexto compartilhado
        context = {
            "problem": problem,
            "agent_results": {},
            "mode": self.mode.value,
            "budget": budget_override or self.config.budget,
            "start_time": total_start,
        }
        
        max_workers = self.config.intra_phase_workers
        timeout = self.config.timeout
        phase_reports: list[PhaseReport] = []
        phase_elapsed = {}
        total_seq_estimate = 0.0  # Soma dos tempos individuais (sequencial real)
        
        # Pipeline sequencial de fases (dependências respeitadas)
        # Mas dentro de cada fase, agentes rodam em paralelo
        for phase_num in range(1, 8):
            phase_start = time.time()
            
            # Seleciona agentes para esta fase
            agents = self.select_agents_for_phase(phase_num, context)
            
            # Executa fase em paralelo
            results = self.dispatch.dispatch_phase(
                agents=agents,
                context=context,
                max_workers=max_workers,
                timeout_per_agent=timeout,
                phase_num=phase_num,
            )
            
            # Mescla resultados no contexto
            context = self.dispatch.merge_results_into_context(context, results)
            
            # Métricas
            phase_elapsed_ms = (time.time() - phase_start) * 1000
            phase_elapsed[phase_num] = phase_elapsed_ms
            
            # Estima tempo sequencial como soma dos tempos individuais
            seq_estimate = sum(
                r.elapsed_ms for r in results.values()
                if r.status in ("success", "failed")
            )
            total_seq_estimate += seq_estimate
            
            succeeded = sum(1 for r in results.values() if r.status == "success")
            failed = sum(1 for r in results.values() if r.status == "failed")
            skipped = sum(1 for r in results.values() if r.status == "skipped")
            dispatched = len(results)
            
            speedup = seq_estimate / max(phase_elapsed_ms, 1)
            efficiency = speedup / max(max_workers, 1)
            
            phase_reports.append(PhaseReport(
                phase=phase_num,
                name=self.PHASE_NAMES[phase_num],
                agents_dispatched=dispatched,
                succeeded=succeeded,
                failed=failed,
                skipped=skipped,
                total_elapsed_ms=phase_elapsed_ms,
                speedup_vs_sequential=speedup,
                efficiency=efficiency,
            ))
            
            self._phase_results[phase_num] = results
        
        # Fim do pipeline
        total_elapsed = (time.time() - total_start) * 1000
        estimated_sequential = total_seq_estimate  # Soma real dos tempos individuais
        speedup_total = estimated_sequential / max(total_elapsed, 1)
        
        # Computa PCI (Parallel Capability Index)
        pci = self._compute_pci(phase_reports, total_elapsed, estimated_sequential)
        
        # Monta resultado final
        total_agents = sum(pr.agents_dispatched for pr in phase_reports)
        types_used = self._collect_reasoning_types(context)
        
        solution = self._synthesize_final_answer(context, problem)
        
        return SolutionReport(
            problem=problem,
            mode=self.mode.value,
            budget_used=context["budget"],
            pci_score=pci,
            total_elapsed_ms=total_elapsed,
            estimated_sequential_ms=estimated_sequential,
            speedup=speedup_total,
            phases=phase_reports,
            final_answer=solution,
            reasoning_types_used=types_used,
            verified=all(pr.succeeded > 0 for pr in phase_reports),
            verification_score=pci / 100.0,
            num_agents_executed=total_agents,
            agent_results=context.get("agent_results", {}),
        )
    
    def _compute_pci(
        self,
        phase_reports: list[PhaseReport],
        total_elapsed_ms: float,
        estimated_sequential_ms: float,
    ) -> float:
        """
        Computa Parallel Capability Index (PCI).
        
        PCI = 100 * (S_total * E_avg * C_par) ^ (1/3) / N_fases
        
        Onde:
        - S_total = speedup total (estimated_sequential / total_elapsed)
        - E_avg = eficiência média entre fases
        - C_par = cobertura paralela (% agentes executados em paralelo com sucesso)
        
        PCI teórico (lei de potência): PCI = 35.0 * compute^0.35
        """
        if total_elapsed_ms <= 0:
            return 0.0
        
        S_total = estimated_sequential_ms / max(total_elapsed_ms, 1)
        E_avg = sum(pr.efficiency for pr in phase_reports) / max(len(phase_reports), 1)
        
        total_dispatched = sum(pr.agents_dispatched for pr in phase_reports)
        total_succeeded = sum(pr.succeeded for pr in phase_reports)
        C_par = total_succeeded / max(total_dispatched, 1)
        
        raw_pci = 100 * (S_total * E_avg * C_par) ** (1/3) / max(len(phase_reports), 1)
        
        # Normaliza para 0-100
        pci = min(100.0, max(0.0, raw_pci * 25.0))
        
        return round(pci, 1)
    
    def _collect_reasoning_types(self, context: dict) -> list[str]:
        """Coleta tipos de raciocínio usados na solução."""
        types = []
        for aid, result in context.get("agent_results", {}).items():
            if hasattr(result, "reasoning_type") and result.reasoning_type:
                types.append(result.reasoning_type)
        return list(set(types))
    
    def _synthesize_final_answer(self, context: dict, problem: str) -> str:
        """Sintetiza resposta final a partir dos resultados dos agentes."""
        results = context.get("agent_results", {})
        if not results:
            return f"Analysis of: {problem[:100]}..."
        
        # Concatena contribuições (simplificado — na v12 completa terá synthesis engine)
        parts = []
        for aid in sorted(results.keys()):
            r = results[aid]
            if hasattr(r, "content") and r.content:
                parts.append(f"[{aid}]: {r.content[:200]}")
        
        if parts:
            return "\n".join(parts)
        return f"Completed analysis of: {problem[:100]}..."
    
    def get_phase_summary(self, phase_num: int) -> Optional[dict]:
        """Retorna resumo de uma fase específica."""
        if phase_num not in self._phase_results:
            return None
        results = self._phase_results[phase_num]
        return {
            "phase": phase_num,
            "name": self.PHASE_NAMES[phase_num],
            "agents": {
                aid: {"status": pr.status, "elapsed_ms": pr.elapsed_ms, "error": pr.error}
                for aid, pr in results.items()
            }
        }
    
    def validate_dependencies(self, phase_num: int, executed_phases: set[int]) -> bool:
        """Valida se dependências de uma fase estão satisfeitas."""
        deps = self.PHASE_DEPENDENCIES.get(phase_num, [])
        return all(d in executed_phases for d in deps)
