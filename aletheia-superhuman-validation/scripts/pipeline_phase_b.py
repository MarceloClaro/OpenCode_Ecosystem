"""
pipeline_phase_b.py — Phase B: Proof Generation Pipeline
Session 11: Main Phase B Execution

Generates proofs for 10 selected Erdős problems using ProofGeneratorV2.
Output: results/pipeline_phase_b_results.json

Execution:
    $ python scripts/pipeline_phase_b.py
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from proof_generator_v2 import ProofGeneratorV2
from proof_templates import get_domain_for_problem


# 10 Selected problems for Phase B V2
SELECTED_PROBLEMS = [
    {
        "id": "A0004",
        "statement": "For any finite set S with n elements, |P(S)| = 2^n",
        "domain": "combinatorics"
    },
    {
        "id": "B0014",
        "statement": "gcd(a, b) divides both a and b for all positive integers a, b",
        "domain": "number_theory"
    },
    {
        "id": "B0017",
        "statement": "If a_n → L and b_n → L, then (a_n + b_n) / 2 → L",
        "domain": "analysis"
    },
    {
        "id": "E0019",
        "statement": "In any connected graph, there exists a path between any two vertices",
        "domain": "graph_theory"
    },
    {
        "id": "E0020",
        "statement": "The sum of angles in any triangle equals π radians",
        "domain": "geometry"
    },
    {
        "id": "E0025",
        "statement": "∑(i=0 to n-1) i = n(n-1)/2 for all non-negative integers n",
        "domain": "induction"
    },
    {
        "id": "E0030",
        "statement": "Any real number x satisfies either x > 0, x = 0, or x < 0",
        "domain": "finite_case"
    },
    {
        "id": "E0035",
        "statement": "The identity element of a group is unique",
        "domain": "algebra"
    },
    {
        "id": "E0038",
        "statement": "√2 is irrational (proof by contradiction)",
        "domain": "logic"
    },
    {
        "id": "E0045",
        "statement": "For functors F and G, F(g ∘ f) = (F g) ∘ (F f)",
        "domain": "category_theory"
    }
]


class PhaseB:
    """Phase B: Proof Generation Pipeline"""
    
    def __init__(self, output_dir: str = "results"):
        """
        Initialize Phase B
        
        Args:
            output_dir: Directory for results
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.generator = ProofGeneratorV2()
        self.results = []
        self.start_time = None
        self.end_time = None
    
    def run(self):
        """Execute Phase B on all selected problems"""
        self.start_time = datetime.now()
        
        print("\n" + "="*80)
        print("PHASE B: PROOF GENERATION (ProofGeneratorV2)")
        print("="*80)
        print(f"Problems: {len(SELECTED_PROBLEMS)}")
        print(f"Output: {self.output_dir}")
        print(f"Start: {self.start_time.isoformat()}")
        print()
        
        # Generate proofs
        for i, problem in enumerate(SELECTED_PROBLEMS, 1):
            self._process_problem(problem, i)
        
        self.end_time = datetime.now()
        duration = (self.end_time - self.start_time).total_seconds()
        
        # Save results
        self._save_results()
        
        # Print summary
        self._print_summary(duration)
    
    def _process_problem(self, problem: dict, index: int):
        """
        Process a single problem
        
        Args:
            problem: Problem dictionary
            index: Problem index (for progress)
        """
        problem_id = problem["id"]
        statement = problem["statement"]
        domain = problem.get("domain") or get_domain_for_problem(problem_id)
        
        print(f"[{index}/10] Generating proof for {problem_id}...", end=" ", flush=True)
        
        try:
            # Generate proof
            candidate = self.generator.generate(
                problem_id=problem_id,
                statement=statement,
                domain=domain,
                max_tokens=1500
            )
            
            # Store result
            self.results.append({
                "problem_id": candidate.problem_id,
                "domain": candidate.domain,
                "statement": candidate.statement,
                "natural_proof": candidate.natural_proof,
                "lean_code": candidate.lean_code,
                "confidence": candidate.confidence,
                "template_used": candidate.template_used,
                "timestamp": candidate.timestamp
            })
            
            print(f"✓ ({candidate.confidence} confidence)")
        
        except Exception as e:
            print(f"✗ Error: {str(e)}")
            self.results.append({
                "problem_id": problem_id,
                "domain": domain,
                "statement": statement,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    def _save_results(self):
        """Save results to JSON"""
        output_file = self.output_dir / "pipeline_phase_b_results.json"
        
        data = {
            "metadata": {
                "phase": "B",
                "engine": "ProofGeneratorV2",
                "total_problems": len(SELECTED_PROBLEMS),
                "generated": len([r for r in self.results if "error" not in r]),
                "failed": len([r for r in self.results if "error" in r]),
                "start_time": self.start_time.isoformat(),
                "end_time": self.end_time.isoformat(),
                "duration_sec": round((self.end_time - self.start_time).total_seconds(), 2)
            },
            "results": self.results
        }
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            print(f"\n✓ Results saved: {output_file}")
        except Exception as e:
            print(f"\n✗ Failed to save results: {str(e)}")
    
    def _print_summary(self, duration: float):
        """Print execution summary"""
        total = len(self.results)
        success = sum(1 for r in self.results if "error" not in r)
        failed = total - success
        
        print()
        print("="*80)
        print("SUMMARY")
        print("="*80)
        print(f"Total:    {total}")
        print(f"Generated: {success}")
        print(f"Failed:    {failed}")
        print(f"Success Rate: {round(100*success/total, 1)}%")
        print(f"Duration: {round(duration, 1)}s")
        print(f"Avg/Problem: {round(duration/total, 1)}s")
        print()


def main():
    """Main entry point"""
    phase_b = PhaseB()
    phase_b.run()


if __name__ == "__main__":
    main()
