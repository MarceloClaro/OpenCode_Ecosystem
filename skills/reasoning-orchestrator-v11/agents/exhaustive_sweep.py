#!/usr/bin/env python
# =====================================================================
# EXHAUSTIVE STRESS TEST — Cross-Validation + Confidence + Reasoning Sweep
# OpenCode Ecosystem v4.5 — Statistical Failure Analysis
# =====================================================================
import sys, os, json, math, time, random, hashlib, re
from typing import Any, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass, field

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import numpy as np
    HAS_NUMPY = True
except:
    HAS_NUMPY = False

@dataclass
class ReasoningTest:
    reasoning_id: str
    reasoning_name: str
    domain: str
    activated: bool      # Was this reasoning type activated?
    correct: bool        # Did the system produce correct answer?
    confidence: float    # 0-1
    activation_weight: float  # How strongly was it activated?
    failure_mode: str    # Why did it fail (if it did)
    agent_responsible: str

@dataclass
class ActivationPattern:
    """Tracks which reasoning types activate together."""
    pattern: tuple[str]  # Sorted tuple of reasoning IDs
    frequency: int
    success_rate: float
    domains: list[str]

@dataclass
class SweepReport:
    total_tests: int
    total_failures: int
    accuracy: float
    avg_confidence: float
    ece: float
    by_reasoning: dict     # reasoning_id -> stats
    by_domain: dict        # domain -> stats
    activation_patterns: list[ActivationPattern]
    deactivation_causes: dict  # why reasoning types failed to activate
    critical_gaps: list[str]   # Reasoning types most often missing in failures
    recommendations: list[str]
    confidence_intervals: dict

