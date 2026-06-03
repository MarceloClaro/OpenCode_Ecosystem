#!/usr/bin/env python3
"""Phase 4 Validation: 5-60 problems with metrics collection"""

import sys
import json
import time
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional

sys.path.insert(0, r'C:\Users\marce\.config\opencode\skills\aletheia-opencode-native\references')

from imo_benchmark_adapter import IMOBenchmarkAdapter
from verifier_v7 import VerifierV7
from prover_agent import ProverAgent
from reasoning_orchestrator_v11 import create_orchestrator
from mcp_enricher import MCPEnricher
from refinement_agent import RefinementAgent, DebateResult

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ProblemMetrics:
    """Métricas por problema"""
    problem_id: str
    category: str
    level: int
    domain: str
    
    # D11 scores
    original_d11: float = 0.0
    refined_d11: float = 0.0
    improvement_ratio: float = 0.0  # (refined - original) / original
    
    # Pipeline stages
    time_original_score: float = 0.0
    time_prover: float = 0.0
    time_reasoner: float = 0.0
    time_enricher: float = 0.0
    time_refiner: float = 0.0
    time_refined_score: float = 0.0
    
    # Reasoning
    reasoning_types_selected: List[str] = field(default_factory=list)
    reasoning_confidence: float = 0.0
    
    # Results
    success: bool = True
    error: Optional[str] = None
    
    def total_time(self) -> float:
        return (self.time_original_score + self.time_prover + 
                self.time_reasoner + self.time_enricher + 
                self.time_refiner + self.time_refined_score)


@dataclass
class ValidationReport:
    """Relatório geral da validação"""
    num_problems: int = 0
    num_success: int = 0
    num_failed: int = 0
    
    avg_original_d11: float = 0.0
    avg_refined_d11: float = 0.0
    avg_improvement: float = 0.0
    
    avg_timing: Dict[str, float] = field(default_factory=dict)
    
    reasoning_types_frequency: Dict[str, int] = field(default_factory=dict)
    
    problems: List[ProblemMetrics] = field(default_factory=list)
    
    timestamp: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# VALIDATION ENGINE
# ============================================================================

