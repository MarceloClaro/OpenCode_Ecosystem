"""Prepare test data for Phase E from Phase B V3 results."""

import json
from pathlib import Path

# Load Phase B V3 results
with open('results/pipeline_phase_b_v3_results.json', encoding='utf-8') as f:
    phase_b = json.load(f)

# Extract first 3 problems
test_data = {
    'phase': 'E.4-test',
    'count': min(3, len(phase_b['results'])),
    'problems': [
        {
            'problem_id': result['problem_id'],
            'domain': result['domain'],
            'statement': result['statement']
        }
        for result in phase_b['results'][:3]
    ]
}

# Save
Path('data').mkdir(exist_ok=True)
output_file = Path('data/test_problems_phase_e.json')
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(test_data, f, indent=2, ensure_ascii=False)

print(f'Created test data with {len(test_data["problems"])} problems')
for p in test_data['problems']:
    print(f'  - {p["problem_id"]} ({p["domain"]})')

print(f'Saved to: {output_file}')
