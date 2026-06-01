import json, re

with open('relatorio_antiplagio.html', 'r', encoding='utf-8') as f:
    html = f.read()

match = re.search(r'const alertas = (\[.*?\]);', html, re.DOTALL)
if not match:
    print("ERRO: nao encontrou dados JSON no HTML")
    exit(1)

alertas = json.loads(match.group(1))
crit = [a for a in alertas if a.get('severidade') == 'CRITICA']
altos = [a for a in alertas if a.get('severidade') == 'ALTA']
med = [a for a in alertas if a.get('severidade') == 'MEDIA']
baix = [a for a in alertas if a.get('severidade') == 'BAIXA']
print(f'CRITICA: {len(crit)}')
print(f'ALTA: {len(altos)}')
print(f'MEDIA: {len(med)}')
print(f'BAIXA: {len(baix)}')

if crit:
    print('\n=== CRITICOS ===')
    for a in crit[:30]:
        print(f'  [{a["tipo"]}] {a.get("arquivo","?")}:{a.get("linha","?")}')
        print(f'    {a.get("mensagem","")[:250]}')

if altos:
    print('\n=== ALTOS ===')
    for a in altos[:15]:
        print(f'  [{a["tipo"]}] {a.get("arquivo","?")}:{a.get("linha","?")}')
        print(f'    {a.get("mensagem","")[:250]}')
