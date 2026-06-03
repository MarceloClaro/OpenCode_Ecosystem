"""Analyze Phase D audit results to guide template refinement."""

import json
from collections import defaultdict
from pathlib import Path

def analyze_phase_d():
    """Analyze Phase D results and provide template improvement guidance."""
    
    results_dir = Path(__file__).parent.parent / 'results'
    phase_d_file = results_dir / 'pipeline_phase_d_results.json'
    
    with open(phase_d_file, encoding='utf-8') as f:
        phase_d = json.load(f)
    
    print('='*80)
    print('PHASE D AUDIT ANALYSIS: Template Refinement Guidance')
    print('='*80)
    
    # Aggregate dimension scores
    dim_totals = defaultdict(lambda: {'sum': 0, 'count': 0, 'problems': []})
    
    for proof in phase_d['results']:
        pid = proof['problem_id']
        domain = proof['domain']
        dims = proof['dimension_scores']
        
        for dim, score_obj in dims.items():
            score = score_obj['avg_score'] if isinstance(score_obj, dict) else score_obj
            dim_totals[dim]['sum'] += score
            dim_totals[dim]['count'] += 1
            dim_totals[dim]['problems'].append((pid, domain, score))
    
    print('\n[DIMENSION PERFORMANCE] (sorted by weakness):')
    print('-'*80)
    sorted_dims = sorted(dim_totals.items(), key=lambda x: x[1]['sum']/x[1]['count'])
    
    for dim, data in sorted_dims:
        avg = data['sum'] / data['count']
        severity = '[CRITICAL]' if avg < 4.0 else '[WEAK]' if avg < 5.0 else '[OK]'
        print(f'{severity} {dim:30s} {avg:.2f}/10')
        
        # Show worst problems
        worst = sorted(data['problems'], key=lambda x: x[2])[:2]
        for pid, domain, score in worst:
            print(f'    - {pid} ({domain}): {score:.1f}/10')
    
    print('\n[TEMPLATE IMPROVEMENT PRIORITIES]:')
    print('-'*80)
    
    priority_map = {
        'hypothesis_clarity': 'Add explicit assumption documentation in templates',
        'case_analysis': 'Include pattern matching / case splitting examples',
        'proof_rigor': 'Add justification steps between proof statements',
        'mathematical_insight': 'Include conceptual explanation before proofs',
        'induction_validity': 'Add base case + inductive step structure',
    }
    
    for i, (dim, data) in enumerate(sorted_dims[:4]):
        avg = data['sum'] / data['count']
        guidance = priority_map.get(dim, 'General improvement needed')
        print(f'Priority #{i+1}')
        print(f'  Dimension: {dim} ({avg:.2f}/10)')
        print(f'  Action: {guidance}')
        print()
    
    print('\n[RECOMMENDATIONS BY DOMAIN]:')
    print('-'*80)
    
    domain_weakness = defaultdict(list)
    for proof in phase_d['results']:
        domain = proof['domain']
        recommendations = proof.get('recommendations', [])
        domain_weakness[domain].extend(recommendations)
    
    for domain in sorted(domain_weakness.keys()):
        print(f'\n{domain.upper()}:')
        recs = set(domain_weakness[domain])
        for rec in sorted(recs)[:3]:
            print(f'  - {rec}')

if __name__ == '__main__':
    analyze_phase_d()
