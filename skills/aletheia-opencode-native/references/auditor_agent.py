"""
Aletheia Auditor Agent
Stage 3: PhD-Level Proof Evaluation (10 Dimensions, 4 Tiers)

Implements:
- 10-dimensional scoring framework
- Tier classification (A, B, C, D)
- Improvement recommendations
- Comparative analysis vs previous versions
"""

import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class TierLevel(Enum):
    """Proof quality tiers"""
    A = ("A", 8.0, "PhD-level, publishable")
    B = ("B", 7.0, "High quality, minor revisions")
    C = ("C", 6.0, "Acceptable, significant revision needed")
    D = ("D", 5.0, "Below standard, major rework required")
    
    def __init__(self, tier_id, min_score, description):
        self.tier_id = tier_id
        self.min_score = min_score
        self.description = description


DIMENSIONS = {
    "hypothesis_clarity": {
        "name": "Hypothesis Clarity",
        "weight": 0.10,
        "description": "Clarity and precision of the main theorem statement"
    },
    "mathematical_insight": {
        "name": "Mathematical Insight",
        "weight": 0.10,
        "description": "Depth of mathematical understanding and novelty"
    },
    "proof_rigor": {
        "name": "Proof Rigor",
        "weight": 0.12,
        "description": "Formal rigor, precision, and logical soundness"
    },
    "case_analysis": {
        "name": "Case Analysis",
        "weight": 0.12,
        "description": "Coverage of all cases and subcases"
    },
    "formal_correctness": {
        "name": "Formal Correctness",
        "weight": 0.12,
        "description": "Absence of logical errors and type errors"
    },
    "induction_validity": {
        "name": "Induction Validity",
        "weight": 0.10,
        "description": "Validity of inductive reasoning (if applicable)"
    },
    "tactic_usage": {
        "name": "Tactic Usage",
        "weight": 0.10,
        "description": "Correct and appropriate use of Lean tactics"
    },
    "lemma_usage": {
        "name": "Lemma Usage",
        "weight": 0.08,
        "description": "Appropriate selection and use of lemmas"
    },
    "edge_case_coverage": {
        "name": "Edge Case Coverage",
        "weight": 0.08,
        "description": "Coverage of boundary and special cases"
    },
    "proof_elegance": {
        "name": "Proof Elegance & Pedagogical Clarity",
        "weight": 0.08,
        "description": "Elegance of presentation, pedagogical structure, and accessibility for learning"
    },
    "overall_soundness": {
        "name": "Overall Soundness",
        "weight": 0.00,  # Computed from other dimensions
        "description": "Overall validity and completeness of proof"
    }
}


@dataclass
class ProofAudit:
    """Complete proof audit result"""
    proof_id: str
    domain: str
    
    # Dimension scores
    hypothesis_clarity: float
    mathematical_insight: float
    proof_rigor: float
    case_analysis: float
    formal_correctness: float
    induction_validity: float
    tactic_usage: float
    lemma_usage: float
    edge_case_coverage: float
    overall_soundness: float
    
    # Tier and metrics
    tier: str  # A, B, C, D
    avg_score: float
    confidence: float
    
    # Improvements and analysis
    weaknesses: List[str]
    strengths: List[str]
    improvement_suggestions: List[str]
    
    # Comparison to baselines
    vs_v3_improvement: Optional[float] = None  # Improvement percentage vs V3
    vs_v4_improvement: Optional[float] = None  # Improvement percentage vs V4
    
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return asdict(self)


