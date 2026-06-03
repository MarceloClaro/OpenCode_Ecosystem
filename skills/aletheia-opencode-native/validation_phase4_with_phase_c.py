"""
Phase 4 Validation WITH Phase C Real MCPs
Integrates websearch, sequential-thinking, scihub, code-runner MCPs.
"""

import json
import time
import argparse
from dataclasses import asdict
from datetime import datetime
from typing import List, Optional

# Import Phase 4 components
from references.imo_benchmark_adapter import IMOBenchmarkAdapter
from references.prover_agent import ProverAgent
from references.reasoning_orchestrator_v11 import ReasoningOrchestrator
from references.mcp_enricher import MCPEnricher
from references.refinement_agent import RefinementAgent
from references.verifier_v7 import VerifierV7

# Import Phase C MCPs
from references.mcp_websearch import get_websearch_mcp
from references.mcp_sequential_thinking import get_sequential_thinking_mcp
from references.mcp_scihub import get_scihub_mcp
from references.mcp_code_runner import get_code_runner_mcp

# Import metrics
from validation_phase4_simple import ProblemMetrics, ValidationReport


class PhaseC_ValidationEngine:
    """Phase 4 Validation with Phase C Real MCPs integrated"""
    
    def __init__(self):
        # Phase 4 components
        self.adapter = IMOBenchmarkAdapter()
        self.prover = ProverAgent()
        self.reasoner = ReasoningOrchestrator()
        self.enricher = MCPEnricher()
        self.refiner = RefinementAgent()
        self.verifier = VerifierV7()
        
        # Phase C MCPs
        self.websearch = get_websearch_mcp()
        self.sequential_thinking = get_sequential_thinking_mcp()
        self.scihub = get_scihub_mcp()
        self.code_runner = get_code_runner_mcp()
        
        self.metrics_list: List[ProblemMetrics] = []
    
    def validate_problem(self, problem) -> Optional[ProblemMetrics]:
        """
        Validate single problem with Phase C MCPs.
        
        6-stage pipeline:
        1. Original score (baseline)
        2. Proof generation + sequential-thinking chains
        3. Reasoning selection + websearch context
        4. Enrichment with scihub + code validation
        5. Refinement
        6. Refined score
        """
        problem_id = problem.problem_id
        domain = getattr(problem, "aletheia_domain", "unknown")
        
        metrics = ProblemMetrics(
            problem_id=problem_id,
            category=getattr(problem, "category", "unknown"),
            level=getattr(problem, "difficulty_level", 1),
            domain=domain
        )
        
        try:
            # Stage 1: Original score
            t0 = time.time()
            original_proof = {"statement": problem.problem_statement}
            assessment = self.verifier.assess(original_proof)
            metrics.original_d11 = assessment.overall_d11_score
            metrics.time_original_score = time.time() - t0
            
            # Stage 2: Proof generation + sequential-thinking
            t0 = time.time()
            proofs = self.prover.generate_proofs(problem, num_strategies=2)
            
            # Stage 2b: Enrich with sequential-thinking chains
            for proof_attempt in proofs.proofs:
                chain = self.sequential_thinking.reason(
                    problem.problem_statement,
                    proof_attempt.strategy,
                    max_steps=5
                )
                proof_attempt.reasoning_chain = chain.steps
                proof_attempt.chain_confidence = chain.confidence
            
            metrics.time_prover = time.time() - t0
            
            # Stage 3: Reasoning selection + websearch
            t0 = time.time()
            reasoning_sel = self.reasoner.select_for_problem(problem, top_k=3)
            
            # Stage 3b: Enrich with websearch sources
            for reasoning_type, score in reasoning_sel.selected_reasonings:
                search_result = self.websearch.search_by_reasoning_type(
                    domain, reasoning_type
                )
                reasoning_sel.metadata[f"{reasoning_type}_sources"] = search_result.sources
            
            metrics.reasoning_types_selected = [r[0] for r in reasoning_sel.selected_reasonings]
            metrics.reasoning_confidence = reasoning_sel.confidence_score
            metrics.time_reasoner = time.time() - t0
            
            # Stage 4: MCPEnricher + scihub + code validation
            t0 = time.time()
            
            best_proof = proofs.proofs[0] if proofs.proofs else {"statement": "empty"}
            
            # Stage 4b: Scihub enrichment
            paper_result = self.scihub.fetch_paper(
                domain.lower(),
                title=problem.problem_statement[:50]
            )
            if paper_result.found:
                best_proof = {
                    **best_proof,
                    "referenced_paper": paper_result.title,
                    "paper_abstract": paper_result.abstract
                }
            
            # Stage 4c: Code validation
            proof_code = getattr(best_proof, "code", "")
            if proof_code:
                exec_result = self.code_runner.execute(proof_code)
                if exec_result.success:
                    best_proof["executable"] = True
                    best_proof["execution_score"] = exec_result.validation_score
            
            enriched = self.enricher.enrich(best_proof)
            metrics.time_enricher = time.time() - t0
            
            # Stage 5: Refinement
            t0 = time.time()
            refined = self.refiner.refine_proof(enriched)
            metrics.time_refiner = time.time() - t0
            
            # Stage 6: Refined score
            t0 = time.time()
            refined_assessment = self.verifier.assess(refined)
            metrics.refined_d11 = refined_assessment.overall_d11_score
            metrics.time_refined_score = time.time() - t0
            
            # Calculate improvement
            if metrics.original_d11 > 0:
                metrics.improvement_ratio = (
                    (metrics.refined_d11 - metrics.original_d11) / metrics.original_d11
                )
            
            metrics.success = True
            return metrics
        
        except Exception as e:
            metrics.error = str(e)
            metrics.success = False
            return metrics
    
    def validate_batch(self, num_problems: int = 5) -> ValidationReport:
        """Validate batch of problems with Phase C MCPs"""
        print("=" * 70)
        print(f"Phase 4 Validation WITH Phase C MCPs: {num_problems} problems")
        print("=" * 70)
        
        print("\n[LOAD] Loading problems from IMO-ProofBench...")
        problems = self.adapter.sample_problems(num_problems)
        print(f"  Loaded {len(problems)} total, using {num_problems}")
        print()
        
        for idx, problem in enumerate(problems, 1):
            print(f"\n[{idx}/{num_problems}] {problem.problem_id} ({problem.category}, Level {problem.difficulty_level})")
            metrics = self.validate_problem(problem)
            
            if metrics:
                self.metrics_list.append(metrics)
                
                if metrics.success:
                    ratio_pct = (metrics.improvement_ratio * 100) if metrics.improvement_ratio else 0
                    print(f"  [OK] Original: {metrics.original_d11:.2f} → Refined: {metrics.refined_d11:.2f} (ratio: {ratio_pct:+.2f}%)")
                else:
                    print(f"  [ERROR] {metrics.error}")
        
        # Aggregate report
        return self._generate_report()
    
    def _generate_report(self) -> ValidationReport:
        """Generate aggregated validation report"""
        successful = [m for m in self.metrics_list if m.success]
        failed = [m for m in self.metrics_list if not m.success]
        
        report = ValidationReport(
            num_problems=len(self.metrics_list),
            num_success=len(successful),
            num_failed=len(failed),
            avg_original_d11=sum(m.original_d11 for m in successful) / len(successful) if successful else 0,
            avg_refined_d11=sum(m.refined_d11 for m in successful) / len(successful) if successful else 0,
            avg_improvement=sum(m.improvement_ratio for m in successful if m.improvement_ratio) / len([m for m in successful if m.improvement_ratio]) if successful else 0,
            problems=successful
        )
        
        # Aggregate timing
        timing_keys = ["time_original_score", "time_prover", "time_reasoner", "time_enricher", "time_refiner", "time_refined_score"]
        for key in timing_keys:
            values = [getattr(m, key, 0) for m in successful]
            report.avg_timing[key] = sum(values) / len(values) if values else 0
        
        # Aggregate reasoning types
        for metric in successful:
            for reasoning_type in metric.reasoning_types_selected:
                report.reasoning_types_frequency[reasoning_type] = report.reasoning_types_frequency.get(reasoning_type, 0) + 1
        
        return report
    
    def save_report(self, report: ValidationReport, filename: str = "validation_phase_c_report.json"):
        """Save validation report to JSON"""
        report_dict = asdict(report)
        report_dict["problems"] = [asdict(p) for p in report.problems]
        
        with open(filename, 'w') as f:
            json.dump(report_dict, f, indent=2)
        
        print(f"\nReport saved: {filename}")


