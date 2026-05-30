# =====================================================================
# ADVANCED CALIBRATION ENGINE — 15-Dimensional Scientific Reasoning Score
# Expands beyond the 5 original criteria to comprehensively calibrate
# scientific reasoning quality
# =====================================================================
import sys, os, math, re, json, hashlib
from typing import Any, Optional
from collections import defaultdict
from dataclasses import dataclass, field

sys.path.insert(0, os.path.dirname(__file__))

@dataclass
class CalibrationDimension:
    name: str
    weight: float        # 0-1, sum of all weights = 1.0
    description: str
    measurement: str     # How it's measured
    threshold_green: float  # Above this = excellent
    threshold_yellow: float # Above this = adequate
    # Below yellow = needs improvement

@dataclass
class CalibrationReport:
    overall_score: float  # 0-100
    dimensions: dict      # dimension_name -> score (0-100)
    grade: str            # A+ through F
    strengths: list[str]
    weaknesses: list[str]
    recommendations: list[str]

class AdvancedCalibrationEngine:
    """
    15-dimensional calibration for scientific reasoning quality.
    
    Dimensions organized in 3 tiers:
    
    TIER 1 — MATHEMATICAL CORRECTNESS (40% total)
      D1: Cross-Reference Consistency (12%)
      D2: Base Case Exhaustiveness (10%)
      D3: Counterexample Resistance (10%)
      D4: Dimensional Consistency (8%)
    
    TIER 2 — STRUCTURAL ELEGANCE (35% total)
      D5: Branch Minimization (10%)
      D6: Invariant Richness (8%)
      D7: Proof Conciseness (7%)
      D8: Lemma Dependency Depth (5%)
      D9: Symmetry Exploitation (5%)
    
    TIER 3 — INTELLECTUAL VALUE (25% total)
      D10: Technique Reusability (7%)
      D11: Generalization Potential (6%)
      D12: Paradigm Shift Score (5%)
      D13: Historical Precedent Alignment (4%)
      D14: Computational Verifiability (3%)
      D15: Educational Clarity (bonus up to 5%)
    """
    
    def __init__(self):
        self.dimensions = self._define_dimensions()
    
    def _define_dimensions(self) -> dict[str, CalibrationDimension]:
        return {
            # TIER 1 — MATHEMATICAL CORRECTNESS (40%)
            "D1_crossref": CalibrationDimension(
                name="Cross-Reference Consistency",
                weight=0.12,
                description="Does the solution agree with independent external sources?",
                measurement="Match score against Evan Chen, DeepMind, AoPS, published solutions",
                threshold_green=0.90,
                threshold_yellow=0.60,
            ),
            "D2_basecase": CalibrationDimension(
                name="Base Case Exhaustiveness",
                weight=0.10,
                description="Was the smallest case verified exhaustively?",
                measurement="Computational enumeration for n ≤ 5 or manual verification",
                threshold_green=0.95,
                threshold_yellow=0.70,
            ),
            "D3_counterexample": CalibrationDimension(
                name="Counterexample Resistance",
                weight=0.10,
                description="Did stress testing find any counterexamples?",
                measurement="1.0 if no counterexamples found for n=3..50, decreases per failure",
                threshold_green=1.00,
                threshold_yellow=0.80,
            ),
            "D4_dimensional": CalibrationDimension(
                name="Dimensional Consistency",
                weight=0.08,
                description="Are all equations dimensionally consistent?",
                measurement="V1 (Cora-Debate) pass rate across all equations",
                threshold_green=1.00,
                threshold_yellow=0.85,
            ),
            
            # TIER 2 — STRUCTURAL ELEGANCE (35%)
            "D5_branches": CalibrationDimension(
                name="Branch Minimization",
                weight=0.10,
                description="How many case splits does the proof require?",
                measurement="Score = 100 - 20*cases. 0 cases = 100, 5+ cases = 0",
                threshold_green=90,
                threshold_yellow=60,
            ),
            "D6_invariants": CalibrationDimension(
                name="Invariant Richness",
                weight=0.08,
                description="How many mathematical invariants does the proof discover and use?",
                measurement="Score = min(100, invariants * 30). 0 = 0, 3 = 90, 4+ = 100",
                threshold_green=75,
                threshold_yellow=40,
            ),
            "D7_conciseness": CalibrationDimension(
                name="Proof Conciseness",
                weight=0.07,
                description="How many logical steps from hypothesis to conclusion?",
                measurement="Score = 100 - 10*(steps - 3). Minimum 3 steps (setup+proof+QED)",
                threshold_green=85,
                threshold_yellow=50,
            ),
            "D8_depth": CalibrationDimension(
                name="Lemma Dependency Depth",
                weight=0.05,
                description="How deep is the proof chain?",
                measurement="Score = 100 - 15*depth. Depth 0 = direct, depth 5 = very nested",
                threshold_green=85,
                threshold_yellow=50,
            ),
            "D9_symmetry": CalibrationDimension(
                name="Symmetry Exploitation",
                weight=0.05,
                description="Does the solution leverage inherent symmetries?",
                measurement="1 symmetry = 60, 2 symmetries = 85, 3+ = 100",
                threshold_green=75,
                threshold_yellow=40,
            ),
            
            # TIER 3 — INTELLECTUAL VALUE (25%)
            "D10_reusability": CalibrationDimension(
                name="Technique Reusability",
                weight=0.07,
                description="How transferable are the techniques to other problems?",
                measurement="gcd(p,p+1)=1 scores 0.95; case_analysis scores 0.30",
                threshold_green=75,
                threshold_yellow=45,
            ),
            "D11_generalization": CalibrationDimension(
                name="Generalization Potential",
                weight=0.06,
                description="Can the technique solve a broader class of problems?",
                measurement="Score based on parameter count and constraint relaxation",
                threshold_green=70,
                threshold_yellow=40,
            ),
            "D12_paradigm": CalibrationDimension(
                name="Paradigm Shift Score",
                weight=0.05,
                description="Does the solution reframe the problem in a fundamentally simpler way?",
                measurement="Reduction n->k scores 90; direct enumeration scores 20",
                threshold_green=70,
                threshold_yellow=35,
            ),
            "D13_historical": CalibrationDimension(
                name="Historical Precedent Alignment",
                weight=0.04,
                description="Does the technique appear in published solutions?",
                measurement="Match with IMO official solutions, Engel, Zeitz, Tao",
                threshold_green=80,
                threshold_yellow=50,
            ),
            "D14_computational": CalibrationDimension(
                name="Computational Verifiability",
                weight=0.03,
                description="Can the proof be verified by a computer?",
                measurement="SymPy check passes, exhaustive enumeration for small n",
                threshold_green=90,
                threshold_yellow=60,
            ),
            "D15_educational": CalibrationDimension(
                name="Educational Clarity",
                weight=0.00,  # Bonus — does not count toward total weight
                description="How accessible is the solution to students? (BONUS)",
                measurement="Clarity of exposition, step-by-step reasoning, diagrams",
                threshold_green=80,
                threshold_yellow=50,
            ),
        }
    
    def calibrate(self, solution_context: dict) -> CalibrationReport:
        """
        Compute the comprehensive 15-dimensional calibration score.
        
        Args:
            solution_context: dict containing:
                - crossref_matches: list of matching external sources
                - basecase_verified: bool
                - counterexamples_found: int
                - dimensional_passes: int/total
                - case_branches: int
                - invariants_found: int
                - proof_steps: int
                - lemma_depth: int
                - symmetries_used: int
                - techniques: list of technique names
                - generalizes_to: str or None
                - paradigm: str
                - historical_match: bool
                - computationally_verified: bool
                - educational_clarity: float 0-1
        """
        scores = {}
        
        # D1: Cross-Reference
        matches = solution_context.get("crossref_matches", 0)
        total_sources = solution_context.get("crossref_total", 2)
        scores["D1_crossref"] = (matches / max(total_sources, 1)) * 100
        
        # D2: Base Case
        scores["D2_basecase"] = 100 if solution_context.get("basecase_verified") else 25
        
        # D3: Counterexample Resistance
        failures = solution_context.get("counterexamples_found", 0)
        scores["D3_counterexample"] = max(0, 100 - failures * 25)
        
        # D4: Dimensional
        passes = solution_context.get("dimensional_passes", 0)
        total = solution_context.get("dimensional_total", 1)
        scores["D4_dimensional"] = (passes / max(total, 1)) * 100
        
        # D5: Branch Minimization
        branches = solution_context.get("case_branches", 0)
        scores["D5_branches"] = max(0, 100 - branches * 20)
        
        # D6: Invariant Richness
        invariants = solution_context.get("invariants_found", 0)
        scores["D6_invariants"] = min(100, invariants * 30)
        
        # D7: Proof Conciseness
        steps = solution_context.get("proof_steps", 5)
        scores["D7_conciseness"] = max(0, 100 - (steps - 3) * 10)
        
        # D8: Lemma Depth
        depth = solution_context.get("lemma_depth", 0)
        scores["D8_depth"] = max(0, 100 - depth * 15)
        
        # D9: Symmetry Exploitation
        syms = solution_context.get("symmetries_used", 0)
        scores["D9_symmetry"] = min(100, 40 + syms * 25) if syms > 0 else 0
        
        # D10: Technique Reusability
        techniques = solution_context.get("techniques", [])
        tech_scores_map = {
            "gcd_consecutive": 0.95, "divisor_symmetry": 0.90,
            "induction_cascade": 0.85, "invariant_method": 0.80,
            "extremal_principle": 0.75, "pigeonhole": 0.65,
            "double_counting": 0.60, "reduction": 0.70,
            "case_analysis": 0.30, "brute_force": 0.15,
        }
        if techniques:
            avg_tech = sum(tech_scores_map.get(t, 0.40) for t in techniques) / len(techniques)
        else:
            avg_tech = 0.40
        scores["D10_reusability"] = avg_tech * 100
        
        # D11: Generalization Potential
        generalizes = solution_context.get("generalizes_to")
        if generalizes == "all_n":
            scores["D11_generalization"] = 95
        elif generalizes == "prime_powers":
            scores["D11_generalization"] = 70
        elif generalizes:
            scores["D11_generalization"] = 50
        else:
            scores["D11_generalization"] = 20
        
        # D12: Paradigm Shift
        paradigm = solution_context.get("paradigm", "direct")
        paradigm_scores = {
            "reduction": 90, "symmetry_exploitation": 85,
            "invariant_discovery": 80, "induction": 70,
            "contradiction": 60, "construction": 50,
            "case_analysis": 20, "brute_force": 10,
        }
        scores["D12_paradigm"] = paradigm_scores.get(paradigm, 40)
        
        # D13: Historical Precedent
        scores["D13_historical"] = 85 if solution_context.get("historical_match") else 35
        
        # D14: Computational Verifiability
        scores["D14_computational"] = 90 if solution_context.get("computationally_verified") else 30
        
        # D15: Educational Clarity (bonus)
        scores["D15_educational"] = solution_context.get("educational_clarity", 0.5) * 100
        
        # Compute weighted overall
        overall = 0.0
        for dim_id, dim in self.dimensions.items():
            if dim_id != "D15_educational":  # Bonus doesn't count in weight
                overall += scores[dim_id] * dim.weight
        
        # Add educational bonus (max +5)
        bonus = scores["D15_educational"] * 0.05
        overall = min(100, overall + bonus)
        
        # Determine grade
        if overall >= 95: grade = "A+"
        elif overall >= 88: grade = "A"
        elif overall >= 80: grade = "B+"
        elif overall >= 72: grade = "B"
        elif overall >= 64: grade = "C+"
        elif overall >= 55: grade = "C"
        elif overall >= 45: grade = "D"
        else: grade = "F"
        
        # Strengths and weaknesses
        strengths = []
        weaknesses = []
        for dim_id, dim in self.dimensions.items():
            s = scores[dim_id]
            if s >= dim.threshold_green:
                strengths.append(f"{dim.name}: {s:.0f}/100")
            elif s < dim.threshold_yellow:
                weaknesses.append(f"{dim.name}: {s:.0f}/100 (need improvement)")
        
        # Recommendations
        recommendations = []
        if scores["D5_branches"] < 60:
            recommendations.append("Reduce case branches: use symmetry or invariants to unify cases")
        if scores["D6_invariants"] < 50:
            recommendations.append("Search for mathematical invariants (symmetry, gcd, monotonicity)")
        if scores["D12_paradigm"] < 40:
            recommendations.append("Consider paradigm shift: reduction, induction, or invariant method")
        if scores["D1_crossref"] < 60:
            recommendations.append("Cross-reference with external sources (Evan Chen, DeepMind, AoPS)")
        if scores["D8_depth"] < 50:
            recommendations.append("Flatten proof structure: reduce lemma dependency depth")
        
        return CalibrationReport(
            overall_score=overall,
            dimensions=scores,
            grade=grade,
            strengths=strengths[:5],
            weaknesses=weaknesses[:5],
            recommendations=recommendations[:5],
        )