class AuditorAgent:
    """Auditor Agent: PhD-level proof evaluation"""
    
    def __init__(self, decision_node=None):
        """
        Initialize Auditor Agent
        
        Args:
            decision_node: DecisionNode MCP client
        """
        self.decision_node = decision_node
        self.audited_proofs = []
        
        # Baseline scores for comparison
        self.v3_baseline = {
            "hypothesis_clarity": 5.83,
            "case_analysis": 5.50,
            "induction_validity": 5.33,
            "avg_score": 1.40  # V3 was very weak
        }
        self.v4_baseline = {
            "hypothesis_clarity": 7.50,
            "case_analysis": 6.50,
            "induction_validity": 7.50,
            "avg_score": 6.23
        }
    
    def score_dimensions(self, verification_data: Dict) -> Dict[str, float]:
        """
        Score all 10 dimensions based on verification data
        
        Uses V1 (Dimensional) scores directly, adjusts with reasoning context
        """
        
        v1 = verification_data.get("v1_dimensional", {})
        phases = verification_data.get("reasoning_phases", [])
        domain = verification_data.get("domain", "algebra")
        
        scores = {
            "hypothesis_clarity": min(v1.get("hypothesis_clarity", 7.5), 10.0),
            "mathematical_insight": min(v1.get("mathematical_insight", 7.0), 10.0),
            "proof_rigor": min(v1.get("proof_rigor", 8.0), 10.0),
            "case_analysis": min(v1.get("case_analysis", 8.0), 10.0),
            "formal_correctness": min(v1.get("formal_correctness", 7.5), 10.0),
            "induction_validity": min(v1.get("induction_validity", 8.5), 10.0),
            "tactic_usage": min(v1.get("tactic_usage", 7.0), 10.0),
            "lemma_usage": min(v1.get("lemma_usage", 7.5), 10.0),
            "edge_case_coverage": min(v1.get("edge_case_coverage", 7.0), 10.0),
        }
        
        # Overall soundness is weighted average
        weighted_sum = sum(
            scores[dim] * DIMENSIONS[dim]["weight"]
            for dim in scores
            if dim != "overall_soundness"
        )
        total_weight = sum(d["weight"] for d in DIMENSIONS.values() if d["weight"] > 0)
        scores["overall_soundness"] = weighted_sum / total_weight
        
        return scores
    
    def classify_tier(self, avg_score: float) -> Tuple[str, str]:
        """
        Classify proof into tier based on average score
        
        Returns:
            (tier_id, description)
        """
        
        for tier in [TierLevel.A, TierLevel.B, TierLevel.C, TierLevel.D]:
            if avg_score >= tier.min_score:
                return tier.tier_id, tier.description
        
        return TierLevel.D.tier_id, TierLevel.D.description
    
    def identify_strengths(self, scores: Dict[str, float]) -> List[str]:
        """Identify dimensions with strong scores (>8.0)"""
        
        strengths = []
        for dim, score in scores.items():
            if score >= 8.0:
                dim_name = DIMENSIONS[dim]["name"]
                strengths.append(f"Strong {dim_name} ({score:.1f}/10)")
        
        return strengths
    
    def identify_weaknesses(self, scores: Dict[str, float], 
                           tier: str) -> List[str]:
        """Identify dimensions below tier threshold"""
        
        weaknesses = []
        tier_threshold = {
            "A": 8.0,
            "B": 7.0,
            "C": 6.0,
            "D": 5.0
        }[tier]
        
        for dim, score in scores.items():
            if score < tier_threshold:
                dim_name = DIMENSIONS[dim]["name"]
                weaknesses.append(
                    f"{dim_name} below tier {tier} threshold ({score:.1f} vs {tier_threshold})"
                )
        
        return weaknesses
    
    def generate_improvements(self, scores: Dict[str, float],
                            domain: str,
                            weaknesses: List[str]) -> List[str]:
        """Generate improvement suggestions"""
        
        suggestions = []
        
        # Generic improvements
        if scores.get("hypothesis_clarity", 10) < 8.5:
            suggestions.append("Clarify the main theorem statement with more explicit notation")
        
        if scores.get("case_analysis", 10) < 8.5:
            suggestions.append("Ensure exhaustive case coverage; enumerate all subcases explicitly")
        
        if scores.get("mathematical_insight", 10) < 8.0:
            suggestions.append("Add auxiliary lemmas to demonstrate deeper mathematical understanding")
        
        if scores.get("edge_case_coverage", 10) < 8.0:
            suggestions.append("Explicitly handle boundary and special cases (e.g., zero, infinity, empty set)")
        
        if scores.get("proof_rigor", 10) < 8.0:
            suggestions.append("Increase formal rigor by adding more intermediate steps")
        
        # Domain-specific
        if domain == "algebra" and scores.get("tactic_usage", 10) < 7.5:
            suggestions.append("Use more appropriate group/ring theoretic tactics")
        
        if domain == "analysis" and scores.get("induction_validity", 10) < 8.0:
            suggestions.append("Strengthen inductive step with limit arguments or epsilon-delta proofs")
        
        return suggestions
    
    def compute_improvements(self, avg_score: float) -> Tuple[Optional[float], Optional[float]]:
        """
        Compute improvement percentage vs V3 and V4 baselines
        
        Returns:
            (vs_v3_improvement_pct, vs_v4_improvement_pct)
        """
        
        v3_improvement = None
        v4_improvement = None
        
        if avg_score > self.v3_baseline["avg_score"]:
            v3_improvement = ((avg_score - self.v3_baseline["avg_score"]) / 
                             self.v3_baseline["avg_score"]) * 100
        
        if avg_score > self.v4_baseline["avg_score"]:
            v4_improvement = ((avg_score - self.v4_baseline["avg_score"]) / 
                             self.v4_baseline["avg_score"]) * 100
        
        return v3_improvement, v4_improvement
    
    def audit_proof(self, proof_with_verification: Dict) -> ProofAudit:
        """
        Full audit pipeline: Score → Tier → Strengths/Weaknesses → Improvements
        
        Args:
            proof_with_verification: Proof dict with verification data
                {
                    "problem_id": "...",
                    "domain": "...",
                    "reasoning_phases": [...],
                    "v1_dimensional": {...},
                    ...
                }
        
        Returns:
            ProofAudit with complete evaluation
        """
        
        proof_id = proof_with_verification.get("problem_id", "unknown")
        domain = proof_with_verification.get("domain", "algebra")
        
        print(f"\n[Auditor] Auditing: {proof_id}")
        
        # Step 1: Score dimensions
        scores = self.score_dimensions(proof_with_verification)
        
        # Step 2: Calculate average
        dimension_values = [v for k, v in scores.items() if k != "overall_soundness"]
        avg_score = sum(dimension_values) / len(dimension_values)
        print(f"  Average score: {avg_score:.2f}/10")
        
        # Step 3: Classify tier
        tier, tier_desc = self.classify_tier(avg_score)
        print(f"  Tier: {tier} ({tier_desc})")
        
        # Step 4: Identify strengths and weaknesses
        strengths = self.identify_strengths(scores)
        weaknesses = self.identify_weaknesses(scores, tier)
        
        print(f"  Strengths: {len(strengths)}")
        for s in strengths[:3]:
            print(f"    - {s}")
        
        print(f"  Weaknesses: {len(weaknesses)}")
        for w in weaknesses[:3]:
            print(f"    - {w}")
        
        # Step 5: Generate improvements
        improvements = self.generate_improvements(scores, domain, weaknesses)
        
        # Step 6: Compute improvements vs baselines
        v3_improvement, v4_improvement = self.compute_improvements(avg_score)
        
        if v3_improvement:
            print(f"  vs V3: +{v3_improvement:.1f}%")
        if v4_improvement:
            print(f"  vs V4: +{v4_improvement:.1f}%")
        
        # Create audit object
        audit = ProofAudit(
            proof_id=proof_id,
            domain=domain,
            hypothesis_clarity=scores["hypothesis_clarity"],
            mathematical_insight=scores["mathematical_insight"],
            proof_rigor=scores["proof_rigor"],
            case_analysis=scores["case_analysis"],
            formal_correctness=scores["formal_correctness"],
            induction_validity=scores["induction_validity"],
            tactic_usage=scores["tactic_usage"],
            lemma_usage=scores["lemma_usage"],
            edge_case_coverage=scores["edge_case_coverage"],
            overall_soundness=scores["overall_soundness"],
            tier=tier,
            avg_score=avg_score,
            confidence=0.85 if tier == "A" else 0.75,
            weaknesses=weaknesses,
            strengths=strengths,
            improvement_suggestions=improvements,
            vs_v3_improvement=v3_improvement,
            vs_v4_improvement=v4_improvement
        )
        
        # Record decision
        if self.decision_node:
            self.decision_node.record_decision(
                id=f"audit-tier-{proof_id}",
                decision=f"Tier {tier} ({avg_score:.2f}/10)",
                rationale=f"{', '.join(strengths[:2])}"
            )
        
        self.audited_proofs.append(audit.to_dict())
        return audit


