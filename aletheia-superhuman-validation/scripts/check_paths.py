"""Check filepath patterns in the dataset."""
import json
import os

with open('data/erdos_718_enriched.json', encoding='utf-8') as f:
    data = json.load(f)

# Check filepath patterns
print("First 20 filepath patterns:")
for p in data['problems'][:20]:
    fp = p.get('filepath', 'MISSING')
    domain = p.get('domain', '?')
    full = os.path.join('raw_data/formal-conjectures', fp)
    exists = os.path.exists(full)
    print(f"  domain={domain:25s} filepath={fp:40s} exists={exists}")

# Count how many files exist vs missing
missing = 0
total = len(data['problems'])
for p in data['problems']:
    fp = p.get('filepath', '')
    full = os.path.join('raw_data/formal-conjectures', fp)
    if not os.path.exists(full):
        missing += 1

print(f"\nTotal problems: {total}")
print(f"Missing files: {missing}")
print(f"Present files: {total - missing}")