class ValidationEngine:
    def __init__(self):
        self.adapter = IMOBenchmarkAdapter()
        self.verifier = VerifierV7()
        self.prover = ProverAgent()
        self.reasoner = create_orchestrator()
        self.enricher = MCPEnricher(timeout_per_mcp=1.0)
        self.refiner = RefinementAgent()
        
    def validate_problem(self, problem) -> ProblemMetrics:
        """Validate 1 problem through full pipeline"""
        metrics = ProblemMetrics(
            problem_id=problem.problem_id,
            category=problem.category,
            level=problem.difficulty_level,
            domain=problem.aletheia_domain
        )
        
        try:
            # Stage 1: Original score
            t0 = time.time()
            original_proof = {
                "proof_id": f"{problem.problem_id}_original",
                "text": "[Baseline - no proof attempt]",
                "domain": problem.aletheia_domain
            }
            original_assess = self.verifier.assess(original_proof)
            metrics.original_d11 = original_assess.overall_d11_score
            metrics.time_original_score = time.time() - t0
            print(f"  [1/6] Original score: {metrics.original_d11:.2f} ({metrics.time_original_score:.2f}s)")
            
            # Stage 2: ProverAgent
            t0 = time.time()
            proof_gen = self.prover.generate_proofs(problem, num_strategies=2)
            proofs = proof_gen.proofs
            metrics.time_prover = time.time() - t0
            print(f"  [2/6] Generated {len(proofs)} proofs ({metrics.time_prover:.2f}s)")
            
            if not proofs:
                raise Exception("No proofs generated")
            proof_attempt = proofs[0]
            
            # Stage 3: ReasoningOrchestrator
            t0 = time.time()
            reasoning_sel = self.reasoner.select_for_problem(problem, top_k=3)
            # selected_reasonings is List[Tuple[str, float]]
            metrics.reasoning_types_selected = [r[0] for r in reasoning_sel.selected_reasonings]
            metrics.reasoning_confidence = reasoning_sel.confidence_score
            metrics.time_reasoner = time.time() - t0
            print(f"  [3/6] Selected {len(metrics.reasoning_types_selected)} reasoning types ({metrics.time_reasoner:.2f}s)")
            
            # Stage 4: MCPEnricher (skip async, use mocks)
            t0 = time.time()
            # Simulated enrichment (no actual MCP calls yet)
            enriched_proof = f"[ENRICHED]\n{proof_attempt.proof_text}"
            metrics.time_enricher = time.time() - t0
            print(f"  [4/6] Enriched proof ({metrics.time_enricher:.2f}s)")
            
            # Stage 5: RefinementAgent
            t0 = time.time()
            debate_result = DebateResult(
                consensus_score=0.75,
                verifier_positions={"V1": 0.8, "V2": 0.7}
            )
            refined_result = self.refiner.refine_proof(
                proof_attempt, 
                debate_result,
                original_d11_score=metrics.original_d11
            )
            metrics.time_refiner = time.time() - t0
            print(f"  [5/6] Refined proof ({metrics.time_refiner:.2f}s)")
            
            # Stage 6: Score refined
            t0 = time.time()
            refined_proof_dict = {
                "proof_id": f"{problem.problem_id}_refined",
                "text": enriched_proof,
                "domain": problem.aletheia_domain
            }
            refined_assess = self.verifier.assess(refined_proof_dict)
            metrics.refined_d11 = refined_assess.overall_d11_score
            metrics.time_refined_score = time.time() - t0
            
            # Calculate improvement
            if metrics.original_d11 > 0:
                metrics.improvement_ratio = (metrics.refined_d11 - metrics.original_d11) / metrics.original_d11
            
            print(f"  [6/6] Refined score: {metrics.refined_d11:.2f} (ratio: {metrics.improvement_ratio:+.2%}) ({metrics.time_refined_score:.2f}s)")
            print(f"  Total time: {metrics.total_time():.2f}s")
            
            return metrics
            
        except Exception as e:
            metrics.success = False
            metrics.error = str(e)
            print(f"  ERROR: {e}")
            return metrics
    
    def validate_batch(self, num_problems: int = 5) -> ValidationReport:
        """Validate N problems"""
        print(f"\n{'='*70}")
        print(f"Phase 4 Validation: {num_problems} problems")
        print(f"{'='*70}\n")
        
        # Load problems
        print("[LOAD] Loading problems from IMO-ProofBench...")
        try:
            self.adapter.load_from_url()
        except Exception as e:
            print(f"  Warning: {e}, using samples")
            self.adapter.problems = self.adapter.sample_problems(n=num_problems)
        
        if not self.adapter.problems:
            raise Exception("No problems loaded")
        
        selected = self.adapter.problems[:num_problems]
        print(f"  Loaded {len(self.adapter.problems)} total, using {len(selected)}\n")
        
        # Validate each
        report = ValidationReport(num_problems=len(selected))
        for i, problem in enumerate(selected, 1):
            print(f"\n[{i}/{len(selected)}] {problem.problem_id} ({problem.category}, Level {problem.difficulty_level})")
            metrics = self.validate_problem(problem)
            report.problems.append(metrics)
            
            if metrics.success:
                report.num_success += 1
            else:
                report.num_failed += 1
        
        # Aggregate metrics
        self._aggregate_report(report)
        
        return report
    
    def _aggregate_report(self, report: ValidationReport):
        """Compute aggregated metrics"""
        successful = [p for p in report.problems if p.success]
        
        if not successful:
            print("\nNo successful validations!")
            return
        
        # D11 scores
        report.avg_original_d11 = sum(p.original_d11 for p in successful) / len(successful)
        report.avg_refined_d11 = sum(p.refined_d11 for p in successful) / len(successful)
        report.avg_improvement = sum(p.improvement_ratio for p in successful) / len(successful)
        
        # Timing
        timing_keys = ["time_original_score", "time_prover", "time_reasoner", "time_enricher", "time_refiner", "time_refined_score"]
        for key in timing_keys:
            avg = sum(getattr(p, key) for p in successful) / len(successful)
            report.avg_timing[key.replace("time_", "")] = round(avg, 3)
        
        # Reasoning types frequency
        all_reasoning = [t for p in successful for t in p.reasoning_types_selected]
        for t in set(all_reasoning):
            report.reasoning_types_frequency[t] = all_reasoning.count(t)
        
        report.timestamp = time.strftime("%Y-%m-%d %H:%M:%S")


# ============================================================================
# MAIN
# ============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--problems", type=int, default=5, help="Number of problems to validate")
    parser.add_argument("--output", type=str, default="validation_report.json", help="Output JSON path")
    args = parser.parse_args()
    
    engine = ValidationEngine()
    report = engine.validate_batch(num_problems=args.problems)
    
    # Print summary
    print(f"\n{'='*70}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total problems: {report.num_problems}")
    print(f"Successful: {report.num_success}")
    print(f"Failed: {report.num_failed}")
    print(f"\nD11 Scores:")
    print(f"  Average original: {report.avg_original_d11:.2f}")
    print(f"  Average refined: {report.avg_refined_d11:.2f}")
    print(f"  Average improvement: {report.avg_improvement:+.2%}")
    print(f"\nAverage Timing (seconds):")
    for stage, time_val in report.avg_timing.items():
        print(f"  {stage}: {time_val:.3f}s")
    total_avg_time = sum(report.avg_timing.values())
    print(f"  TOTAL: {total_avg_time:.3f}s per problem")
    print(f"\nReasoning Types (frequency):")
    for rtype, count in sorted(report.reasoning_types_frequency.items(), key=lambda x: -x[1]):
        print(f"  {rtype}: {count}")
    
    # Save JSON
    with open(args.output, 'w') as f:
        json.dump(report.to_dict(), f, indent=2, default=str)
    print(f"\nReport saved: {args.output}")


if __name__ == "__main__":
    main()
