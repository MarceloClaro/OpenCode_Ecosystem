"""Phase D: PhD Auditor Evaluation for V4 Proofs."""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

def audit_proof_v4(proof: Dict) -> Dict:
    """Audit a V4 proof across 10 dimensions (same as Phase D)."""
    
    domain = proof['domain']
    sorry_count = proof['sorry_count']
    lean_code = proof['lean_code']
    confidence = proof.get('confidence', 0.5)
    
    # PhD Auditor: 10 dimensions (simplified heuristics matching Phase D)
    dimensions = {}
    
    # 1. Hypothesis Clarity (0-10): sorry count impact
    if sorry_count == 0:
        dimensions['hypothesis_clarity'] = 8.5
    elif sorry_count <= 1:
        dimensions['hypothesis_clarity'] = 6.5
    else:
        dimensions['hypothesis_clarity'] = 4.5
    
    # 2. Mathematical Insight (0-10): domain complexity
    domain_insight = {
        'combinatorics': 7.0,
        'number_theory': 7.5,
        'analysis': 8.0,
        'graph_theory': 7.0,
        'geometry': 7.5,
        'induction': 6.5,
        'finite_case': 6.0,
        'algebra': 7.5,
        'logic': 6.5,
        'category_theory': 8.5
    }
    dimensions['mathematical_insight'] = domain_insight.get(domain, 6.5)
    
    # 3. Proof Rigor (0-10): sorry + confidence
    dimensions['proof_rigor'] = min(9.0, 8.0 - (sorry_count * 0.5) + (confidence * 2.0))
    
    # 4. Case Analysis (0-10): proof structure presence
    case_analysis_score = 5.0
    if 'cases' in lean_code.lower() or 'match' in lean_code.lower():
        case_analysis_score += 2.0
    if 'induction' in lean_code.lower() or 'recursor' in lean_code.lower():
        case_analysis_score += 1.5
    dimensions['case_analysis'] = min(9.0, case_analysis_score)
    
    # 5. Formal Correctness (0-10): inverse of sorry
    dimensions['formal_correctness'] = max(3.0, 9.0 - (sorry_count * 1.5))
    
    # 6. Induction Validity (0-10): if applicable
    if 'induction' in lean_code.lower():
        dimensions['induction_validity'] = 7.0 - (sorry_count * 0.5)
    else:
        dimensions['induction_validity'] = 5.0
    
    # 7. Tactic Usage (0-10): presence of structured tactics
    tactic_score = 5.0
    if 'simp' in lean_code:
        tactic_score += 1.5
    if 'omega' in lean_code or 'ring' in lean_code:
        tactic_score += 1.5
    if 'calc' in lean_code:
        tactic_score += 1.5
    dimensions['tactic_usage'] = min(9.0, tactic_score)
    
    # 8. Lemma Usage (0-10): explicit lemmas/have statements
    lemma_count = lean_code.count('have ') + lean_code.count('lemma ')
    dimensions['lemma_usage'] = min(9.0, 5.0 + lemma_count)
    
    # 9. Edge Case Coverage (0-10): heuristic
    dimensions['edge_case_coverage'] = 5.5 - (sorry_count * 0.5)
    
    # 10. Overall Soundness (0-10): weighted average
    dimensions['overall_soundness'] = sum(dimensions.values()) / len(dimensions)
    
    # Tier classification (same as Phase D)
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
        'timestamp': datetime.now().isoformat()
    }

def run_phase_d_v4() -> List[Dict]:
    """Run Phase D audit on V4 proofs."""
    
    # Load V4 proofs
    with open('results/pipeline_phase_e_v4_results.json', encoding='utf-8') as f:
        v4_data = json.load(f)
    
    results = []
    tier_dist = {'A': 0, 'B': 0, 'C': 0, 'D': 0}
    
    print("\n" + "="*80)
    print("PHASE D: PhD Auditor Evaluation of V4 Proofs")
    print("="*80 + "\n")
    
    for proof in v4_data['results']:
        audit = audit_proof_v4(proof)
        results.append(audit)
        tier_dist[audit['tier']] += 1
        
        print(f"[{proof['problem_id']}] {audit['tier']} ({audit['overall_score']:.2f}) - sorry={proof['sorry_count']}")
    
    # Summary
    print("\n" + "="*80)
    print("PHASE D SUMMARY")
    print("="*80)
    print(f"Total proofs:      {len(results)}")
    for tier in ['A', 'B', 'C', 'D']:
        count = tier_dist[tier]
        pct = 100 * count / len(results) if results else 0
        print(f"Tier {tier}:            {count}/{len(results)} ({pct:.0f}%)")
    
    # Dimension analysis
    print("\nDimension Scores (average across proofs):")
    if results:
        dim_names = list(results[0]['dimensions'].keys())
        for dim in dim_names:
            avg_score = sum(r['dimensions'][dim] for r in results) / len(results)
            print(f"  {dim:.<30} {avg_score:.2f}/10")
    
    # Comparison with Phase D V3 (if available)
    phase_d_v3_file = Path('results/pipeline_phase_d_results.json')
    if phase_d_v3_file.exists():
        with open(phase_d_v3_file, encoding='utf-8') as f:
            v3_data = json.load(f)
        
        print("\n" + "="*80)
        print("V3 vs V4 COMPARISON")
        print("="*80)
        
        # Extract dimension scores from V3 (if available)
        v3_dims = {}
        if v3_data.get('results'):
            for r in v3_data['results']:
                for dim, score in r.get('dimensions', {}).items():
                    if dim not in v3_dims:
                        v3_dims[dim] = []
                    v3_dims[dim].append(score)
        
        if v3_dims:
            print("\nDimension Improvement (V3 → V4):")
            for dim in dim_names:
                v3_avg = sum(v3_dims.get(dim, [0])) / len(v3_dims.get(dim, [1]))
                v4_avg = sum(r['dimensions'][dim] for r in results) / len(results)
                delta = v4_avg - v3_avg
                sign = "↑" if delta >= 0 else "↓"
                print(f"  {dim:.<30} V3: {v3_avg:.2f} → V4: {v4_avg:.2f} ({sign}{abs(delta):.2f})")
    
    # Save results
    phase_d_output = {
        'phase': 'D-V4',
        'timestamp': datetime.now().isoformat(),
        'total_proofs': len(results),
        'tier_distribution': tier_dist,
        'results': results
    }
    
    output_file = Path('results/pipeline_phase_d_v4_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(phase_d_output, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: {output_file}\n")
    
    return results

if __name__ == '__main__':
    run_phase_d_v4()
