#!/usr/bin/env python
# =====================================================================
# PARALLEL CHAIN v1 — Execução Multi-Cadeia via ProcessPoolExecutor
# =====================================================================
# Executa múltiplas cadeias de raciocínio (ParallelOrchestrator) em
# processos paralelos, cada cadeia com modo/budget independente.
# Resultados consolidados pelo SynthesisEngine.
# =====================================================================

import sys, os, time, math
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field
from typing import Optional


# Path setup para encontrar agentes
_V12_AGENTS = os.path.join(os.path.dirname(__file__))
if _V12_AGENTS not in sys.path:
    sys.path.insert(0, _V12_AGENTS)

_V11_PATH = os.path.join(os.path.dirname(__file__),
                         "..", "..", "reasoning-orchestrator-v11", "agents")
if _V11_PATH not in sys.path:
    sys.path.insert(0, _V11_PATH)


# =====================================================================
# DATA STRUCTURES
# =====================================================================

@dataclass
class ChainResult:
    """Resultado de uma cadeia de raciocínio."""
    chain_id: int
    mode: str
    budget: int
    solution_text: str
    pci_score: float
    elapsed_ms: float
    num_agents: int
    error: Optional[str] = None


@dataclass
class ChainConfig:
    """Configuração de uma cadeia."""
    mode: str = "standard"
    budget: int = 60
    workers: int = 2


# =====================================================================
# FUNÇÃO DE NÍVEL DE MÓDULO (picklable para Windows ProcessPool)
# =====================================================================

def _run_single_chain(problem: str, mode: str, budget: int,
                      workers: int, chain_id: int, verify: bool) -> ChainResult:
    """
    Executa uma cadeia única em subprocesso.
    Função de módulo necessária para Windows (pickle).
    """
    from orchestrator_v12 import ParallelOrchestrator
    from parallel_verifiers import ParallelVerifiers
    
    start = time.time()
    error = None
    
    try:
        orch = ParallelOrchestrator(mode=mode)
        orch.config.budget = budget
        orch.config.intra_phase_workers = workers
        
        report = orch.solve(problem)
        
        if verify:
            pv = ParallelVerifiers(max_workers=workers)
            context = {
                "solution_text": str(report.final_answer),
                "problem": problem,
                "agent_results": report.agent_results,
            }
            consensus = pv.verify_parallel(context)
            verification_info = f" | verification_score={consensus.weighted_score}"
        else:
            verification_info = ""
        
        elapsed = (time.time() - start) * 1000
        
        return ChainResult(
            chain_id=chain_id,
            mode=mode,
            budget=budget,
            solution_text=str(report.final_answer),
            pci_score=report.pci_score,
            elapsed_ms=elapsed,
            num_agents=report.num_agents_executed,
        )
    except Exception as e:
        elapsed = (time.time() - start) * 1000
        return ChainResult(
            chain_id=chain_id,
            mode=mode,
            budget=budget,
            solution_text=f"Error: {str(e)}",
            pci_score=0.0,
            elapsed_ms=elapsed,
            num_agents=0,
            error=str(e),
        )


# =====================================================================
# PARALLEL CHAIN
# =====================================================================

DEFAULT_CHAIN_MODES = [
    {"mode": "express",  "budget": 30,  "workers": 1},
    {"mode": "standard", "budget": 60,  "workers": 2},
    {"mode": "magnum",   "budget": 100, "workers": 4},
    {"mode": "research", "budget": 200, "workers": 8},
]


class ParallelChain:
    """
    Executa múltiplas cadeias de raciocínio em ProcessPoolExecutor.
    
    Cada cadeia roda em um processo separado com seu próprio modo/budget,
    garantindo isolamento completo entre cadeias.
    """
    
    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers
    
    def run_chains(
        self,
        problem: str,
        chain_configs: Optional[list[dict]] = None,
        verify: bool = False,
    ) -> list[ChainResult]:
        """
        Executa N cadeias em paralelo via ProcessPoolExecutor.
        
        Args:
            problem: Problema a ser resolvido
            chain_configs: Lista de configs (mode, budget, workers).
                Se None, usa DEFAULT_CHAIN_MODES.
            verify: Se True, executa verificação V1-V7 em cada cadeia
        
        Returns:
            Lista de ChainResult, um por cadeia
        """
        if chain_configs is None:
            chain_configs = DEFAULT_CHAIN_MODES
        
        results: list[ChainResult] = []
        
        # Em Windows, ProcessPoolExecutor requer função picklable
        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_map = {}
            for i, cfg in enumerate(chain_configs):
                future = executor.submit(
                    _run_single_chain,
                    problem,
                    cfg.get("mode", "standard"),
                    cfg.get("budget", 60),
                    cfg.get("workers", 2),
                    i + 1,
                    verify,
                )
                future_map[future] = i
            
            for future in as_completed(future_map):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    idx = future_map[future]
                    cfg = chain_configs[idx] if idx < len(chain_configs) else {}
                    results.append(ChainResult(
                        chain_id=idx + 1,
                        mode=cfg.get("mode", "unknown"),
                        budget=cfg.get("budget", 0),
                        solution_text=f"Process error: {str(e)}",
                        pci_score=0.0,
                        elapsed_ms=0,
                        num_agents=0,
                        error=str(e),
                    ))
        
        # Ordena por chain_id
        results.sort(key=lambda r: r.chain_id)
        return results
    
    def run_sequential(
        self,
        problem: str,
        chain_configs: Optional[list[dict]] = None,
        verify: bool = False,
    ) -> list[ChainResult]:
        """
        Executa cadeias sequencialmente (baseline para benchmark).
        Útil para comparar speedup.
        """
        if chain_configs is None:
            chain_configs = DEFAULT_CHAIN_MODES
        
        results = []
        for i, cfg in enumerate(chain_configs):
            result = _run_single_chain(
                problem,
                cfg.get("mode", "standard"),
                cfg.get("budget", 60),
                cfg.get("workers", 2),
                i + 1,
                verify,
            )
            results.append(result)
        
        return results