# =====================================================================
# CALIBRATION AGENT — Integrates with the orchestrator
# =====================================================================

class CalibrationAgent:
    """
    Wraps the AdvancedCalibrationEngine for use in the OpenCode pipeline.
    
    This agent evaluates solutions AFTER the orchestrator produces them,
    providing a comprehensive 15-dimensional quality score.
    """
    
    def __init__(self):
        self.engine = AdvancedCalibrationEngine()
        self.history = []  # Track calibration history for learning
    
    def evaluate(self, solution: dict, proof_context: dict) -> CalibrationReport:
        """Evaluate a solution using the 15-dimensional calibration."""
        context = self._extract_context(solution, proof_context)
        report = self.engine.calibrate(context)
        self.history.append(report)
        return report
    
    def _extract_context(self, solution, proof_context):
        """Extract calibration dimensions from solution and proof context."""
        ctx = {}
        
        # From cross-reference
        ctx["crossref_matches"] = proof_context.get("crossref_matches", 0)
        ctx["crossref_total"] = proof_context.get("crossref_total", 2)
        
        # From verification
        ctx["basecase_verified"] = proof_context.get("basecase_verified", False)
        ctx["counterexamples_found"] = proof_context.get("counterexamples_found", 0)
        ctx["dimensional_passes"] = proof_context.get("dimensional_passes", 0)
        ctx["dimensional_total"] = proof_context.get("dimensional_total", 1)
        
        # From solution structure
        ctx["case_branches"] = solution.get("case_branches", 0)
        ctx["invariants_found"] = solution.get("invariants_found", 0)
        ctx["proof_steps"] = solution.get("proof_steps", 5)
        ctx["lemma_depth"] = solution.get("lemma_depth", 0)
        ctx["symmetries_used"] = solution.get("symmetries_used", 0)
        ctx["techniques"] = solution.get("techniques", [])
        ctx["generalizes_to"] = solution.get("generalizes_to")
        ctx["paradigm"] = solution.get("paradigm", "direct")
        ctx["historical_match"] = solution.get("historical_match", False)
        ctx["computationally_verified"] = solution.get("computationally_verified", False)
        ctx["educational_clarity"] = solution.get("educational_clarity", 0.5)
        
        return ctx
    
    def compare_solutions(self, sol_a: dict, sol_b: dict, ctx_a: dict, ctx_b: dict) -> dict:
        """Compare two solutions and explain the difference."""
        report_a = self.evaluate(sol_a, ctx_a)
        report_b = self.evaluate(sol_b, ctx_b)
        
        diff = {}
        for dim_id in self.engine.dimensions:
            if dim_id != "D15_educational":
                diff[dim_id] = report_b.dimensions[dim_id] - report_a.dimensions[dim_id]
        
        # Find key differentiators (dimensions with largest difference)
        sorted_diff = sorted(diff.items(), key=lambda x: abs(x[1]), reverse=True)
        key_diffs = [(dim_id, delta) for dim_id, delta in sorted_diff[:5] if abs(delta) > 5]
        
        return {
            "score_a": report_a.overall_score,
            "score_b": report_b.overall_score,
            "grade_a": report_a.grade,
            "grade_b": report_b.grade,
            "winner": "B" if report_b.overall_score > report_a.overall_score else "A",
            "margin": abs(report_a.overall_score - report_b.overall_score),
            "key_differentiators": [
                f"{self.engine.dimensions[did].name}: {'+' if delta > 0 else ''}{delta:.0f}pts"
                for did, delta in key_diffs
            ],
            "recommendations_a": report_a.recommendations,
            "recommendations_b": report_b.recommendations,
        }


