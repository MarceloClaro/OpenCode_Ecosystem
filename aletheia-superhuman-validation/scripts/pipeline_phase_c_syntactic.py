#!/usr/bin/env python3
"""
Phase C: Syntactic verification without Lean binary.
When Lean 4 is not available, performs structural validation of Lean code.
"""

import sys
import io
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

# Force UTF-8 output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class VerificationIteration:
    """Single verification iteration result."""
    iteration: int
    status: str  # "verified", "syntax_ok", "incomplete", "timeout", "unknown"
    error_message: str = ""
    error_classification: str = ""

@dataclass
class ProblemPhaseC:
    """Phase C result for a single problem."""
    problem_id: str
    domain: str
    problem_statement: str
    initial_candidate: Dict
    verification_iterations: List[VerificationIteration]
    final_status: str  # "success", "partial", "failed"
    execution_time_seconds: float
    
    def to_dict(self):
        return {
            "problem_id": self.problem_id,
            "domain": self.domain,
            "problem_statement": self.problem_statement,
            "initial_candidate": self.initial_candidate,
            "verification_iterations": [asdict(it) for it in self.verification_iterations],
            "final_status": self.final_status,
            "execution_time_seconds": self.execution_time_seconds,
        }

class SyntacticVerifier:
    """Basic syntactic verification of Lean code without Lean binary."""
    
    def __init__(self):
        self.lean_keywords = {
            'theorem', 'lemma', 'def', 'example', 'by', 'sorry',
            'intro', 'exact', 'apply', 'rw', 'simp', 'norm_num',
            'cases', 'induction', 'contradiction', 'push_neg'
        }
        self.lean_symbols = {':', '|-', '∀', '∃', '→', '∧', '∨', '¬', '=', '<', '>', '≤', '≥'}
    
    def verify_syntax(self, lean_code: str) -> Dict:
        """Basic syntactic check of Lean code."""
        result = {
            "status": "unknown",
            "issues": [],
            "confidence": 0.0
        }
        
        # Check if code is empty
        if not lean_code or len(lean_code.strip()) == 0:
            result["status"] = "incomplete"
            result["issues"].append("Lean code is empty")
            return result
        
        # Check for theorem/lemma declaration
        has_theorem = any(kw in lean_code for kw in ['theorem', 'lemma', 'example'])
        if not has_theorem:
            result["issues"].append("Missing theorem/lemma/example declaration")
            result["confidence"] -= 0.2
        
        # Check for proof body
        has_proof = 'by' in lean_code or ':=' in lean_code
        if not has_proof:
            result["issues"].append("Missing proof body (no 'by' or ':=' found)")
            result["confidence"] -= 0.2
            result["status"] = "incomplete"
        
        # Check for sorry (incomplete proof)
        if 'sorry' in lean_code:
            result["issues"].append("Proof contains 'sorry' (incomplete)")
            result["confidence"] -= 0.3
            result["status"] = "incomplete"
        
        # Check for placeholder propositions
        if '∀ x, P x' in lean_code or 'Q x' in lean_code:
            result["issues"].append("Proof uses placeholder propositions (P x, Q x)")
            result["confidence"] -= 0.25
        
        # Check basic syntax
        if lean_code.count('(') != lean_code.count(')'):
            result["issues"].append("Mismatched parentheses")
            result["status"] = "incomplete"
            result["confidence"] -= 0.3
        
        if lean_code.count('[') != lean_code.count(']'):
            result["issues"].append("Mismatched brackets")
            result["status"] = "incomplete"
            result["confidence"] -= 0.3
        
        # Count Lean keywords used
        keywords_found = sum(1 for kw in self.lean_keywords if kw in lean_code)
        result["keywords_used"] = keywords_found
        
        # Set final status if not already set
        if result["status"] == "unknown":
            if result["issues"]:
                result["status"] = "syntax_ok"  # Has issues but structure is OK
                result["confidence"] = 0.5
            else:
                result["status"] = "syntax_ok"
                result["confidence"] = 0.7
        
        return result

