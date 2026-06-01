#!/usr/bin/env python
# Extrai alertas do HTML com severidade e arquivo
import re

with open('relatorio_antiplagio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find all severity rows
severities = ['CRÍTICA', 'ALTA', 'MEDIA', 'BAIXA']

for sev in severities:
    print(f'\n===== {sev} =====')
    idx = 0
    count = 0
    while True:
        idx = content.find(sev, idx)
        if idx < 0:
            break
        row_start = content.rfind('<tr>', 0, idx)
        if row_start < 0:
            idx += 1
            continue
        row_end = content.find('</tr>', idx)
        if row_end < 0:
            break
        snippet = content[row_start:row_end+5]
        
        tipo_match = re.search(r'<td[^>]*>([^<]+)</td>', snippet)
        tipo = tipo_match.group(1).strip() if tipo_match else '?'
        
        arq_match = re.search(r'>([^<]*\.tex)<', snippet)
        arq = arq_match.group(1) if arq_match else '?'
        
        # Get extract  
        ext_start = snippet.find('class="extrato"')
        ext = ''
        if ext_start >= 0:
            ext_start = snippet.find('>', ext_start) + 1
            ext_end = snippet.find('</', ext_start)
            ext = snippet[ext_start:ext_end]
        
        safe = ext.encode('ascii', 'replace').decode('ascii')[:100]
        print(f'  {tipo:40s} | {arq:25s} | {safe}')
        count += 1
        idx += 1
    if count == 0:
        print('  (none)')
    print(f'  Total: {count}')