def auditor_run_example():
    """Example: Audit sample proofs"""
    
    auditor = AuditorAgent()
    
    # Sample proofs with verification data
    proofs_with_verification = [
        {
            "problem_id": "A0004",
            "domain": "set_theory",
            "reasoning_phases": [1, 2, 3, 5, 6, 7],
            "v1_dimensional": {
                "hypothesis_clarity": 8.2,
                "mathematical_insight": 7.5,
                "proof_rigor": 8.0,
                "case_analysis": 9.1,
                "formal_correctness": 7.8,
                "induction_validity": 9.5,
                "tactic_usage": 8.9,
                "lemma_usage": 8.5,
                "edge_case_coverage": 8.3,
                "overall_soundness": 8.35
            }
        },
        {
            "problem_id": "B0014",
            "domain": "algebra",
            "reasoning_phases": [1, 2, 3, 4, 6, 7],
            "v1_dimensional": {
                "hypothesis_clarity": 8.1,
                "mathematical_insight": 8.3,
                "proof_rigor": 7.9,
                "case_analysis": 8.8,
                "formal_correctness": 8.1,
                "induction_validity": 8.2,
                "tactic_usage": 8.0,
                "lemma_usage": 8.4,
                "edge_case_coverage": 8.1,
                "overall_soundness": 8.21
            }
        }
    ]
    
    results = []
    for proof in proofs_with_verification:
        audit = auditor.audit_proof(proof)
        results.append(audit.to_dict())
    
    return results


if __name__ == "__main__":
    results = auditor_run_example()
    print("\n" + "="*60)
    print(f"Auditor Agent: Audited {len(results)} proofs")
    for r in results:
        print(f"  {r['proof_id']}: Tier {r['tier']} ({r['avg_score']:.2f}/10)")
    print("="*60)
    
    # Save results
    with open("auditor_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print("Results saved to auditor_results.json")