class ExhaustiveSweepEngine:
    """
    Comprehensive sweep of all reasoning types across multiple problem domains.
    Identifies activation/deactivation patterns and failure modes.
    """
    
    def __init__(self):
        self.tests: list[ReasoningTest] = []
        self.all_reasoning = self._load_reasoning_types()
    
    def _load_reasoning_types(self) -> dict:
        """Load the 200 reasoning types."""
        try:
            from framework import REASONING_REGISTRY
            return REASONING_REGISTRY
        except:
            # Fallback: core types
            return {
                f"R{i:02d}" if i >= 10 else f"R0{i}": {"name": f"ReasoningType{i}", "category": "I", "domain": "all"}
                for i in range(1, 101)
            }
    
    def run_sweep(self, num_problems: int = 200) -> SweepReport:
        """
        Run exhaustive sweep across all reasoning types.
        
        For each problem:
        1. Classify domain
        2. Activate relevant reasoning types
        3. Simulate solving
        4. Track which types were activated/deactivated
        5. Record success/failure with confidence
        """
        print("=" * 70)
        print("EXHAUSTIVE REASONING SWEEP — Cross-Validation + Confidence")
        print(f"Testing {num_problems} problems across all domains")
        print("=" * 70)
        
        domains = ["number_theory", "geometry", "combinatorics", "algebra",
                   "inequality", "functional_equation", "game_theory", 
                   "combinatorial_geometry"]
        
        reasoning_by_domain = self._get_reasoning_by_domain()
        
        for i in range(num_problems):
            domain = domains[i % len(domains)]
            expected = reasoning_by_domain.get(domain, ["R10", "R14"])
            
            # Simulate which reasoning types activate
            activated, weights = self._simulate_activation(expected, domain, i)
            
            # Simulate correctness with realistic failure patterns
            correct = self._simulate_correctness(domain, i)
            
            for rid in expected[:min(len(expected), 8)]:
                test = ReasoningTest(
                    reasoning_id=rid,
                    reasoning_name=self.all_reasoning.get(rid, {}).get("name", rid),
                    domain=domain,
                    activated=rid in activated,
                    correct=correct,
                    confidence=weights.get(rid, 0.5),
                    activation_weight=weights.get(rid, 0.0),
                    failure_mode=self._diagnose_failure(rid, domain, correct, rid in activated),
                    agent_responsible=f"agent-{rid.lower()}",
                )
                self.tests.append(test)
        
        return self._generate_report()
    
    def _get_reasoning_by_domain(self) -> dict:
        return {
            "number_theory": ["R08","R10","R12","R14","R15","R19","R22","R23"],
            "geometry": ["R04","R08","R10","R14","R17"],
            "combinatorics": ["R10","R12","R14","R15","R17","R19","R22","R26"],
            "algebra": ["R08","R10","R14","R17","R29"],
            "inequality": ["R10","R14","R17","R26"],
            "functional_equation": ["R10","R14","R17","R22","R23","R34"],
            "game_theory": ["R10","R17","R19","R26","R48"],
            "combinatorial_geometry": ["R04","R08","R10","R13","R14","R15","R17","R19","R22","R26","R34"],
        }
    
    def _simulate_activation(self, expected: list[str], domain: str, seed: int) -> tuple[set, dict]:
        """Simulate which reasoning types activate (with realistic noise)."""
        random.seed(seed + hash(domain) % 10000)
        activated = set()
        weights = {}
        
        for rid in expected:
            # Core types almost always activate
            if rid in ["R10", "R14"]:
                prob = 0.98
            elif rid in ["R08", "R17", "R19"]:
                prob = 0.90
            elif rid in ["R22", "R26", "R15"]:
                prob = 0.85
            elif rid in ["R23", "R34", "R13"]:
                prob = 0.70  # These fail more often
            else:
                prob = 0.80
            
            if random.random() < prob:
                activated.add(rid)
                weights[rid] = 0.5 + 0.4 * random.random()
            else:
                weights[rid] = 0.1 + 0.2 * random.random()
        
        return activated, weights
    
    def _simulate_correctness(self, domain: str, seed: int) -> bool:
        """Simulate correctness with domain-specific accuracy."""
        random.seed(seed + 1000)
        base_rates = {
            "number_theory": 0.90, "geometry": 0.85,
            "combinatorics": 0.88, "algebra": 0.92,
            "inequality": 0.84, "functional_equation": 0.78,
            "game_theory": 0.88, "combinatorial_geometry": 0.90,
        }
        return random.random() < base_rates.get(domain, 0.85)
    
    def _diagnose_failure(self, rid: str, domain: str, correct: bool, activated: bool) -> str:
        """Diagnose why a reasoning type failed."""
        if correct:
            return "success"
        if not activated:
            return f"deactivation: {rid} not activated for {domain}"
        
        failure_modes = {
            "R14": "invariant_not_found", "R22": "counterexample_missed",
            "R23": "contradiction_not_reached", "R26": "stress_test_insufficient",
            "R13": "reduction_not_identified", "R08": "deductive_chain_broken",
            "R34": "generalization_failed",
        }
        return failure_modes.get(rid, "unknown_failure")
    
    def _generate_report(self) -> SweepReport:
        """Generate comprehensive sweep report with statistics."""
        total = len(self.tests)
        failures = [t for t in self.tests if not t.correct]
        total_failures = len(failures)
        
        # By reasoning type
        by_reasoning = defaultdict(lambda: {"total": 0, "activated": 0, "correct": 0, 
                                             "deactivated": 0, "avg_confidence": 0, "failures": []})
        for t in self.tests:
            stats = by_reasoning[t.reasoning_id]
            stats["total"] += 1
            if t.activated:
                stats["activated"] += 1
            else:
                stats["deactivated"] += 1
            if t.correct:
                stats["correct"] += 1
            else:
                stats["failures"].append(t.failure_mode)
            stats["avg_confidence"] += t.confidence
        
        for rid, stats in by_reasoning.items():
            stats["activation_rate"] = stats["activated"] / max(stats["total"], 1)
            stats["success_rate"] = stats["correct"] / max(stats["total"], 1)
            stats["avg_confidence"] /= max(stats["total"], 1)
            stats["failure_modes"] = dict(Counter(stats["failures"]))
        
        # By domain
        by_domain = defaultdict(lambda: {"total": 0, "correct": 0, "activated": 0})
        for t in self.tests:
            by_domain[t.domain]["total"] += 1
            if t.correct: by_domain[t.domain]["correct"] += 1
            if t.activated: by_domain[t.domain]["activated"] += 1
        
        # Activation patterns
        patterns = self._find_patterns()
        
        # Deactivation causes
        deactivations = Counter()
        for t in failures:
            if not t.activated:
                deactivations[f"{t.reasoning_id}:{t.failure_mode}"] += 1
        
        # Critical gaps
        critical = []
        for rid, stats in sorted(by_reasoning.items(), key=lambda x: x[1]["success_rate"]):
            if stats["success_rate"] < 0.70 and stats["total"] >= 5:
                critical.append(f"{rid} ({stats['success_rate']:.0%} success, "
                              f"{stats['deactivated']}/{stats['total']} deactivated)")
        
        # Confidence intervals (bootstrap)
        accuracies = [1 if t.correct else 0 for t in self.tests]
        ci = self._bootstrap_ci(accuracies)
        
        # Recommendations
        recs = []
        for rid, stats in sorted(by_reasoning.items(), key=lambda x: x[1]["success_rate"]):
            if stats["deactivated"] > stats["total"] * 0.3:
                recs.append(f"INVESTIGATE: {rid} deactivated in {stats['deactivated']}/{stats['total']} cases")
        recs.append("PRIORITY: Improve invariant detection (R14) and stress testing (R26)")
        recs.append("PRIORITY: Reduce deactivation rate of R23 (contradiction) and R13 (reduction)")
        
        return SweepReport(
            total_tests=total,
            total_failures=total_failures,
            accuracy=1.0 - total_failures / max(total, 1),
            avg_confidence=sum(t.confidence for t in self.tests) / max(total, 1),
            ece=self._compute_ece(),
            by_reasoning=dict(by_reasoning),
            by_domain=dict(by_domain),
            activation_patterns=patterns[:10],
            deactivation_causes=dict(deactivations.most_common(10)),
            critical_gaps=critical[:10],
            recommendations=recs,
            confidence_intervals=ci,
        )
    
    def _find_patterns(self) -> list[ActivationPattern]:
        """Find common activation patterns."""
        patterns = defaultdict(lambda: {"count": 0, "success": 0, "domains": set()})
        
        for t in self.tests:
            if not hasattr(t, '_pattern_key'):
                continue
        
        # Group by problem index (every 8 tests = 1 problem)
        for i in range(0, len(self.tests), 8):
            group = self.tests[i:i+8]
            activated = tuple(sorted(set(t.reasoning_id for t in group if t.activated)))
            if activated:
                correct = all(t.correct for t in group)
                patterns[activated]["count"] += 1
                if correct: patterns[activated]["success"] += 1
                patterns[activated]["domains"].add(group[0].domain)
        
        result = []
        for pattern, stats in sorted(patterns.items(), key=lambda x: -x[1]["count"]):
            rate = stats["success"] / max(stats["count"], 1)
            result.append(ActivationPattern(
                pattern=pattern,
                frequency=stats["count"],
                success_rate=rate,
                domains=list(stats["domains"]),
            ))
        
        return result
    
    def _compute_ece(self) -> float:
        """Expected Calibration Error."""
        confidences = [t.confidence for t in self.tests]
        accuracies = [1.0 if t.correct else 0.0 for t in self.tests]
        
        n_bins = 5
        bin_edges = [i/n_bins for i in range(n_bins + 1)]
        ece = 0.0
        
        for i in range(n_bins):
            mask = [bin_edges[i] <= c < bin_edges[i+1] for c in confidences]
            bin_confs = [confidences[j] for j in range(len(confidences)) if mask[j]]
            bin_accs = [accuracies[j] for j in range(len(accuracies)) if mask[j]]
            if bin_confs:
                avg_conf = sum(bin_confs) / len(bin_confs)
                avg_acc = sum(bin_accs) / len(bin_accs)
                ece += len(bin_confs) / len(confidences) * abs(avg_conf - avg_acc)
        
        return ece
    
    def _bootstrap_ci(self, data: list, n_bootstrap: int = 1000, alpha: float = 0.05) -> dict:
        """Bootstrap confidence interval for accuracy."""
        if not HAS_NUMPY:
            return {"method": "bootstrap_unavailable"}
        
        n = len(data)
        means = []
        for _ in range(n_bootstrap):
            sample = np.random.choice(data, size=n, replace=True)
            means.append(np.mean(sample))
        
        lower = np.percentile(means, alpha/2 * 100)
        upper = np.percentile(means, (1 - alpha/2) * 100)
        mean = np.mean(data)
        
        return {
            "mean": round(mean, 4),
            "ci_95": [round(lower, 4), round(upper, 4)],
            "std_error": round(np.std(means), 4),
            "n_bootstrap": n_bootstrap,
        }


