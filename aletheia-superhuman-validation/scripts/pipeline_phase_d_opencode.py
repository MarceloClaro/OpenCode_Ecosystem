"""Phase D: PhD Auditor with Cora-Debate integration for OpenCode Phase E results."""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

def audit_proof_opencode(proof: Dict) -> Dict:
    """Audit OpenCode-generated proof using Cora-Debate dimension framework."""
    
    domain = proof['domain']
    sorry_count = proof['sorry_count']
    confidence = proof['confidence']
    
    # PhD Auditor: 10 dimensions (Cora-Debate enhanced)
    dimensions = {}
    
    # 1. Hypothesis Clarity: Explicit in reasoning_plan?
    plan = proof.get('reasoning_plan', {})
    phase1_steps = len(plan.get('phase_1_foundational', []))
    dimensions['hypothesis_clarity'] = min(8.5, 5.0 + phase1_steps * 1.0)
    
    # 2. Mathematical Insight: Domain complexity + phases
    domain_insight = {
        'combinatorics': 7.0, 'number_theory': 7.5, 'analysis': 8.0,
        'graph_theory': 7.0, 'geometry': 7.5, 'induction': 7.0,
        'finite_case': 6.5, 'algebra': 7.5, 'logic': 7.0, 'category_theory': 8.5
    }
    phases_used = sum(1 for k, v in plan.items() if v)
    dimensions['mathematical_insight'] = (domain_insight.get(domain, 7.0) * 0.7 + 
                                          min(10, phases_used * 1.4) * 0.3)
    
    # 3. Proof Rigor: Cora verification + sorry
    cora_verdict = proof.get('cora_verdict', {})
    cora_passed = sum(1 for v, s in cora_verdict.items() if s == 'PASS')
    dimensions['proof_rigor'] = min(9.0, 7.0 + (cora_passed / 3) * 2.0 - (sorry_count * 0.5))
    
    # 4. Case Analysis: Refutational phase quality
    phase5 = len(plan.get('phase_5_refutational', []))
    dimensions['case_analysis'] = min(9.0, 5.0 + phase5 * 2.0)
    
    # 5. Formal Correctness: Inverse of sorry
    dimensions['formal_correctness'] = max(3.0, 9.0 - (sorry_count * 1.5))
    
    # 6. Induction Validity: Inductive phase present?
    phase2_steps = len(plan.get('phase_2_inductive', []))
    dimensions['induction_validity'] = 5.0 + phase2_steps * 1.5 if phase2_steps > 0 else 5.0
    
    # 7. Tactic Usage: Deductive phase
    phase3_steps = len(plan.get('phase_3_deductive', []))
    dimensions['tactic_usage'] = min(9.0, 5.0 + phase3_steps * 1.3)
    
    # 8. Lemma Usage: Foundational references
    dimensions['lemma_usage'] = min(9.0, 4.0 + phase1_steps * 1.5)
    
    # 9. Edge Case Coverage: Refutational + exhaustive
    phase6_steps = len(plan.get('phase_6_verificational', []))
    dimensions['edge_case_coverage'] = min(9.0, 5.0 + phase6_steps * 1.2 - (sorry_count * 0.3))
    
    # 10. Overall Soundness: Weighted average
    dimensions['overall_soundness'] = sum(dimensions.values()) / len(dimensions)
    
    # Tier
    avg_score = dimensions['overall_soundness']
    if avg_score >= 8.0:
        tier = 'A'
    elif avg_score >= 6.5:
        tier = 'B'
    elif avg_score >= 5.0:
        tier = 'C'
    else:
        tier = 'D'
    
    return {
        'problem_id': proof['problem_id'],
        'domain': domain,
        'tier': tier,
        'overall_score': round(avg_score, 2),
        'dimensions': {k: round(v, 2) for k, v in dimensions.items()},
        'sorry_count': sorry_count,
        'confidence': confidence,
        'reasoning_phases_active': sum(1 for k, v in plan.items() if v),
        'timestamp': datetime.now().isoformat()
    }

def run_phase_d_opencode() -> List[Dict]:
    """Run Phase D audit on OpenCode Phase E results."""
    
    # Load OpenCode Phase E results
    with open('results/pipeline_phase_e_opencode_results.json', encoding='utf-8') as f:
        opencode_data = json.load(f)
    
    results = []
    tier_dist = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    
    print("\n" + "="*80)
    print("PHASE D: PhD Auditor + Cora-Debate (OpenCode Results)")
    print("="*80 + "\n")
    
    for proof in opencode_data['results']:
        audit = audit_proof_opencode(proof)
        results.append(audit)
        tier_dist[audit['tier']] += 1
        
        print(f"[{proof['problem_id']}] {audit['tier']} ({audit['overall_score']:.2f}) - "
              f"sorry={proof['sorry_count']}, phases={audit['reasoning_phases_active']}/6")
    
    # Summary
    print("\n" + "="*80)
    print("PHASE D SUMMARY (OpenCode)")
    print("="*80)
    print(f"Total proofs:      {len(results)}")
    for tier in ['A', 'B', 'C', 'D']:
        count = tier_dist[tier]
        pct = 100 * count / len(results) if results else 0
        print(f"Tier {tier}:            {count}/{len(results)} ({pct:.0f}%)")
    
    # Dimension analysis
    print("\nDimension Scores (average):")
    if results:
        dim_names = list(results[0]['dimensions'].keys())
        for dim in dim_names:
            avg_score = sum(r['dimensions'][dim] for r in results) / len(results)
            print(f"  {dim:.<30} {avg_score:.2f}/10")
    
    # Compare V3 vs V4 vs OpenCode
    print("\n" + "="*80)
    print("VERSION COMPARISON: V3 → V4 → OpenCode")
    print("="*80)
    
    # Load Phase D V4 results (V3 different structure)
    try:
        with open('results/pipeline_phase_d_v4_results.json', encoding='utf-8') as f:
            v4_data = json.load(f)
        
        # Compare dimensions
        dims_to_compare = ['hypothesis_clarity', 'case_analysis', 'proof_rigor']
        
        print("\nDimension Improvement Trajectory:")
        for dim in dims_to_compare:
            # V4: average of first 3 proofs
            v4_scores = [r['dimensions'].get(dim, 0) for r in v4_data['results'][:3]]
            v4_avg = sum(v4_scores) / len(v4_scores) if v4_scores else 0
            
            # OpenCode: average of all 10
            opencode_scores = [r['dimensions'].get(dim, 0) for r in results]
            opencode_avg = sum(opencode_scores) / len(opencode_scores) if opencode_scores else 0
            
            improvement = opencode_avg - v4_avg
            print(f"\n  {dim}:")
            print(f"    V4 (3 proofs):   {v4_avg:.2f}")
            print(f"    OpenCode (10):   {opencode_avg:.2f} ({improvement:+.2f})")
    
    except FileNotFoundError:
        print("(V4 comparison file not found)")
    
    # Save results
    phase_d_output = {
        'phase': 'D-OpenCode',
        'timestamp': datetime.now().isoformat(),
        'total_proofs': len(results),
        'tier_distribution': tier_dist,
        'results': results
    }
    
    output_file = Path('results/pipeline_phase_d_opencode_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(phase_d_output, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}\n")
    
    return results

if __name__ == '__main__':
    run_phase_d_opencode()
