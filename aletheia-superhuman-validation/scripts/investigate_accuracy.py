import json

with open('data/spotcheck_validation_report.json', encoding='utf-8') as f:
    report = json.load(f)

low = [x for x in report['individual_results'] if x['scores']['statement_accuracy'] < 0.7]
print(f"Statement accuracy < 0.7: {len(low)} samples out of {len(report['individual_results'])}")
for x in sorted(low, key=lambda y: y['scores']['statement_accuracy'])[:15]:
    print(f"  [{x['id']}] ({x['domain']}) score={x['scores']['statement_accuracy']}: {x['notes']['statement_accuracy']}")