# =====================================================================
# TEST: Compare brute force vs elegant IMO solutions
# =====================================================================

def test_calibration():
    """Test the 15-dimensional calibration on IMO 2002 P1 solutions."""
    print("=" * 65)
    print("15-DIMENSIONAL CALIBRATION — IMO 2002 Problem 1")
    print("=" * 65)
    
    agent = CalibrationAgent()
    
    # Solution A: Brute force (case analysis)
    sol_a = {
        "case_branches": 2,
        "invariants_found": 0,
        "proof_steps": 8,
        "lemma_depth": 1,
        "symmetries_used": 0,
        "techniques": ["case_analysis"],
        "generalizes_to": None,
        "paradigm": "case_analysis",
        "historical_match": False,
        "computationally_verified": False,
        "educational_clarity": 0.6,
    }
    ctx_a = {
        "crossref_matches": 2,
        "basecase_verified": True,
        "counterexamples_found": 0,
        "dimensional_passes": 1,
    }
    
    # Solution B: Elegant (symmetry + gcd + induction)
    sol_b = {
        "case_branches": 0,
        "invariants_found": 3,
        "proof_steps": 4,
        "lemma_depth": 0,
        "symmetries_used": 2,
        "techniques": ["gcd_consecutive", "divisor_symmetry", "induction_cascade"],
        "generalizes_to": "prime_powers",
        "paradigm": "symmetry_exploitation",
        "historical_match": True,
        "computationally_verified": True,
        "educational_clarity": 0.85,
    }
    ctx_b = {
        "crossref_matches": 2,
        "basecase_verified": True,
        "counterexamples_found": 0,
        "dimensional_passes": 1,
    }
    
    # Evaluate both
    report_a = agent.evaluate(sol_a, ctx_a)
    report_b = agent.evaluate(sol_b, ctx_b)
    
    print(f"\n{'='*65}")
    print(f"SOLUTION A (Brute Force): {report_a.overall_score:.1f}/100 — Grade: {report_a.grade}")
    print(f"{'='*65}")
    _print_report(report_a)
    
    print(f"\n{'='*65}")
    print(f"SOLUTION B (Elegant IMO): {report_b.overall_score:.1f}/100 — Grade: {report_b.grade}")
    print(f"{'='*65}")
    _print_report(report_b)
    
    # Compare
    comparison = agent.compare_solutions(sol_a, sol_b, ctx_a, ctx_b)
    print(f"\n{'='*65}")
    print(f"COMPARISON: B vs A — Margin: {comparison['margin']:.0f}pts ({comparison['winner']} wins)")
    print(f"{'='*65}")
    for d in comparison["key_differentiators"]:
        print(f"  {d}")


def _print_report(report: CalibrationReport):
    """Print calibration report."""
    print(f"  Overall: {report.overall_score:.0f}/100 ({report.grade})")
    if report.strengths:
        print(f"  Strengths:")
        for s in report.strengths[:3]:
            print(f"    + {s}")
    if report.weaknesses:
        print(f"  Weaknesses:")
        for w in report.weaknesses[:3]:
            print(f"    - {w}")
    if report.recommendations:
        print(f"  Recommendations:")
        for r in report.recommendations[:3]:
            print(f"    >> {r}")


if __name__ == "__main__":
    test_calibration()
