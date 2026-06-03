"""Prepare full Phase E with 10 problems from Phase B."""

import json
from pathlib import Path

# Load Phase B V3 results (all 10 problems)
with open('results/pipeline_phase_b_v3_results.json', encoding='utf-8') as f:
    phase_b = json.load(f)

# Extract all 10 problems
full_data = {
    'phase': 'E-full',
    'count': len(phase_b['results']),
    'problems': [
        {
            'problem_id': result['problem_id'],
            'domain': result['domain'],
            'statement': result['statement']
        }
        for result in phase_b['results']
    ]
}

# Save
output_file = Path('data/full_problems_phase_e.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(full_data, f, indent=2, ensure_ascii=False)

print(f'Created full data with {len(full_data["problems"])} problems')
for p in full_data['problems']:
    print(f'  - {p["problem_id"]} ({p["domain"]})')

print(f'Saved to: {output_file}')
