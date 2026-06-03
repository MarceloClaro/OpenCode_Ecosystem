#!/usr/bin/env python
# =====================================================================
# BENCHMARK C5 — Integração do Pipeline (FullPipeline)
# =====================================================================
# Mede speedup real da execução multi-cadeia via ProcessPoolExecutor,
# eficiência de paralelismo, overhead de scheduling e seleção de
# estratégia.
#
# Estrutura:
#   Parte 1: Raw ProcessPoolExecutor Benchmark (chain-level)
#   Parte 2: Strategy Selection Correctness (FullPipeline)
#   Parte 3: FullPipeline End-to-End (opcional, real)
#
# Uso: python tests/benchmark_c5.py
# =====================================================================
import sys, os, time, json, math
from dataclasses import dataclass, field
from typing import Optional
from concurrent.futures import ProcessPoolExecutor, as_completed

# Path setup
V12_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "agents")
sys.path.insert(0, V12_PATH)

# =====================================================================
# PARTE 0: FUNÇÃO PICKLABLE PARA ProcessPoolExecutor
# =====================================================================
# Necessário no Windows — funções de módulo são serializáveis.

def _benchmark_chain(compute_seconds: float, chain_id: int) -> dict:
    """Função picklable que simula uma cadeia de raciocínio.
    
    Args:
        compute_seconds: Tempo de computação simulado (time.sleep)
        chain_id: Identificador da cadeia
    
    Returns:
        dict com métricas da execução
    """
    import time, os
    start = time.time()
    time.sleep(compute_seconds)
    elapsed = (time.time() - start) * 1000
    return {
        "chain_id": chain_id,
        "compute_time": compute_seconds,
        "elapsed_ms": round(elapsed, 2),
        "pid": os.getpid(),
    }


# =====================================================================
# PARTE 1: RAW ProcessPoolExecutor BENCHMARK
# =====================================================================

# Configurações de cadeias (match DEFAULT_CHAIN_MODES)
CHAIN_CONFIGS = [
    {"mode": "express",  "budget": 30,  "workers": 1, "time": 0.5},
    {"mode": "standard", "budget": 60,  "workers": 2, "time": 1.0},
    {"mode": "magnum",   "budget": 100, "workers": 4, "time": 1.5},
    {"mode": "research", "budget": 200, "workers": 8, "time": 2.0},
]


@dataclass
class RawBenchmarkResult:
    """Resultado de uma execução do benchmark raw."""
    worker_count: int
    compute_scale: float
    num_chains: int
    sequential_ms: float
    parallel_ms: float
    speedup: float
    efficiency: float
    overhead_ms: float
    chain_times_seq: list[float]
    chain_times_par: list[float]
    
    def to_dict(self) -> dict:
        return {
            "worker_count": self.worker_count,
            "compute_scale": self.compute_scale,
            "num_chains": self.num_chains,
            "sequential_ms": round(self.sequential_ms, 2),
            "parallel_ms": round(self.parallel_ms, 2),
            "speedup": round(self.speedup, 3),
            "efficiency": round(self.efficiency, 3),
            "overhead_ms": round(self.overhead_ms, 2),
        }


def build_tasks(num_chains: int, compute_scale: float) -> list[tuple[float, int]]:
    """Constrói lista de tarefas (compute_time, chain_id).
    
    Distribui tempos proporcionais aos budgets do DEFAULT_CHAIN_MODES,
    escalados pelo fator compute_scale.
    """
    chain_times = [
        cfg["time"] * compute_scale
        for cfg in CHAIN_CONFIGS[:num_chains]
    ]
    return [(t, i) for i, t in enumerate(chain_times)]


def run_parallel(tasks: list[tuple[float, int]],
                 max_workers: int) -> list[dict]:
    """Executa tarefas em paralelo via ProcessPoolExecutor.
    
    Args:
        tasks: Lista de (compute_time, chain_id)
        max_workers: Número máximo de workers
    
    Returns:
        Lista de resultados ordenados por chain_id
    """
    results = []
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {
            executor.submit(_benchmark_chain, ct, cid): cid
            for ct, cid in tasks
        }
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                cid = futures[future]
                results.append({
                    "chain_id": cid,
                    "compute_time": 0,
                    "elapsed_ms": 0,
                    "error": str(e),
                })
    results.sort(key=lambda r: r["chain_id"])
    return results


def run_sequential(tasks: list[tuple[float, int]]) -> list[dict]:
    """Executa tarefas sequencialmente (baseline).
    
    Args:
        tasks: Lista de (compute_time, chain_id)
    
    Returns:
        Lista de resultados ordenados por chain_id
    """
    results = []
    for ct, cid in tasks:
        results.append(_benchmark_chain(ct, cid))
    return results


