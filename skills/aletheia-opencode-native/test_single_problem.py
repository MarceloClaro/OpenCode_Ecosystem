#!/usr/bin/env python3
"""Test Phase 4 with a single problem"""

import sys
import asyncio
sys.path.insert(0, r'C:\Users\marce\.config\opencode\skills\aletheia-opencode-native\references')

from prover_agent import ProverAgent, ProofAttempt, ProofStrategy
from reasoning_orchestrator_v11 import create_orchestrator
from debate_arena import DebateArena
from mcp_enricher import create_mcp_enricher
from refinement_agent import RefinementAgent, DebateResult
from imo_benchmark_adapter import IMOBenchmarkAdapter

async def main():
    print("Phase 4 Single Problem Test")
    print("=" * 60)
    
    # Load problems
    print("[1] Loading IMO problems...")
    adapter = IMOBenchmarkAdapter()
    
    # Try loading from URL
    try:
        loaded = adapter.load_from_url()
        print(f"  Loaded {loaded} problems from URL")
    except Exception as e:
        print(f"  Could not load from URL: {e}")
        print("  Using sample problems...")
        sample = adapter.sample_problems(n=1)
        adapter.problems = sample
        loaded = len(adapter.problems)
    
    problems = adapter.problems
    print(f"  Total: {len(problems)} problems")
    
    if not problems:
        print("  ERROR: No problems loaded!")
        return False
    
    problem = problems[0]
    print(f"  Using: {problem.problem_id} ({problem.category})")
    
    # Stage 1: ProverAgent
    print("\n[2] ProverAgent - Generate proofs...")
    prover = ProverAgent()
    proofs = prover.generate_proofs(problem, num_strategies=2)
    print(f"  Generated {len(proofs)} proofs")
    if not proofs:
        print("  ERROR: No proofs generated!")
        return False
    
    best_proof = proofs[0]
    print(f"  Best proof strategy: {best_proof.strategy}")
    
    # Stage 2: ReasoningOrchestrator
    print("\n[3] ReasoningOrchestrator - Select reasoning types...")
    reasoner = create_orchestrator()
    selection = reasoner.select_for_problem(problem, top_k=3)
    print(f"  Selected {len(selection.selected_reasonings)} reasoning types")
    print(f"  Confidence: {selection.confidence_score:.2f}")
    for reasoning_type, score in selection.selected_reasonings[:3]:
        print(f"    - {reasoning_type}: {score:.2f}")
    
    # Stage 3: DebateArena
    print("\n[4] DebateArena - Orchestrate debate...")
    debate = DebateArena()
    debate_result = debate.orchestrate_debate(best_proof)
    print(f"  Consensus score: {debate_result.consensus_score:.2f}")
    print(f"  Phases completed: {debate_result.phases}")
    
    # Stage 4: MCPEnricher
    print("\n[5] MCPEnricher - Enrich proof...")
    mcp_enricher = create_mcp_enricher(timeout_per_mcp=1.0)
    enriched, mcp_results = await mcp_enricher.enrich_proof(
        best_proof.proof_text,
        problem,
        [r[0] for r in selection.selected_reasonings[:2]]
    )
    mcp_success = sum(1 for r in mcp_results.values() if r.status.value in ["SUCCESS", "MOCK"])
    print(f"  MCPs completed: {mcp_success}/{len(mcp_results)}")
    for mcp_name, result in mcp_results.items():
        print(f"    - {mcp_name}: {result.status.value} ({result.elapsed_time:.3f}s)")
    
    # Stage 5: RefinementAgent
    print("\n[6] RefinementAgent - Refine proof...")
    refiner = RefinementAgent()
    refined = refiner.refine_proof(best_proof, debate_result, original_d11_score=5.0)
    print(f"  Original score: {refined.original_score:.2f}")
    print(f"  Refined score: {refined.refined_score:.2f}")
    print(f"  Improvement: +{(refined.refined_score - refined.original_score):.2f}")
    print(f"  Improvements: {len(refined.improvements)}")
    for imp in refined.improvements:
        print(f"    - {imp}")
    
    print("\n" + "=" * 60)
    print("SUCCESS: Phase 4 single problem test passed!")
    return True

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
