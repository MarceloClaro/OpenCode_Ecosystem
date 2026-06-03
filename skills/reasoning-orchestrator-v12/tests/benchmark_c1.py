#!/usr/bin/env python
# =====================================================================
# BENCHMARK C1 — Paralelo vs Sequencial (v12 vs v11)
# =====================================================================
# Mede speedup real, eficiência, overhead e lei de Amdahl.
# Compara execução paralela (ParallelDispatch) com sequencial (v11-style).
#
# Uso: python tests/benchmark_c1.py
# =====================================================================
import sys, os, time, json, math
from dataclasses import dataclass, field
from typing import Optional

# Path
V12_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents")
V11_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                         "..", "reasoning-orchestrator-v11", "agents")
sys.path.insert(0, V12_PATH)
sys.path.insert(0, V11_PATH)

from framework import ReasoningAgent, ReasoningResult, REASONING_REGISTRY
from parallel_dispatch import ParallelDispatch, ParallelResult, PhaseMetrics


# =====================================================================
# AGENTE DE BENCHMARK — simula tempo de raciocínio realista
# =====================================================================

class BenchmarkAgent(ReasoningAgent):
    """Agente sintético para benchmark com tempo de computação configurável.
    
    Simula o custo computacional de agentes reais do v11 sem
    depender da lógica de raciocínio propriamente dita.
    """
    def __init__(self, agent_id: str, reasoning_type: str,
                 compute_time: float, category: str = "I"):
        super().__init__(agent_id, reasoning_type, category)
        self._compute_time = compute_time
    
    def reason(self, ctx: dict) -> ReasoningResult:
        if self._compute_time > 0:
            time.sleep(self._compute_time)
        return ReasoningResult(
            agent_id=self.agent_id,
            reasoning_type=self.reasoning_type,
            category=self.category,
            conclusion=f"Benchmark result from {self.agent_id} ({self._compute_time:.3f}s)",
            confidence=max(0.5, min(1.0, 1.0 - self._compute_time * 0.2)),
        )
    
    def get_dependencies(self) -> list:
        return []
    
    def validate_dependencies(self, ctx: dict) -> bool:
        return True


# =====================================================================
# CONFIGURAÇÕES DE AGENTES POR FASE (inspirado no v11)
# =====================================================================
# v11 real: F1=3, F2=3, F3=4, F4=2, F5=3, F6=3, F7=1 agentes
# Tempos: distribuição log-normal simulando complexidade real

PHASE_AGENTS = {
    1: [  # Problem Analysis (v11: 3 agents)
        ("notation", 0.12),
        ("abstraction", 0.18),
        ("modular", 0.08),
    ],
    2: [  # Reasoning Selection (v11: 3 agents)
        ("inductor", 0.15),
        ("basecase", 0.10),
        ("induction", 0.22),
    ],
    3: [  # Deductive Derivation (v11: 4 agents)
        ("lemma_tracker", 0.05),
        ("deductive_chain", 0.25),
        ("backward_chain", 0.20),
        ("quantificational", 0.15),
    ],
    4: [  # Inductive Verification (v11: 2 agents)
        ("constructor", 0.30),
        ("stress_test", 0.45),
    ],
    5: [  # Cross-Reference (v11: 3 agents)
        ("contradiction", 0.20),
        ("contraexemplo", 0.35),
        ("reductio", 0.18),
    ],
    6: [  # Proof Health Check (v11: 3 agents)
        ("exhaustive", 0.50),
        ("cross_ref", 0.12),
        ("enumeration", 0.28),
    ],
    7: [  # Synthesis (v11: 1 agent)
        ("generalization", 0.10),
    ],
}


def create_benchmark_agents(scale: float = 1.0) -> dict[int, list[BenchmarkAgent]]:
    """Cria agentes de benchmark com tempos escalados.
    
    Args:
        scale: Fator de escala (1.0 = tempos reais, 0.5 = metade, 2.0 = dobro)
    
    Returns:
        dict[phase_num, list[BenchmarkAgent]]
    """
    phases = {}
    for phase, agents_config in PHASE_AGENTS.items():
        agents = []
        for name, time_s in agents_config:
            agent = BenchmarkAgent(
                agent_id=f"b-agent-{phase}-{name}",
                reasoning_type=f"R{phase}{name[:3].upper()}",
                compute_time=time_s * scale,
            )
            agents.append(agent)
        phases[phase] = agents
    return phases


# =====================================================================
# EXECUTOR SEQUENCIAL (simula v11)
# =====================================================================

@dataclass
class SequentialRun:
    """Resultado de uma execução sequencial."""
    phase_times_ms: dict[int, float]
    agent_times_ms: dict[str, float]
    total_ms: float
    total_agents: int
    succeeded: int