def run_benchmark_raw(tasks: list[tuple[float, int]],
                      max_workers: int = 4) -> dict:
    """Executa benchmark raw comparando paralelo vs sequencial.
    
    Args:
        tasks: Lista de (compute_time, chain_id)
        max_workers: Número de workers paralelos
    
    Returns:
        Dicionário com métricas (speedup, eficiência, overhead)
    """
    # Sequencial
    seq_results = run_sequential(tasks)
    seq_ms = sum(r["elapsed_ms"] for r in seq_results)
    seq_times = [r["elapsed_ms"] for r in seq_results]
    
    # Paralelo
    par_start = time.time()
    par_results = run_parallel(tasks, max_workers=max_workers)
    par_wall = (time.time() - par_start) * 1000
    par_times = [r["elapsed_ms"] for r in par_results]
    max_par = max(par_times) if par_times else 1
    
    # Métricas
    # speedup = T_seq / T_par (wall-clock do paralelo)
    speedup = seq_ms / max(par_wall, 1)
    efficiency = speedup / max_workers
    # overhead = T_par - (T_seq / W)  # Amdahl ideal
    ideal_par = seq_ms / max_workers
    overhead = max(par_wall - ideal_par, 0)
    
    return {
        "worker_count": max_workers,
        "compute_scale": tasks[0][0] / 0.5 if tasks else 0,
        "num_chains": len(tasks),
        "sequential_ms": round(seq_ms, 2),
        "parallel_ms": round(par_wall, 2),
        "speedup": round(speedup, 3),
        "efficiency": round(efficiency, 3),
        "overhead_ms": round(overhead, 2),
        "chain_times_seq": [round(t, 2) for t in seq_times],
        "chain_times_par": [round(t, 2) for t in par_times],
    }


# =====================================================================
# PARTE 2: STRATEGY SELECTION CORRECTNESS
# =====================================================================

from full_pipeline import FullPipeline, ProblemProfile


DOMAIN_EXPECTED = {
    "Prove that sqrt(2) is irrational": "weighted_vote",
    "Implement a binary search tree in Python": "weighted_vote",
    "Calculate the escape velocity from Earth": "weighted_vote",
    "Debate the pros and cons of AI regulation": "debate",
    "Design a novel renewable energy system": "ensemble",
    "What is 2 + 2?": "best_of",
}


def test_strategy_selection() -> list[dict]:
    """Verifica seleção de estratégia em problemas reais."""
    pipeline = FullPipeline()
    results = []
    
    print("\n" + "=" * 60)
    print("PARTE 2: Strategy Selection Correctness")
    print("=" * 60)
    
    all_correct = True
    for problem, expected in DOMAIN_EXPECTED.items():
        profile = pipeline.analyze_problem(problem)
        strategy = pipeline.select_strategy(profile)
        correct = strategy == expected
        if not correct:
            all_correct = False
        
        status = "[OK]" if correct else "[FAIL]"
        print(f"  {status} [{profile.domain:>10}] {problem[:55]:<55} -> {strategy:<15} (esperado: {expected})")
        
        results.append({
            "problem": problem,
            "domain": profile.domain,
            "complexity": profile.complexity,
            "strategy": strategy,
            "expected": expected,
            "correct": correct,
        })
    
    print(f"\n  Resultado: {sum(1 for r in results if r['correct'])}/{len(results)} corretos")
    print(f"  {'[OK] TODOS CORRETOS' if all_correct else '[FAIL] HÁ FALHAS'}")
    
    return results


# =====================================================================
# PARTE 3: FULL PIPELINE END-TO-END
# =====================================================================

