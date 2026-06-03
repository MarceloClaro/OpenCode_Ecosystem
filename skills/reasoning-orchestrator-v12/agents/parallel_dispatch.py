#!/usr/bin/env python
# =====================================================================
# PARALLEL DISPATCH — Parallel Thinking Engine v12.0
# =====================================================================
# Camada 1: Intra-Fase Parallelism
# Executa agentes independentes de uma fase em paralelo via ThreadPool.
# 
# Dependências:
#   - reasoning-orchestrator-v11/agents/framework.py (ReasoningAgent)
# =====================================================================
import sys, os, time, json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from dataclasses import dataclass, field
from typing import Any, Optional

# Path para agentes v11 (reutilizados)
V11_PATH = os.path.join(os.path.dirname(__file__), 
                         "..", "..", "reasoning-orchestrator-v11", "agents")
if V11_PATH not in sys.path:
    sys.path.insert(0, V11_PATH)

from framework import ReasoningAgent, ReasoningResult


# =====================================================================
# DATA STRUCTURES
# =====================================================================

@dataclass
class ParallelResult:
    """Resultado de um agente executado paralelamente."""
    phase: int
    agent_id: str
    result: Optional[ReasoningResult]
    elapsed_ms: float
    thread_id: int
    status: str  # "success" | "failed" | "timeout" | "skipped"
    error: Optional[str] = None


@dataclass
class PhaseMetrics:
    """Métricas de execução de uma fase paralela."""
    phase: int
    total_agents: int
    succeeded: int
    failed: int
    skipped: int
    total_elapsed_ms: float
    speedup_vs_sequential: float  # T_seq_est / T_real
    
    @property
    def efficiency(self) -> float:
        """Eficiência do paralelismo (Amdahl)."""
        return self.speedup_vs_sequential / max(1, self.total_agents)


# =====================================================================
# PARALLEL DISPATCH ENGINE
# =====================================================================

