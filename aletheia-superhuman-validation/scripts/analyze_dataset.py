"""
analyze_dataset.py — Analyze current dataset structure for enrichment design
Phase 1.1 Stage 4
"""
import json
import random
from collections import Counter

with open('data/erdos_718_enriched.json', encoding='utf-8') as f:
    data = json.load(f)

problems = data['problems']
print(f'Total problems: {len(problems)}')

# Sample 3 problems from different domains
for idx in [0, 100, 400, 550]:
    p = problems[idx]
    print(f'\n=== Problem {p["id"]} ({p["domain"]}) ===')
    print(f'  theorem_type: {p.get("theorem_type")}')
    print(f'  theorem_name: {p.get("theorem_name")}')
    print(f'  types: {p.get("types")}')
    print(f'  difficulty: {p.get("difficulty")}')
    rc = p.get('raw_lean_code', '')
    print(f'  raw_lean_code ({len(rc)} chars): {rc[:250]}...')
    st = p.get('statement', '')
    print(f'  statement ({len(st)} chars): {st[:200]}...')

# Analyze raw_lean_code patterns
print('\n\n=== RAW LEAN CODE ANALYSIS ===')
code_stats = []
for p in problems:
    rc = p.get('raw_lean_code', '')
    code_stats.append({
        'id': p['id'],
        'code_len': len(rc),
        'statement_len': len(p.get('statement', '')),
        'num_lines': rc.count('\n'),
        'num_tactics': sum(rc.count(t) for t in ['by ', 'apply ', 'simp', 'omega', 'calc', 'induction', 'cases']),
        'has_simp': 'simp' in rc,
        'has_calc': 'calc' in rc,
        'has_induction': 'induction' in rc,
        'has_omega': 'omega' in rc,
        'has_nlinarith': 'nlinarith' in rc,
        'has_by': 'by ' in rc,
    })

# Summary stats
lens = [s['code_len'] for s in code_stats]
stmt_lens = [s['statement_len'] for s in code_stats]
tactics = [s['num_tactics'] for s in code_stats]
lines = [s['num_lines'] for s in code_stats]

print(f'Code length: min={min(lens)}, max={max(lens)}, mean={sum(lens)/len(lens):.0f}, median={sorted(lens)[len(lens)//2]}')
print(f'Statement length: min={min(stmt_lens)}, max={max(stmt_lens)}, mean={sum(stmt_lens)/len(stmt_lens):.0f}')
print(f'Lines: min={min(lines)}, max={max(lines)}, mean={sum(lines)/len(lines):.1f}')
print(f'Tactics used: min={min(tactics)}, max={max(tactics)}, mean={sum(tactics)/len(tactics):.1f}')
print(f'Using "simp": {sum(1 for s in code_stats if s["has_simp"])} ({100*sum(1 for s in code_stats if s["has_simp"])/len(code_stats):.0f}%)')
print(f'Using "calc": {sum(1 for s in code_stats if s["has_calc"])}')
print(f'Using "induction": {sum(1 for s in code_stats if s["has_induction"])}')
print(f'Using "omega": {sum(1 for s in code_stats if s["has_omega"])}')
print(f'Using "nlinarith": {sum(1 for s in code_stats if s["has_nlinarith"])}')
print(f'Using "by": {sum(1 for s in code_stats if s["has_by"])}')

# Theorem types
theorem_types = Counter(p.get('theorem_type', '') for p in problems)
print(f'\n=== THEOREM TYPE DISTRIBUTION ===')
for k, v in theorem_types.most_common():
    print(f'  {k}: {v}')

# Has proof sketch?
has_sketch = sum(1 for p in problems if 'sketch' in p.get('statement', '').lower())
print(f'\nProblems mentioning "sketch": {has_sketch}')

# Conjecture detection
is_conj = sum(1 for p in problems if 'conjecture' in p.get('statement', '').lower() or 'conjecture' in p.get('filename', '').lower())
is_thm = sum(1 for p in problems if 'theorem' in p.get('statement', '').lower() or 'theorem' == p.get('theorem_type', ''))
print(f'Mention conjecture: {is_conj}, theorem: {is_thm}')
