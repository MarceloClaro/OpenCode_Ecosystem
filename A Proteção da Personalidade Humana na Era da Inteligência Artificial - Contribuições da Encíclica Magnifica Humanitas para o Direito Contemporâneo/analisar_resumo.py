import re

with open('relatorio_antiplagio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Count severity levels
severidades = {'CRITICA': 0, 'CRÍTICA': 0, 'ALTA': 0, 'MEDIA': 0, 'BAIXA': 0, 'MEDÍA': 0}
for s in severidades:
    severidades[s] = content.count(f'<span class="severidade-badge"')

# Count alert types by searching for the tipo column
tipos = {}
idx = 0
while True:
    idx = content.find('<td style="font-size:0.8rem">', idx)
    if idx < 0:
        break
    start = idx + len('<td style="font-size:0.8rem">')
    end = content.find('</td>', start)
    tipo = content[start:end].strip()
    tipos[tipo] = tipos.get(tipo, 0) + 1
    idx = end + 5

# Count by file
arquivos = {}
idx = 0
while True:
    idx = content.find('<td style="font-size:0.85rem">cap', idx)
    if idx < 0:
        idx2 = content.find('<td style="font-size:0.85rem">anexo', idx)
        if idx2 < 0:
            break
        idx = idx2
    start = idx + len('<td style="font-size:0.85rem">')
    end = content.find('</td>', start)
    arq = content[start:end].strip()
    arquivos[arq] = arquivos.get(arq, 0) + 1
    idx = end + 5

print('=== ALERTAS POR TIPO ===')
for t, c in sorted(tipos.items(), key=lambda x: -x[1]):
    print(f'  {t}: {c}')

print()
print('=== ALERTAS POR ARQUIVO ===')
for a, c in sorted(arquivos.items(), key=lambda x: -x[1]):
    print(f'  {a}: {c}')

print()
print('=== TOTAL NO DASHBOARD ===')
# Find dashboard numbers
for term in ['CRÍTICA', 'ALTA', 'MÉDIA', 'BAIXA']:
    idx = content.find(term)
    if idx >= 0:
        # find preceding number
        pre = content[max(0,idx-50):idx]
        nums = re.findall(r'(\d+)</div>', pre)
        if nums:
            print(f'  {term}: {nums[-1]}')
