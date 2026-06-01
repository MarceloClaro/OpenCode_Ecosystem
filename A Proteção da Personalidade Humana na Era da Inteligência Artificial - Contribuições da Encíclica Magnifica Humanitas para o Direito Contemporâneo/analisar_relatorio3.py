import re

with open('relatorio_antiplagio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all CRITICA and ALTA occurrences with context
for term in ['CRÍTICA', 'ALTA']:
    idx = 0
    count = 0
    while True:
        idx = content.find(term, idx)
        if idx < 0 or count >= 30:
            break
        start = max(0, idx - 150)
        end = min(len(content), idx + 250)
        snippet = content[start:end]
        # sanitize for console
        safe = snippet.encode('ascii', 'replace').decode('ascii')
        print(f'=== {term} #{count+1} at byte {idx} ===')
        print(safe)
        print()
        idx += 1
        count += 1
    print(f'--- Total {term}: {count} ---')