class ParallelDispatch:
    """
    Executa agentes de uma fase em paralelo usando ThreadPoolExecutor.
    
    Features:
    - Execução paralela com timeout por agente
    - Isolamento de falhas (um agente não aborta os outros)
    - Validação de dependências antes da execução
    - Métricas de paralelismo (speedup, eficiência)
    - Suporte a diferentes modos (Express, Standard, Magnum)
    """
    
    def __init__(self):
        self._local = threading.local()
    
    def dispatch_phase(
        self,
        agents: list[ReasoningAgent],
        context: dict,
        max_workers: int = 4,
        timeout_per_agent: float = 60.0,
        phase_num: int = 1,
    ) -> dict[str, ParallelResult]:
        """
        Executa todos os agentes de uma fase em paralelo.
        
        Args:
            agents: Lista de agentes ReasoningAgent para executar
            context: Contexto compartilhado (problem, agent_results anteriores)
            max_workers: Tamanho do ThreadPool (default: 4)
            timeout_per_agent: Timeout máximo por agente em segundos
            phase_num: Número da fase (para métricas)
        
        Returns:
            dict[agent_id, ParallelResult] com resultados consolidados
        """
        start_time = time.time()
        results = {}
        processed = set()
        
        # Filtra agentes com dependências satisfeitas
        valid_agents = []
        skipped_agents = []
        
        for agent in agents:
            try:
                if not agent.validate_dependencies(context):
                    skipped_agents.append(agent.agent_id)
                    continue
                valid_agents.append(agent)
            except Exception:
                skipped_agents.append(agent.agent_id)
                continue
        
        # Executa agentes válidos em paralelo
        # NOTA: Não usar 'with ThreadPoolExecutor' pois o __exit__ bloqueia
        # até todos os threads terminarem (shutdown wait=True), o que impede
        # o timeout de funcionar corretamente.
        executor = ThreadPoolExecutor(max_workers=max_workers)
        future_to_agent = {}
        batch_timed_out = False
        
        try:
            for agent in valid_agents:
                future = executor.submit(self._execute_agent, agent, context, phase_num)
                future_to_agent[future] = agent
            
            try:
                for future in as_completed(future_to_agent, timeout=timeout_per_agent):
                    agent = future_to_agent[future]
                    try:
                        result = future.result(timeout=1)
                        results[agent.agent_id] = result
                        processed.add(agent.agent_id)
                    except TimeoutError:
                        results[agent.agent_id] = ParallelResult(
                            phase=phase_num,
                            agent_id=agent.agent_id,
                            result=None,
                            elapsed_ms=timeout_per_agent * 1000,
                            thread_id=0,
                            status="timeout",
                            error=f"Timeout after {timeout_per_agent}s"
                        )
                    except Exception as e:
                        results[agent.agent_id] = ParallelResult(
                            phase=phase_num,
                            agent_id=agent.agent_id,
                            result=None,
                            elapsed_ms=0.1,
                            thread_id=0,
                            status="failed",
                            error=str(e)
                        )
            except TimeoutError:
                batch_timed_out = True
                for future, agent in future_to_agent.items():
                    if agent.agent_id not in processed:
                        future.cancel()
                        results[agent.agent_id] = ParallelResult(
                            phase=phase_num,
                            agent_id=agent.agent_id,
                            result=None,
                            elapsed_ms=timeout_per_agent * 1000,
                            thread_id=0,
                            status="timeout",
                            error=f"Batch timeout after {timeout_per_agent}s"
                        )
        finally:
            # Não esperar threads em execução terminarem (shutdown wait=False)
            executor.shutdown(wait=False)
        
        # Adiciona agentes skipped
        for aid in skipped_agents:
            results[aid] = ParallelResult(
                phase=phase_num,
                agent_id=aid,
                result=None,
                elapsed_ms=0.1,
                thread_id=0,
                status="skipped",
                error="Dependencies not satisfied"
            )
        
        return results
    
    def _execute_agent(
        self,
        agent: ReasoningAgent,
        context: dict,
        phase_num: int
    ) -> ParallelResult:
        """Executa um único agente e mede tempo."""
        agent_start = time.time()
        thread_id = threading.get_ident()
        
        try:
            result = agent.reason(context)
            elapsed = max((time.time() - agent_start) * 1000, 0.1)  # floor 0.1ms
            
            return ParallelResult(
                phase=phase_num,
                agent_id=agent.agent_id,
                result=result,
                elapsed_ms=elapsed,
                thread_id=thread_id,
                status="success",
            )
        except Exception as e:
            elapsed = max((time.time() - agent_start) * 1000, 0.1)  # floor 0.1ms
            return ParallelResult(
                phase=phase_num,
                agent_id=agent.agent_id,
                result=None,
                elapsed_ms=elapsed,
                thread_id=thread_id,
                status="failed",
                error=str(e),
            )
    
    def compute_metrics(
        self,
        phase_num: int,
        results: dict[str, ParallelResult],
        estimated_sequential_ms: float = None
    ) -> PhaseMetrics:
        """Computa métricas da execução paralela."""
        succeeded = sum(1 for r in results.values() if r.status == "success")
        failed = sum(1 for r in results.values() if r.status == "failed")
        skipped = sum(1 for r in results.values() if r.status == "skipped")
        
        max_elapsed = max(
            (r.elapsed_ms for r in results.values() if r.status in ("success", "failed")),
            default=0
        )
        
        if estimated_sequential_ms is None:
            estimated_sequential_ms = sum(
                r.elapsed_ms for r in results.values()
                if r.status in ("success", "failed")
            )
        
        speedup = estimated_sequential_ms / max(max_elapsed, 1)
        
        return PhaseMetrics(
            phase=phase_num,
            total_agents=len(results),
            succeeded=succeeded,
            failed=failed,
            skipped=skipped,
            total_elapsed_ms=max_elapsed,
            speedup_vs_sequential=speedup,
        )
    
    def merge_results_into_context(
        self,
        context: dict,
        results: dict[str, ParallelResult]
    ) -> dict:
        """Mescla resultados paralelos no contexto para fases seguintes."""
        for aid, pr in results.items():
            if pr.status == "success" and pr.result is not None:
                context["agent_results"][aid] = pr.result
        return context