class PipelinePhaseCLite:
    """Phase C pipeline with syntactic verification only."""
    
    def __init__(
        self,
        dataset_path: str = "data/erdos_718_enriched_v1.1.json",
        selected_problems_path: str = "data/selected_problems_phase_b_v2.json",
        results_dir: str = "results"
    ):
        self.dataset_path = Path(dataset_path)
        self.selected_path = Path(selected_problems_path)
        self.results_dir = Path(results_dir)
        self.verifier = SyntacticVerifier()
        
        logger.info("Pipeline Phase C (Syntactic) initialized")
    
    def _load_proof_candidate(self, problem_id: str) -> Optional[Dict]:
        """Load proof candidate from Phase B."""
        candidate_file = self.results_dir / "proof_candidates" / f"{problem_id}_proof.json"
        
        if not candidate_file.exists():
            logger.warning(f"Proof candidate not found: {candidate_file}")
            return None
        
        with open(candidate_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _load_selected_problems(self, top_n: int = 5) -> List[Dict]:
        """Load selected problems."""
        if self.selected_path.exists():
            with open(self.selected_path, 'r', encoding='utf-8') as f:
                return json.load(f)[:top_n]
        return []
    
    def verify_problem(self, problem_id: str, problem_data: Dict) -> ProblemPhaseC:
        """Verify a single problem using syntactic analysis."""
        start_time = datetime.now()
        
        # Load proof candidate
        candidate = self._load_proof_candidate(problem_id)
        
        iterations = []
        
        if not candidate:
            iterations.append(VerificationIteration(
                iteration=1,
                status="incomplete",
                error_message="No proof candidate from Phase B",
                error_classification="missing_candidate"
            ))
            
            end_time = datetime.now()
            return ProblemPhaseC(
                problem_id=problem_id,
                domain=problem_data.get("domain", "unknown"),
                problem_statement=problem_data.get("statement", ""),
                initial_candidate=None,
                verification_iterations=iterations,
                final_status="failed",
                execution_time_seconds=(end_time - start_time).total_seconds()
            )
        
        # Syntactic verification
        for iter_num in range(1, 4):
            logger.info(f"  [{problem_id}] Iter {iter_num}/3...")
            
            result = self.verifier.verify_syntax(candidate["lean_code"])
            
            iterations.append(VerificationIteration(
                iteration=iter_num,
                status=result["status"],
                error_message=json.dumps(result["issues"]),
                error_classification="syntax" if result["issues"] else "none"
            ))
            
            # If syntax OK and no major issues, stop
            if result["status"] in ["verified", "syntax_ok"] and result["confidence"] > 0.6:
                break
        
        # Determine final status
        final_status = "partial" if iterations[-1].status == "syntax_ok" else "failed"
        if all(it.status in ["verified", "syntax_ok"] for it in iterations) and iterations[-1].status == "verified":
            final_status = "success"
        
        end_time = datetime.now()
        
        return ProblemPhaseC(
            problem_id=problem_id,
            domain=problem_data.get("domain", "unknown"),
            problem_statement=problem_data.get("statement", ""),
            initial_candidate=candidate,
            verification_iterations=iterations,
            final_status=final_status,
            execution_time_seconds=(end_time - start_time).total_seconds()
        )
    
    def run(self, top_n: int = 5) -> Dict:
        """Run Phase C verification."""
        logger.info("=" * 70)
        logger.info("PHASE C: SYNTACTIC VERIFICATION (No Lean binary required)")
        logger.info("=" * 70)
        
        problems = self._load_selected_problems(top_n)
        results = []
        success_count = 0
        partial_count = 0
        failed_count = 0
        
        for idx, problem_data in enumerate(problems):
            problem_id = problem_data.get("id")
            logger.info(f"\n{'=' * 70}")
            logger.info(f"PHASE C: {problem_id}")
            logger.info(f"{'=' * 70}")
            logger.info(f"  Domain: {problem_data.get('domain')}")
            logger.info(f"  Statement: {problem_data.get('statement', '')[:100]}...")
            logger.info(f"  [1/{len(problems)}] Verifying...")
            
            result = self.verify_problem(problem_id, problem_data)
            results.append(result)
            
            if result.final_status == "success":
                success_count += 1
            elif result.final_status == "partial":
                partial_count += 1
            else:
                failed_count += 1
        
        # Generate reports
        self._generate_json_report(results)
        self._generate_markdown_report(results, success_count, partial_count, failed_count)
        
        # Print summary
        logger.info("\n" + "=" * 70)
        logger.info("PHASE C SUMMARY (SYNTACTIC)")
        logger.info("=" * 70)
        logger.info(f"Total: {len(results)} problemas")
        logger.info(f"✅ Sucessos: {success_count}")
        logger.info(f"🟡 Parciais: {partial_count}")
        logger.info(f"❌ Falhas: {failed_count}")
        logger.info(f"Taxa de sucesso: {success_count/len(results)*100:.1f}%")
        logger.info(f"✓ Resultados JSON: {self.results_dir / 'pipeline_phase_c_syntactic_results.json'}")
        logger.info(f"✓ Relatório Markdown: {self.results_dir / 'PHASE_C_SYNTACTIC_RESULTS.md'}")
        logger.info("")
        logger.info("✅ Phase C (Syntactic) completado!")
        
        return {
            "success_count": success_count,
            "partial_count": partial_count,
            "failed_count": failed_count,
            "results": results
        }
    
    def _generate_json_report(self, results: List[ProblemPhaseC]):
        """Generate JSON report."""
        output = {
            "timestamp": datetime.now().isoformat(),
            "mode": "syntactic_verification",
            "total_problems": len(results),
            "results": [r.to_dict() for r in results]
        }
        
        output_path = self.results_dir / "pipeline_phase_c_syntactic_results.json"
        with open(output_path, "w", encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
    
    def _generate_markdown_report(self, results: List[ProblemPhaseC], success: int, partial: int, failed: int):
        """Generate Markdown report."""
        lines = [
            "# Phase C Results Report (Syntactic Verification)",
            "",
            f"**Data**: {datetime.now().isoformat()}",
            "",
            f"**Mode**: Syntactic verification (Lean 4 binary not available)",
            "",
            "## Summary",
            "",
            "| Status | Count | % |",
            "|--------|-------|-----|",
            f"| ✅ Success | {success} | {success/len(results)*100:.1f}% |",
            f"| 🟡 Partial | {partial} | {partial/len(results)*100:.1f}% |",
            f"| ❌ Failed | {failed} | {failed/len(results)*100:.1f}% |",
            f"| **Total** | **{len(results)}** | **100%** |",
            "",
            "## Details",
            ""
        ]
        
        # Successful
        lines.append("### ✅ Successful Problems")
        lines.append("")
        success_problems = [r for r in results if r.final_status == "success"]
        if success_problems:
            for r in success_problems:
                lines.append(f"- **{r.problem_id}** ({r.domain})")
        else:
            lines.append("- None")
        lines.append("")
        
        # Partial
        lines.append("### 🟡 Partial Solutions")
        lines.append("")
        partial_problems = [r for r in results if r.final_status == "partial"]
        if partial_problems:
            for r in partial_problems:
                issues = json.loads(r.verification_iterations[-1].error_message) if r.verification_iterations else []
                issues_str = ", ".join(issues[:2]) if issues else "syntax issues"
                lines.append(f"- **{r.problem_id}** ({r.domain}, issues: {issues_str}...)")
        else:
            lines.append("- None")
        lines.append("")
        
        # Failed
        lines.append("### ❌ Failed Problems")
        lines.append("")
        failed_problems = [r for r in results if r.final_status == "failed"]
        if failed_problems:
            for r in failed_problems:
                error = r.verification_iterations[0].error_message if r.verification_iterations else "unknown"
                lines.append(f"- **{r.problem_id}** ({r.domain}, error: {error[:60]}...)")
        else:
            lines.append("- None")
        lines.append("")
        
        # Recommendations
        lines.append("## Recommendations")
        lines.append("")
        lines.append("### To Enable Full Phase C (Real Lean Verification):")
        lines.append("1. Install Lean 4 via elan: `curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh`")
        lines.append("2. Or use Docker: `docker build -t aletheia-lean . && docker run aletheia-lean python scripts/pipeline_phase_c.py`")
        lines.append("3. Or use WSL2 + Ubuntu + Lean 4")
        lines.append("")
        
        output_path = self.results_dir / "PHASE_C_SYNTACTIC_RESULTS.md"
        output_path.write_text("\n".join(lines), encoding='utf-8')

if __name__ == "__main__":
    pipeline = PipelinePhaseCLite()
    pipeline.run(top_n=5)
