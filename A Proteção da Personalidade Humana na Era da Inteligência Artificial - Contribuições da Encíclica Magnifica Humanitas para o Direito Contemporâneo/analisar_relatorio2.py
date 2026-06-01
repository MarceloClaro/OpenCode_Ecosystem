import re

with open('relatorio_antiplagio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Search for common data patterns
terms = ['CRITICA', 'CRÍTICA', 'severidade', 'tipo', 'mensagem', 'cap1', 
         'PARAGRAFO', 'CITACAO', 'alertas', 'const alertas']

for term in terms:
    idx = content.find(term)
    if idx >= 0:
        start = max(0, idx - 80)
        end = min(len(content), idx + 200)
        snippet = content[start:end]
        print(f'=== "{term}" at byte {idx} ===')
        print(snippet)
        print()
    else:
        print(f'=== "{term}" NOT FOUND ===')
        print()
