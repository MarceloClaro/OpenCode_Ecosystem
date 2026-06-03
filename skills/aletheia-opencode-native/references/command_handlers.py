"""
Aletheia Command Handlers
Integration with OpenCode slash commands

Commands:
  /aletheia [problem]              → Generate + verify + audit proof
  /aletheia-audit [proof_id]       → Run PhD Auditor on existing proof
  /aletheia-benchmark              → Run full pipeline on 10-problem benchmark
  /aletheia-scale [n]              → Scale benchmark to n problems
  /aletheia-decisions [proof_id]   → Show DecisionNode audit trail
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional, List

# Import orchestration
from orchestration import AletheiaPipeline, AletheiaPipelineResult
from architect_agent import Problem

# Configuration
BENCHMARK_PATH = "benchmarks/aletheia_benchmark.json"
RESULTS_DIR = "results"
DECISIONS_DIR = ".decisions"


class CommandHandler:
    """OpenCode command handler for Aletheia"""
    
    def __init__(self):
        self.pipeline = AletheiaPipeline()
        self.results = {}
        self._load_benchmark()
    
    def _load_benchmark(self):
        """Load benchmark problems from JSON"""
        try:
            with open(BENCHMARK_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.benchmark_problems = data.get("problems", [])
                self.benchmark_metadata = data.get("metadata", {})
        except FileNotFoundError:
            print(f"Warning: Benchmark file not found at {BENCHMARK_PATH}")
            self.benchmark_problems = []
            self.benchmark_metadata = {}
    
    def cmd_aletheia(self, problem_statement: str) -> Dict:
        """
        /aletheia [problem]
        Generate proof with full pipeline validation
        """
        
        print(f"\n[/aletheia] Processing: {problem_statement[:80]}...")
        
        # Create problem from statement
        # Extract ID if provided, otherwise generate
        problem_id = f"P{len(self.results):04d}"
        domain = self._infer_domain(problem_statement)
        
        problem = Problem(
            id=problem_id,
            domain=domain,
            statement=problem_statement,
            difficulty="intermediate"  # Default
        )
        
        # Run pipeline
        result = self.pipeline.process_problem(problem)
        
        # Store result
        self.results[problem_id] = result
        
        # Return summary
        return {
            "proof_id": problem_id,
            "verdict": result.verification_verdict,
            "tier": result.audit_tier,
            "score": result.audit_avg_score,
            "confidence": result.verification_confidence
        }
    
    def cmd_aletheia_audit(self, proof_id: str) -> Dict:
        """
        /aletheia-audit [proof_id]
        Run PhD Auditor on existing proof
        """
        
        if proof_id not in self.results:
            return {"error": f"Proof {proof_id} not found"}
        
        result = self.results[proof_id]
        
        return {
            "proof_id": proof_id,
            "tier": result.audit_tier,
            "score": result.audit_avg_score,
            "strengths": result.audit_strengths,
            "weaknesses": result.audit_weaknesses,
            "improvements": result.audit_improvements,
            "vs_v3": result.audit_vs_v3_improvement,
            "vs_v4": result.audit_vs_v4_improvement
        }
    
    def cmd_aletheia_benchmark(self) -> Dict:
        """
        /aletheia-benchmark
        Run full pipeline on 10-problem benchmark
        """
        
        print(f"\n[/aletheia-benchmark] Running 10-problem benchmark...")
        
        if not self.benchmark_problems:
            return {"error": "Benchmark problems not loaded"}
        
        # Convert benchmark problems to Problem objects
        problems = []
        for bp in self.benchmark_problems[:10]:
            problem = Problem(
                id=bp["id"],
                domain=bp["domain"],
                statement=bp["statement"],
                difficulty=bp["difficulty"]
            )
            problems.append(problem)
        
        # Run batch processing
        results = self.pipeline.process_batch(problems)
        
        # Store results
        for result in results:
            self.results[result.problem_id] = result
        
        # Export
        self.pipeline.export_results(f"{RESULTS_DIR}/aletheia_benchmark_results.json")
        
        # Compute statistics
        tier_distribution = {tier: 0 for tier in "ABCD"}
        for result in results:
            tier_distribution[result.audit_tier] += 1
        
        avg_score = sum(r.audit_avg_score for r in results) / len(results)
        
        return {
            "problems_processed": len(results),
            "tier_distribution": tier_distribution,
            "avg_score": avg_score,
            "total_time": sum(r.processing_time_seconds for r in results),
            "exported_to": f"{RESULTS_DIR}/aletheia_benchmark_results.json"
        }
    
    def cmd_aletheia_scale(self, n: int) -> Dict:
        """
        /aletheia-scale [n]
        Scale benchmark to n problems (up to available)
        """
        
        print(f"\n[/aletheia-scale] Scaling to {n} problems...")
        
        if not self.benchmark_problems:
            return {"error": "Benchmark problems not loaded"}
        
        n = min(n, len(self.benchmark_problems))
        
        # Convert to Problem objects
        problems = []
        for bp in self.benchmark_problems[:n]:
            problem = Problem(
                id=bp["id"],
                domain=bp["domain"],
                statement=bp["statement"],
                difficulty=bp["difficulty"]
            )
            problems.append(problem)
        
        # Run batch processing
        results = self.pipeline.process_batch(problems)
        
        # Store results
        for result in results:
            self.results[result.problem_id] = result
        
        # Export
        self.pipeline.export_results(f"{RESULTS_DIR}/aletheia_scale_{n}_results.json")
        
        # Statistics
        tier_distribution = {tier: 0 for tier in "ABCD"}
        for result in results:
            tier_distribution[result.audit_tier] += 1
        
        avg_score = sum(r.audit_avg_score for r in results) / len(results)
        
        return {
            "problems_processed": n,
            "tier_distribution": tier_distribution,
            "avg_score": avg_score,
            "total_time": sum(r.processing_time_seconds for r in results),
            "exported_to": f"{RESULTS_DIR}/aletheia_scale_{n}_results.json"
        }
    
    def cmd_aletheia_decisions(self, proof_id: str) -> Dict:
        """
        /aletheia-decisions [proof_id]
        Show DecisionNode audit trail for proof
        """
        
        if proof_id not in self.results:
            return {"error": f"Proof {proof_id} not found"}
        
        result = self.results[proof_id]
        
        return {
            "proof_id": proof_id,
            "decisions_recorded": [
                {
                    "id": f"proof-strategy-{proof_id}",
                    "type": "strategy",
                    "phases": result.reasoning_plan["phases_selected"],
                    "reasoning_types": result.reasoning_plan["reasoning_types"]
                },
                {
                    "id": f"verification-{proof_id}",
                    "type": "verification",
                    "verdict": result.verification_verdict,
                    "confidence": result.verification_confidence
                },
                {
                    "id": f"audit-tier-{proof_id}",
                    "type": "audit",
                    "tier": result.audit_tier,
                    "score": result.audit_avg_score
                }
            ],
            "timestamp": result.timestamp
        }
    
    def _infer_domain(self, statement: str) -> str:
        """Infer mathematical domain from statement"""
        
        keywords = {
            "set_theory": ["set", "element", "subset", "powerset", "cardinality", "finite"],
            "algebra": ["group", "ring", "field", "ideal", "homomorphism", "cyclic"],
            "logic": ["proposition", "predicate", "quantifier", "formula", "proof", "theorem"],
            "analysis": ["limit", "continuous", "convergent", "series", "derivative", "integral", "epsilon", "delta"],
            "number_theory": ["prime", "divisible", "modulo", "gcd", "lcm", "factorization"]
        }
        
        statement_lower = statement.lower()
        
        for domain, keys in keywords.items():
            if any(key in statement_lower for key in keys):
                return domain
        
        return "algebra"  # Default


def main():
    """Main entry point for command handler"""
    
    handler = CommandHandler()
    
    # Parse command line arguments
    if len(sys.argv) < 2:
        print("Usage: /aletheia [command] [args]")
        print("Commands:")
        print("  /aletheia [problem]")
        print("  /aletheia-audit [proof_id]")
        print("  /aletheia-benchmark")
        print("  /aletheia-scale [n]")
        print("  /aletheia-decisions [proof_id]")
        return
    
    command = sys.argv[1]
    
    try:
        if command == "/aletheia" and len(sys.argv) > 2:
            problem_statement = " ".join(sys.argv[2:])
            result = handler.cmd_aletheia(problem_statement)
            print(json.dumps(result, indent=2))
        
        elif command == "/aletheia-audit" and len(sys.argv) > 2:
            proof_id = sys.argv[2]
            result = handler.cmd_aletheia_audit(proof_id)
            print(json.dumps(result, indent=2))
        
        elif command == "/aletheia-benchmark":
            result = handler.cmd_aletheia_benchmark()
            print(json.dumps(result, indent=2))
        
        elif command == "/aletheia-scale" and len(sys.argv) > 2:
            n = int(sys.argv[2])
            result = handler.cmd_aletheia_scale(n)
            print(json.dumps(result, indent=2))
        
        elif command == "/aletheia-decisions" and len(sys.argv) > 2:
            proof_id = sys.argv[2]
            result = handler.cmd_aletheia_decisions(proof_id)
            print(json.dumps(result, indent=2))
        
        else:
            print(f"Unknown command: {command}")
    
    except Exception as e:
        print(json.dumps({"error": str(e)}, indent=2))


if __name__ == "__main__":
    main()