def run_sequential(phases: dict[int, list]) -> SequentialRun:
    """Executa todas as fases sequencialmente (como v11).
    
    Cada fase executa agentes um por um, sem paralelismo.
    """
    phase_times = {}
    agent_times = {}
    total_agents = 0
    succeeded = 0
    
    for phase in sorted(phases.keys()):
        phase_start = time.time()
        for agent in phases[phase]:
            total_agents += 1
            agent_start = time.time()
            try:
                result = agent.reason({
                    "problem": "benchmark",
                    "agent_results": {},
                    "mode": "sequential",
                })
                elapsed = (time.time() - agent_start) * 1000
                agent_times[agent.agent_id] = elapsed
                if result.confidence > 0:
                    succeeded += 1
            except Exception:
                pass
        phase_times[phase] = (time.time() - phase_start) * 1000
    
    total_ms = sum(phase_times.values())
    return SequentialRun(
        phase_times_ms=phase_times,
        agent_times_ms=agent_times,
        total_ms=total_ms,
        total_agents=total_agents,
        succeeded=succeeded,
    )


# =====================================================================
# EXECUTOR PARALELO (v12 ParallelDispatch)
# =====================================================================

@dataclass
class ParallelRun:
    """Resultado de uma execução paralela."""
    phase_times_ms: dict[int, float]
    total_ms: float
    total_agents: int
    succeeded: int
    failed: int
    skipped: int
    speedup: float
    efficiency: float
    estimated_sequential_ms: float


def run_parallel(phases: dict[int, list],
                 max_workers: int = 4,
                 timeout: float = 60.0) -> ParallelRun:
    """Executa todas as fases em paralelo (v12 ParallelDispatch).
    
    Dentro de cada fase, agentes rodam em paralelo.
    Fases ainda são sequenciais (respeitando dependências).
    """
    dispatch = ParallelDispatch()
    context = {"problem": "benchmark", "agent_results": {}, "mode": "parallel"}
    phase_times = {}
    total_agents = 0
    succeeded = 0
    failed = 0
    skipped = 0
    estimated_seq = 0.0
    
    for phase in sorted(phases.keys()):
        phase_start = time.time()
        
        results = dispatch.dispatch_phase(
            agents=phases[phase],
            context=context,
            max_workers=max_workers,
            timeout_per_agent=timeout,
            phase_num=phase,
        )
        
        context = dispatch.merge_results_into_context(context, results)
        phase_elapsed = (time.time() - phase_start) * 1000
        phase_times[phase] = phase_elapsed
        
        for aid, pr in results.items():
            total_agents += 1
            estimated_seq += pr.elapsed_ms
            if pr.status == "success":
                succeeded += 1
            elif pr.status == "failed":
                failed += 1
            elif pr.status == "skipped":
                skipped += 1
    
    total_ms = sum(phase_times.values())
    speedup = estimated_seq / max(total_ms, 1)
    efficiency = speedup / max_workers
    
    return ParallelRun(
        phase_times_ms=phase_times,
        total_ms=total_ms,
        total_agents=total_agents,
        succeeded=succeeded,
        failed=failed,
        skipped=skipped,
        speedup=speedup,
        efficiency=efficiency,
        estimated_sequential_ms=estimated_seq,
    )


# =====================================================================
# REPORT
# =====================================================================

@dataclass
class BenchmarkResult:
    """Resultado completo do benchmark."""
    scale: float
    max_workers: int
    sequential: SequentialRun
    parallel: ParallelRun
    speedup: float
    efficiency: float
    overhead_ms: float
    amdahl_max_speedup: float
    
    def summary_dict(self) -> dict:
        return {
            "scale": self.scale,
            "max_workers": self.max_workers,
            "sequential_ms": round(self.sequential.total_ms, 2),
            "parallel_ms": round(self.parallel.total_ms, 2),
            "estimated_sequential_ms": round(self.parallel.estimated_sequential_ms, 2),
            "speedup": round(self.speedup, 3),
            "efficiency": round(self.efficiency, 3),
            "overhead_ms": round(self.overhead_ms, 2),
            "amdahl_max_speedup": round(self.amdahl_max_speedup, 3),
            "total_agents": self.sequential.total_agents,
            "phase_times_seq": {str(k): round(v, 2) for k, v in self.sequential.phase_times_ms.items()},
            "phase_times_par": {str(k): round(v, 2) for k, v in self.parallel.phase_times_ms.items()},
        }


