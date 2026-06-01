import re

with open('relatorio_antiplagio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find L3 (CITACAO DIRETA SEM REFERENCIA) alerts with full context
idx = 0
count = 0
while True:
    # Find the tipo cell
    idx = content.find('CITAÇÃO DIRETA SEM REFERÊNCIA', idx)
    if idx < 0:
        idx = content.find('CITACAO DIRETA SEM REFERENCIA', idx)
    if idx < 0:
        break
    count += 1
    
    # Find the surrounding <tr>
    row_start = content.rfind('<tr>', 0, idx)
    row_end = content.find('</tr>', idx)
    snippet = content[row_start:row_end+5]
    
    # Find the extrato
    ext_start = snippet.find('class="extrato"')
    if ext_start >= 0:
        ext_start = snippet.find('>', ext_start) + 1
        ext_end = snippet.find('</div>', ext_start)
        extrato = snippet[ext_start:ext_end]
    else:
        extrato = '(no extract)'
    
    # Find the arquivo
    arq_start = snippet.find('cap')
    if arq_start >= 0:
        arq_end = snippet.find('.tex', arq_start) + 4
        arq = snippet[arq_start:arq_end]
    else:
        arq = '(unknown)'
    
    safe = extrato.encode('ascii', 'replace').decode('ascii')
    print(f'#{count} [{arq}]: {safe[:150]}')
    print()
    idx += 1
    if count >= 40:
        break

print(f'\nTotal L3 found: {count}')