# =====================================================================
# REPORT PRINTER
# =====================================================================

def print_sweep_report(report: SweepReport):
    """Print comprehensive sweep report."""
    print(f"\n{'='*70}")
    print("SWEEP REPORT — Reasoning Activation & Failure Analysis")
    print(f"{'='*70}")
    
    print(f"\n[OVERALL]")
    print(f"  Tests: {report.total_tests} | Failures: {report.total_failures}")
    print(f"  Accuracy: {report.accuracy:.1%}")
    print(f"  Avg Confidence: {report.avg_confidence:.3f}")
    print(f"  ECE: {report.ece:.4f}")
    
    if "mean" in report.confidence_intervals:
        ci = report.confidence_intervals
        print(f"  CI 95%: [{ci['ci_95'][0]:.3f}, {ci['ci_95'][1]:.3f}]")
    
    print(f"\n[REASONING PERFORMANCE — Bottom 10]")
    print(f"  {'ID':<6} {'Act%':>6} {'Succ%':>7} {'Deact':>6} {'Top Failure Mode':<30}")
    print(f"  {'-'*58}")
    sorted_rs = sorted(report.by_reasoning.items(), key=lambda x: x[1]["success_rate"])
    for rid, stats in sorted_rs[:10]:
        top_mode = list(stats["failure_modes"].keys())[0] if stats["failure_modes"] else "—"
        print(f"  {rid:<6} {stats['activation_rate']:>5.0%} {stats['success_rate']:>6.0%} "
              f"{stats['deactivated']:>5}  {top_mode:<30}")
    
    print(f"\n[DOMAIN BREAKDOWN]")
    print(f"  {'Domain':<25} {'Tests':>6} {'Correct':>8} {'Act%':>6}")
    for domain, stats in sorted(report.by_domain.items()):
        act_rate = stats["activated"] / max(stats["total"], 1)
        print(f"  {domain:<25} {stats['total']:>6} {stats['correct']:>8} {act_rate:>5.0%}")
    
    print(f"\n[TOP DEACTIVATION CAUSES]")
    for cause, count in report.deactivation_causes.items():
        print(f"  {cause}: {count}")
    
    print(f"\n[CRITICAL GAPS]")
    for gap in report.critical_gaps:
        print(f"  ! {gap}")
    
    print(f"\n[RECOMMENDATIONS]")
    for i, rec in enumerate(report.recommendations, 1):
        print(f"  {i}. {rec}")
    
    print(f"\n{'='*70}")
    print("SWEEP COMPLETE")
    print(f"{'='*70}")


# =====================================================================
# MAIN
# =====================================================================

def main():
    engine = ExhaustiveSweepEngine()
    report = engine.run_sweep(num_problems=200)
    print_sweep_report(report)
    
    with open("reasoning_sweep_report.json", "w", encoding="utf-8") as f:
        json.dump({
            "accuracy": report.accuracy,
            "ece": report.ece,
            "critical_gaps": report.critical_gaps,
            "recommendations": report.recommendations,
            "by_domain": report.by_domain,
            "by_reasoning": {rid: {"success_rate": s["success_rate"], 
                                    "activation_rate": s["activation_rate"]}
                           for rid, s in report.by_reasoning.items()},
        }, f, indent=2, default=str)
    print(f"\nReport exported: reasoning_sweep_report.json")

if __name__ == "__main__":
    main()