def run_benchmark(scale: float = 1.0, workers: int = 4) -> BenchmarkResult:
    """Executa benchmark completo para uma configuração.
    
    Args:
        scale: Fator de escala para tempos de computação
        workers: Número de workers paralelos
    
    Returns:
        BenchmarkResult com métricas comparativas
    """
    agents = create_benchmark_agents(scale=scale)
    
    print(f"\n{'='*60}")
    print(f"BENCHMARK C1 — ParallelDispatch vs Sequential")
    print(f"Scale: {scale}x | Max workers: {workers}")
    print(f"Total agents: {sum(len(a) for a in agents.values())} em {len(agents)} fases")
    print(f"{'='*60}")
    
    # Sequencial
    print(f"\n--- Execução Sequencial (v11) ---")
    seq_start = time.time()
    sequential = run_sequential(agents)
    seq_wall = (time.time() - seq_start) * 1000
    print(f"  Tempo total: {sequential.total_ms:.2f}ms (wall: {seq_wall:.2f}ms)")
    for p, t in sequential.phase_times_ms.items():
        print(f"  Fase {p}: {t:.2f}ms")
    
    # Paralelo
    print(f"\n--- Execução Paralela (v12) ---")
    par_start = time.time()
    parallel = run_parallel(agents, max_workers=workers)
    par_wall = (time.time() - par_start) * 1000
    print(f"  Tempo total: {parallel.total_ms:.2f}ms (wall: {par_wall:.2f}ms)")
    for p, t in parallel.phase_times_ms.items():
        print(f"  Fase {p}: {t:.2f}ms")
    
    # Métricas
    speedup = sequential.total_ms / max(parallel.total_ms, 1)
    efficiency = speedup / workers
    overhead = parallel.total_ms - (parallel.estimated_sequential_ms / workers)
    amdahl_max = 1 / (1 - 0.7)  # 70% paralelizável
    
    print(f"\n--- Resultados ---")
    print(f"  Speedup: {speedup:.3f}x")
    print(f"  Eficiência: {efficiency:.3f}")
    print(f"  Overhead: {overhead:.2f}ms")
    print(f"  Amdahl max (70% paralelizável): {amdahl_max:.3f}x")
    print(f"  Sequencial: {sequential.total_ms:.2f}ms")
    print(f"  Paralelo: {parallel.total_ms:.2f}ms")
    print(f"  Estimado seq (soma individuais): {parallel.estimated_sequential_ms:.2f}ms")
    
    return BenchmarkResult(
        scale=scale,
        max_workers=workers,
        sequential=sequential,
        parallel=parallel,
        speedup=speedup,
        efficiency=efficiency,
        overhead_ms=overhead,
        amdahl_max_speedup=amdahl_max,
    )


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("BENCHMARK C1 — Parallel Thinking v12 vs Sequential v11")
    print("=" * 60)
    
    results = []
    
    # Teste 1: Scale 1.0, workers=4 (config Standard)
    print("\n" + "#" * 60)
    print("# TESTE 1: Scale=1.0, Workers=4 (Modo Standard)")
    print("#" * 60)
    r1 = run_benchmark(scale=1.0, workers=4)
    results.append(r1)
    
    # Teste 2: Scale 2.0, workers=4 (problemas mais complexos)
    print("\n" + "#" * 60)
    print("# TESTE 2: Scale=2.0, Workers=4 (Problemas Complexos)")
    print("#" * 60)
    r2 = run_benchmark(scale=2.0, workers=4)
    results.append(r2)
    
    # Teste 3: Scale 1.0, workers=2 (Modo Express)
    print("\n" + "#" * 60)
    print("# TESTE 3: Scale=1.0, Workers=2 (Modo Express)")
    print("#" * 60)
    r3 = run_benchmark(scale=1.0, workers=2)
    results.append(r3)
    
    # Teste 4: Scale 1.0, workers=8 (Modo Research)
    print("\n" + "#" * 60)
    print("# TESTE 4: Scale=1.0, Workers=8 (Modo Research)")
    print("#" * 60)
    r4 = run_benchmark(scale=1.0, workers=8)
    results.append(r4)
    
    # Tabela comparativa
    print("\n" + "=" * 60)
    print("TABELA COMPARATIVA")
    print("=" * 60)
    print(f"{'Config':<25} {'Seq(ms)':<10} {'Par(ms)':<10} {'Speedup':<10} {'Efic':<10} {'Overhead(ms)':<12}")
    print("-" * 77)
    for r in results:
        config = f"Scale={r.scale}x W={r.max_workers}"
        print(f"{config:<25} {r.sequential.total_ms:<10.2f} {r.parallel.total_ms:<10.2f} {r.speedup:<10.3f} {r.efficiency:<10.3f} {r.overhead_ms:<12.2f}")
    
    # Export
    output = {
        "benchmark": "C1 - ParallelDispatch vs Sequential",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "tests": [r.summary_dict() for r in results],
    }
    out_path = os.path.join(os.path.dirname(__file__), "..", "docs", "benchmark_c1_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\nResultados exportados: {out_path}")
