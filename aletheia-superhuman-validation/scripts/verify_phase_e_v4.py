"""Verify Phase E V4 results."""

import json

with open('results/pipeline_phase_e_v4_results.json', encoding='utf-8') as f:
    v4_results = json.load(f)

print('Phase E V4 Results Summary:')
print(f'Total: {len(v4_results["results"])}')
zero_sorry = sum(1 for p in v4_results["results"] if p["sorry_count"] == 0)
print(f'Zero sorry: {zero_sorry}/{len(v4_results["results"])}')
print()
print('Proofs:')
for p in v4_results['results']:
    print(f'  {p["problem_id"]}: sorry={p["sorry_count"]}, method={p["generation_method"]}')