def run_pipeline_benchmark() -> list[dict]:
    """Executa FullPipeline.run_with_benchmark() em problemas reais.
    
    AVISO: Esta parte executa agentes reais (não simulados) e pode
    levar minutos para completar. Os resultados variam conforme o
    hardware e a carga do sistema.
    """
    from full_pipeline import FullPipeline
    
    problems = [
        "Prove that sqrt(2) is irrational",
        "What is 2 + 2?",
    ]
    
    results = []
    print("\n" + "=" * 60)
    print("PARTE 3: FullPipeline End-to-End")
    print("(agentes reais — pode levar minutos)")
    print("=" * 60)
    
    for problem in problems:
        print(f"\n  Problema: {problem}")
        start = time.time()
        pipeline = FullPipeline()
        try:
            benchmark = pipeline.run_with_benchmark(problem)
            elapsed = (time.time() - start) * 1000
            
            result = {
                "problem": problem,
                "total_elapsed_ms": round(benchmark.total_elapsed_ms, 2),
                "wall_clock_ms": round(elapsed, 2),
                "chain_count": benchmark.chain_count,
                "chain_times_ms": [round(t, 2) for t in benchmark.chain_times_ms],
                "synthesis_time_ms": round(benchmark.synthesis_time_ms, 2),
                "speedup_vs_sequential": benchmark.speedup_vs_sequential,
                "mean_pci": benchmark.mean_pci,
                "strategy_used": benchmark.strategy_used,
                "synthesis_confidence": round(benchmark.synthesis_confidence, 3),
            }
            results.append(result)
            
            print(f"    Chains: {benchmark.chain_count}")
            print(f"    Speedup: {benchmark.speedup_vs_sequential:.2f}x")
            print(f"    PCI médio: {benchmark.mean_pci:.2f}")
            print(f"    Estratégia: {benchmark.strategy_used}")
            print(f"    Confiança: {benchmark.synthesis_confidence:.2f}")
            print(f"    Tempo total: {benchmark.total_elapsed_ms:.0f}ms")
            
        except Exception as e:
            print(f"    ERRO: {e}")
            results.append({
                "problem": problem,
                "error": str(e),
            })
    
    return results


# =====================================================================
# MAIN
# =====================================================================

if __name__ == "__main__":
    import platform
    
    print("=" * 60)
    print("BENCHMARK C5 — Pipeline Integration Benchmark")
    print("=" * 60)
    print(f"Sistema: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version.split()[0]}")
    print(f"CPU lógico: {os.cpu_count() or 'desconhecido'}")
    print(f"Horário: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # ==================================================================
    # PARTE 1: Raw ProcessPoolExecutor Benchmark
    # ==================================================================
    print("\n" + "=" * 60)
    print("PARTE 1: Raw ProcessPoolExecutor Benchmark")
    print("=" * 60)
    
    all_raw_results = []
    worker_counts = [1, 2, 4, 8]
    compute_scales = [0.5, 1.0, 2.0]
    num_chains = len(CHAIN_CONFIGS)  # 4
    
    for scale in compute_scales:
        tasks = build_tasks(num_chains, scale)
        print(f"\n--- Compute Scale: {scale}x ({num_chains} chains) ---")
        for w in worker_counts:
            result = run_benchmark_raw(tasks, max_workers=w)
            all_raw_results.append(result)
            print(f"  W={w:2d} | Seq={result['sequential_ms']:8.2f}ms "
                  f"| Par={result['parallel_ms']:8.2f}ms "
                  f"| Speedup={result['speedup']:6.3f}x "
                  f"| Efic={result['efficiency']:.3f}")
    
    # Tabela comparativa
    print("\n" + "=" * 60)
    print("TABELA COMPARATIVA — Speedup por Configuração")
    print("=" * 60)
    header = f"{'Scale':>6} {'W':>3} {'Seq(ms)':>10} {'Par(ms)':>10} {'Speedup':>10} {'Efic':>6} {'Over(ms)':>10}"
    print(header)
    print("-" * len(header))
    for r in all_raw_results:
        print(f"{r['compute_scale']:>6.1f} {r['worker_count']:>3d} {r['sequential_ms']:>10.2f} {r['parallel_ms']:>10.2f} {r['speedup']:>10.3f} {r['efficiency']:>6.3f} {r['overhead_ms']:>10.2f}")
    
    # ==================================================================
    # PARTE 2: Strategy Selection
    # ==================================================================
    strategy_results = test_strategy_selection()
    
    # ==================================================================
    # PARTE 3: FullPipeline End-to-End (opcional, comentado por padrão)
    # ==================================================================
    pipeline_results = []
    # Descomente para executar agentes reais:
    # pipeline_results = run_pipeline_benchmark()
    
    # ==================================================================
    # EXPORT
    # ==================================================================
    output = {
        "benchmark": "C5 - Pipeline Integration Benchmark",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "system": {
            "platform": platform.system(),
            "python": sys.version.split()[0],
            "cpu_logical": os.cpu_count(),
        },
        "raw_benchmark": all_raw_results,
        "strategy_selection": strategy_results,
        "pipeline_end_to_end": pipeline_results,
    }
    
    out_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "docs", "benchmark_c5_results.json",
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"\n{'='*60}")
    print(f"Resultados exportados: {out_path}")
    print(f"{'='*60}")
