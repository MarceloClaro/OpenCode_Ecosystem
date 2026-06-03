#!/usr/bin/env python3
"""
AUTOEVOLVE - Phase 4 Quick Test
================================

Executa validação rápida (5 problemas) para:
1. Validar pipeline imports
2. Testar cada componente
3. Coletar métricas iniciais
4. Decidir próximos passos
"""

import asyncio
import sys
import traceback
from pathlib import Path

# Add references to path
sys.path.insert(0, str(Path(__file__).parent / "references"))

async def test_imports():
    """Step 1: Validar todos os imports"""
    print("[STEP 1] Validating imports...")
    try:
        from prover_agent import ProverAgent, ProofAttempt
        print("  ✅ ProverAgent")
        
        from reasoning_orchestrator_v11 import create_orchestrator
        print("  ✅ ReasoningOrchestrator-v11")
        
        from debate_arena import DebateArena, DebatePhase
        print("  ✅ DebateArena")
        
        from mcp_enricher import create_mcp_enricher
        print("  ✅ MCPEnricher")
        
        from refinement_agent import RefinementAgent, DebateResult
        print("  ✅ RefinementAgent")
        
        from imo_benchmark_adapter import IMOBenchmarkAdapter
        print("  ✅ IMOBenchmarkAdapter")
        
        from verifier_v7 import VerifierV7
        print("  ✅ VerifierV7")
        
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        traceback.print_exc()
        return False


async def test_components():
    """Step 2: Testar cada componente isoladamente"""
    print("\n[STEP 2] Testing components...")
    
    from prover_agent import ProverAgent, ProofAttempt, ProofStrategy
    from imo_benchmark_adapter import IMOBenchmarkAdapter
    from reasoning_orchestrator_v11 import create_orchestrator
    from debate_arena import DebateArena
    from mcp_enricher import create_mcp_enricher
    from refinement_agent import RefinementAgent, DebateResult
    
    adapter = IMOBenchmarkAdapter()
    problems = adapter.load_all_problems()
    
    if not problems:
        print("  ❌ No IMO problems loaded")
        return False
    
    problem = problems[0]
    print(f"  Testing with: {problem.problem_id}")
    
    try:
        # Test ProverAgent
        prover = ProverAgent()
        proofs = prover.generate_proofs(problem, num_strategies=2)
        print(f"  ✅ ProverAgent: generated {len(proofs)} proofs")
        
        # Test ReasoningOrchestrator
        reasoner = create_orchestrator()
        selection = reasoner.select_for_problem(problem, top_k=3)
        print(f"  ✅ ReasoningOrchestrator: selected {len(selection.selected_reasonings)} types")
        
        # Test DebateArena
        debate = DebateArena()
        best_proof = proofs[0]
        debate_result = debate.orchestrate_debate(best_proof)
        print(f"  ✅ DebateArena: consensus={debate_result.consensus_score:.2f}")
        
        # Test MCPEnricher
        mcp_enricher = create_mcp_enricher(timeout_per_mcp=1.0)
        enriched, mcp_results = await mcp_enricher.enrich_proof(
            best_proof.proof_text,
            problem,
            ["Direct Proof", "Induction"]
        )
        succeeded = sum(1 for r in mcp_results.values() if r.status.value in ["SUCCESS", "MOCK"])
        print(f"  ✅ MCPEnricher: {succeeded} MCPs succeeded")
        
        # Test RefinementAgent
        refiner = RefinementAgent()
        refined = refiner.refine_proof(best_proof, debate_result, original_d11_score=5.0)
        print(f"  ✅ RefinementAgent: refined score={refined.refined_score:.2f}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Component test failed: {e}")
        traceback.print_exc()
        return False


async def test_pipeline(num_problems: int = 5):
    """Step 3: Testar pipeline completa"""
    print(f"\n[STEP 3] Testing full pipeline with {num_problems} problems...")
    
    from validation_pipeline import ValidationPipeline
    
    try:
        pipeline = ValidationPipeline(use_real_v7=False, max_problems=num_problems)
        report = await pipeline.validate_all()
        
        print(f"\n[RESULTS]")
        print(f"  Completed: {report.problems_completed}/{report.total_problems}")
        print(f"  Success rate: {report.success_rate:.1%}")
        print(f"  Avg D11 original: {report.avg_d11_original:.2f}")
        print(f"  Avg D11 refined: {report.avg_d11_refined:.2f}")
        print(f"  Avg improvement: +{report.avg_improvement_ratio:+.1%}")
        print(f"  Avg total time: {report.avg_time_total:.2f}s")
        
        # Print timing breakdown
        print(f"\n[TIMING BREAKDOWN]")
        print(f"  ProverAgent:         {report.avg_time_prover:.3f}s")
        print(f"  ReasoningOrch:       {report.avg_time_reasoning:.3f}s")
        print(f"  DebateArena:         {report.avg_time_debate:.3f}s")
        print(f"  MCPEnricher:         {report.avg_time_mcp:.3f}s")
        print(f"  RefinementAgent:     {report.avg_time_refinement:.3f}s")
        
        return report.success_rate > 0.8
        
    except Exception as e:
        print(f"  ❌ Pipeline test failed: {e}")
        traceback.print_exc()
        return False


async def main():
    """Main test flow"""
    print("="*70)
    print("AUTOEVOLVE - PHASE 4 VALIDATION TEST")
    print("="*70)
    
    # Step 1: Imports
    if not await test_imports():
        print("\n❌ ABORTED: Import validation failed")
        return False
    
    # Step 2: Components
    if not await test_components():
        print("\n❌ ABORTED: Component testing failed")
        return False
    
    # Step 3: Pipeline
    success = await test_pipeline(num_problems=5)
    
    print("\n" + "="*70)
    if success:
        print("✅ PHASE 4 TEST PASSED - Ready for full validation")
        print("="*70)
        return True
    else:
        print("❌ PHASE 4 TEST FAILED - Debug needed")
        print("="*70)
        return False


if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