def main():
    parser = argparse.ArgumentParser(description="Phase 4 Validation with Phase C MCPs")
    parser.add_argument("--problems", type=int, default=5, help="Number of problems to validate")
    parser.add_argument("--output", default="validation_phase_c_report.json", help="Output JSON filename")
    args = parser.parse_args()
    
    engine = PhaseC_ValidationEngine()
    report = engine.validate_batch(num_problems=args.problems)
    
    # Print summary
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY (Phase 4 WITH Phase C MCPs)")
    print("=" * 70)
    print(f"Total problems: {report.num_problems}")
    print(f"Successful: {report.num_success}")
    print(f"Failed: {report.num_failed}")
    print()
    print("D11 Scores:")
    print(f"  Average original: {report.avg_original_d11:.2f}")
    print(f"  Average refined: {report.avg_refined_d11:.2f}")
    improvement_pct = (report.avg_improvement * 100) if report.avg_improvement else 0
    print(f"  Average improvement: {improvement_pct:+.2f}%")
    print()
    print("Average Timing (seconds):")
    total_time = sum(report.avg_timing.values())
    for key, value in report.avg_timing.items():
        print(f"  {key}: {value:.3f}s")
    print(f"  TOTAL: {total_time:.3f}s per problem")
    print()
    print("Reasoning Types (frequency):")
    for rtype, freq in sorted(report.reasoning_types_frequency.items(), key=lambda x: x[1], reverse=True):
        print(f"  {rtype}: {freq}")
    
    engine.save_report(report, args.output)


if __name__ == "__main__":
    main()
