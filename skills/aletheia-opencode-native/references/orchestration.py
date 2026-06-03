"""
Aletheia Orchestration Engine
Coordinates Architect → Verifier → Auditor pipeline

Pipeline flow:
  Problem → [Architect] → Proof Skeleton
          → [Verifier] → Verification (V1, V2, V3)
          → [Auditor] → PhD Evaluation
          → DecisionNode Recording
          → Output: Complete Proof Package
"""

import json
from typing import Dict, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# Import agents
from architect_agent import ArchitectAgent, Problem, ReasoningPlan
from verifier_agent import VerifierAgent, VerificationVerdict
from auditor_agent import AuditorAgent, ProofAudit


@dataclass
class AletheiaPipelineResult:
    """Complete output from Architect → Verifier → Auditor pipeline"""
    
    problem_id: str
    domain: str
    
    # Stage 1: Architect
    reasoning_plan: Dict
    proof_skeleton: Dict
    
    # Stage 2: Verifier
    verification_v1: Dict  # Dimensional
    verification_v2: Dict  # Algebraic
    verification_v3: Dict  # Counterexample
    verification_verdict: str  # "VERIFIED" or "REQUIRES_REVISION"
    verification_confidence: float
    
    # Stage 3: Auditor
    audit_tier: str  # A, B, C, D
    audit_avg_score: float
    audit_strengths: List[str]
    audit_weaknesses: List[str]
    audit_improvements: List[str]
    audit_vs_v3_improvement: Optional[float]
    audit_vs_v4_improvement: Optional[float]
    
    # Metadata
    processing_time_seconds: float
    timestamp: str
    decisions_recorded: List[str]  # DecisionNode IDs
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AletheiaPipeline:
    """Main orchestration engine"""
    
    def __init__(self, decision_node=None):
        """
        Initialize pipeline with agents
        
        Args:
            decision_node: DecisionNode MCP client (optional)
        """
        self.architect = ArchitectAgent(decision_node=decision_node)
        self.verifier = VerifierAgent(decision_node=decision_node)
        self.auditor = AuditorAgent(decision_node=decision_node)
        self.decision_node = decision_node
        
        self.results = []
    
    def process_problem(self, problem: Problem) -> AletheiaPipelineResult:
        """
        Run full pipeline on a single problem
        
        Architect → Verifier → Auditor
        
        Returns:
            AletheiaPipelineResult with all stages completed
        """
        
        print(f"\n{'='*60}")
        print(f"ALETHEIA PIPELINE: {problem.id}")
        print(f"{'='*60}")
        
        start_time = datetime.now()
        decisions = []
        
        # ═════════════════════════════════════════════
        # STAGE 1: ARCHITECT
        # ═════════════════════════════════════════════
        print(f"\n[STAGE 1/3] ARCHITECT")
        print(f"{'─'*60}")
        
        architect_result = self.architect.process(problem)
        reasoning_plan = architect_result["reasoning_plan"]
        proof_skeleton = architect_result["proof"]
        
        decisions.append(f"proof-strategy-{problem.id}")
        
        # ═════════════════════════════════════════════
        # STAGE 2: VERIFIER
        # ═════════════════════════════════════════════
        print(f"\n[STAGE 2/3] VERIFIER (Cora-Debate V1, V2, V3)")
        print(f"{'─'*60}")
        
        # Prepare verification input
        verification_input = {
            "problem_id": problem.id,
            "domain": problem.domain,
            "reasoning_phases": reasoning_plan["phases_selected"],
            "reasoning_types": reasoning_plan["reasoning_types"],
            "lean_code": proof_skeleton["lean_code"]
        }
        
        verdict = self.verifier.verify_proof(verification_input)
        
        verification_v1 = asdict(verdict.v1_dimensional)
        verification_v2 = asdict(verdict.v2_algebraic)
        verification_v3 = asdict(verdict.v3_counterexample)
        
        decisions.append(f"verification-{problem.id}")
        
        # ═════════════════════════════════════════════
        # STAGE 3: AUDITOR
        # ═════════════════════════════════════════════
        print(f"\n[STAGE 3/3] AUDITOR (PhD Evaluation)")
        print(f"{'─'*60}")
        
        # Prepare audit input
        audit_input = {
            "problem_id": problem.id,
            "domain": problem.domain,
            "reasoning_phases": reasoning_plan["phases_selected"],
            "v1_dimensional": verification_v1
        }
        
        audit = self.auditor.audit_proof(audit_input)
        
        decisions.append(f"audit-tier-{problem.id}")
        
        # ═════════════════════════════════════════════
        # FINALIZE RESULT
        # ═════════════════════════════════════════════
        processing_time = (datetime.now() - start_time).total_seconds()
        
        result = AletheiaPipelineResult(
            problem_id=problem.id,
            domain=problem.domain,
            
            # Architect output
            reasoning_plan=reasoning_plan,
            proof_skeleton=proof_skeleton,
            
            # Verifier output
            verification_v1=verification_v1,
            verification_v2=verification_v2,
            verification_v3=verification_v3,
            verification_verdict=verdict.combined_verdict,
            verification_confidence=verdict.confidence_score,
            
            # Auditor output
            audit_tier=audit.tier,
            audit_avg_score=audit.avg_score,
            audit_strengths=audit.strengths,
            audit_weaknesses=audit.weaknesses,
            audit_improvements=audit.improvement_suggestions,
            audit_vs_v3_improvement=audit.vs_v3_improvement,
            audit_vs_v4_improvement=audit.vs_v4_improvement,
            
            # Metadata
            processing_time_seconds=processing_time,
            timestamp=datetime.now().isoformat(),
            decisions_recorded=decisions
        )
        
        self.results.append(result)
        
        # Print summary
        print(f"\n{'='*60}")
        print(f"RESULT SUMMARY")
        print(f"{'='*60}")
        print(f"Verification: {result.verification_verdict} (confidence: {result.verification_confidence:.2f})")
        print(f"Audit Tier:   {result.audit_tier}")
        print(f"Audit Score:  {result.audit_avg_score:.2f}/10")
        if result.audit_vs_v4_improvement:
            print(f"vs V4:        +{result.audit_vs_v4_improvement:.1f}%")
        print(f"Time:         {result.processing_time_seconds:.2f}s")
        print(f"Decisions:    {len(result.decisions_recorded)}")
        print(f"{'='*60}\n")
        
        return result
    
    def process_batch(self, problems: List[Problem]) -> List[AletheiaPipelineResult]:
        """
        Run pipeline on multiple problems
        
        Returns:
            List of AletheiaPipelineResult
        """
        
        print(f"\n{'#'*60}")
        print(f"ALETHEIA BATCH PROCESSING ({len(problems)} problems)")
        print(f"{'#'*60}")
        
        results = []
        for i, problem in enumerate(problems, 1):
            print(f"\n[{i}/{len(problems)}]")
            result = self.process_problem(problem)
            results.append(result)
        
        # Print batch summary
        print(f"\n{'#'*60}")
        print(f"BATCH SUMMARY")
        print(f"{'#'*60}")
        print(f"Problems processed: {len(results)}")
        print(f"Tier A: {sum(1 for r in results if r.audit_tier == 'A')}/{len(results)}")
        print(f"Avg score: {sum(r.audit_avg_score for r in results) / len(results):.2f}/10")
        print(f"Total time: {sum(r.processing_time_seconds for r in results):.2f}s")
        print(f"{'#'*60}\n")
        
        return results
    
    def export_results(self, filename: str = "aletheia_pipeline_results.json"):
        """Export all results to JSON"""
        
        output = {
            "timestamp": datetime.now().isoformat(),
            "total_problems": len(self.results),
            "results": [r.to_dict() for r in self.results],
            "summary": {
                "tier_a": sum(1 for r in self.results if r.audit_tier == "A"),
                "tier_b": sum(1 for r in self.results if r.audit_tier == "B"),
                "tier_c": sum(1 for r in self.results if r.audit_tier == "C"),
                "tier_d": sum(1 for r in self.results if r.audit_tier == "D"),
                "avg_score": sum(r.audit_avg_score for r in self.results) / len(self.results) if self.results else 0,
                "avg_verification_confidence": sum(r.verification_confidence for r in self.results) / len(self.results) if self.results else 0,
                "avg_processing_time": sum(r.processing_time_seconds for r in self.results) / len(self.results) if self.results else 0
            }
        }
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults exported to {filename}")
        return output


def pipeline_run_example():
    """Example: Run pipeline on 3 sample problems"""
    
    pipeline = AletheiaPipeline()
    
    problems = [
        Problem(
            id="A0004",
            domain="set_theory",
            statement="For finite set S with n elements, |P(S)| = 2^n",
            difficulty="intermediate"
        ),
        Problem(
            id="B0014",
            domain="algebra",
            statement="Every finite group of prime order is cyclic",
            difficulty="intermediate"
        ),
        Problem(
            id="E0019",
            domain="analysis",
            statement="If f is continuous on [a,b], then f is uniformly continuous on [a,b]",
            difficulty="hard"
        )
    ]
    
    # Run batch processing
    results = pipeline.process_batch(problems)
    
    # Export results
    pipeline.export_results("aletheia_example_results.json")
    
    return results


if __name__ == "__main__":
    results = pipeline_run_example()
    
    print("\n" + "="*60)
    print("PIPELINE EXECUTION COMPLETE")
    print("="*60)
    
    # Print final statistics
    if results:
        tiers = {}
        for r in results:
            tier = r.audit_tier
            tiers[tier] = tiers.get(tier, 0) + 1
        
        print(f"\nTier Distribution:")
        for tier in "ABCD":
            count = tiers.get(tier, 0)
            print(f"  Tier {tier}: {count}")
        
        print(f"\nAverage Score: {sum(r.audit_avg_score for r in results) / len(results):.2f}/10")
        print(f"Total Processing Time: {sum(r.processing_time_seconds for r in results):.2f}s")
