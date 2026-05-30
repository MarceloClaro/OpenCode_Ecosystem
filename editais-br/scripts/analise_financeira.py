#!/usr/bin/env python3
"""
Analise financeira dos 65 editais curados.
Le: CURATED_EDITAIS.json
Produz: relatorio_financeiro.md
"""

import json, re, os, statistics
from collections import defaultdict, Counter

CURATED_PATH = r'C:\Users\marce\.config\opencode\skills\research\editais-br\curated\CURATED_EDITAIS.json'
OUT_PATH = r'C:\Users\marce\.config\opencode\editais-br\relatorio_financeiro.md'

with open(CURATED_PATH, 'r', encoding='utf-8') as f:
    editais = json.load(f)

def parse_brl(s: str) -> float | None:
    """Parse Brazilian currency string like 'R$ 1.500,00' or 'R$ 1.500/mes' or 'US$ 1.300/mes'."""
    if not s or s.strip().lower() == 'a definir':
        return None
    s = s.strip()

    is_usd = 'us$' in s.lower()
    is_monthly = '/mes' in s.lower()
    is_range = ' a ' in s or 'a r$' in s.lower() or 'a us$' in s.lower()

    s_clean = s.lower().replace('r$', '').replace('us$', '').replace('/mes', '').strip()

    if is_range:
        parts = re.split(r'\s+a\s+', s_clean)
        vals = []
        for p in parts:
            p = p.strip()
            # Handle ranges within ranges (e.g. "900 a 1800 + 12.000 a 30.000")
            if '+' in p:
                sub_parts = p.split('+')
                for sp in sub_parts:
                    sp = sp.strip()
                    v = _parse_single_brl(sp)
                    if v is not None:
                        vals.append(v)
            else:
                v = _parse_single_brl(p)
                if v is not None:
                    vals.append(v)
        if len(vals) >= 2:
            low = min(vals)
            high = max(vals)
            mid = (low + high) / 2
        elif len(vals) == 1:
            mid = vals[0]
        else:
            return None

        if is_usd:
            mid *= 5.0
        if is_monthly:
            mid *= 12

        return mid

    elif is_monthly:
        v = _parse_single_brl(s_clean)
        if v is None:
            return None
        if is_usd:
            v *= 5.0
        return v * 12

    else:
        v = _parse_single_brl(s_clean)
        if v is None:
            return None
        if is_usd:
            v *= 5.0
        return v

def _parse_single_brl(s: str) -> float | None:
    """Parse a single BRL value like '1.500,00' or '5.200' (Brazilian notation)."""
    s = s.strip()
    s = s.replace('.', '').replace(',', '.')
    m = re.search(r'[\d.]+', s)
    if m:
        try:
            return float(m.group())
        except ValueError:
            return None
    return None

# Parse all values
rows = []
tbds = []
values = []
for e in editais:
    v = parse_brl(e['valor_declarado'])
    e['valor_anual_estimado'] = v
    if v is None:
        tbds.append(e)
    else:
        values.append(v)
    rows.append(e)

# ===== Tabela detalhada =====
table_lines = []
table_lines.append('| # | Edital | Agência | Categoria | Valor Declarado | Valor Anual Estimado (R\$) | Nota |')
table_lines.append('|---|--------|---------|-----------|-----------------|---------------------------|------|')
for i, e in enumerate(rows, 1):
    v_est = e.get('valor_anual_estimado')
    v_str = f'R\$ {v_est:,.2f}' if v_est is not None else 'TBD'
    table_lines.append(f'| {i} | {e["nome"]} | {e["agencia"]} | {e["categoria"]} | {e["valor_declarado"]} | {v_str} | {e["nota"]} |')

tabela = '\n'.join(table_lines)

# ===== Sumários =====
total = sum(v for v in values if v is not None)
n_valued = len(values)
n_tbd = len(tbds)
n_total = len(rows)

# Per agency
por_agencia = defaultdict(list)
for e in rows:
    v = e.get('valor_anual_estimado')
    if v is not None:
        por_agencia[e['agencia']].append(v)

# Per category
por_categoria = defaultdict(list)
for e in rows:
    v = e.get('valor_anual_estimado')
    if v is not None:
        por_categoria[e['categoria']].append(v)

# Per-profile weighted average for 'pesquisa'
pesquisa_vals = [v for e in rows if e['categoria'] == 'pesquisa' and (v := e.get('valor_anual_estimado')) is not None]
pesquisa_avg = statistics.mean(pesquisa_vals) if pesquisa_vals else 0

# TBD list
tbd_nomes = [e['nome'] for e in tbds]

# Build markdown
md = f"""# Relatorio Financeiro — Editais Curados (Brasil 2026)

> Gerado automaticamente a partir de `CURATED_EDITAIS.json` ({n_total} editais, {n_valued} com valor, {n_tbd} TBD).

---

## 1. Sumario Executivo

| Metrica | Valor |
|---------|-------|
| Numero total de editais analisados | {n_total} |
| Editais com valor definido | {n_valued} |
| Editais com valor TBD | {n_tbd} |
| **Total teorico maximo (soma de todos os editais)** | **R\$ {total:,.2f}** |
| Media por edital (valor definido) | R\$ {statistics.mean(values):,.2f} |
| Mediana por edital | R\$ {statistics.median(values):,.2f} |
| Maior valor individual | R\$ {max(values):,.2f} |
| Menor valor individual | R\$ {min(values):,.2f} |

---

## 2. Sumario por Agencia

| Agencia | Qtd Editais | Total Estimado (R\$) | Media (R\$) |
|---------|-------------|---------------------|-------------|
"""

for agencia in sorted(por_agencia.keys()):
    vals = por_agencia[agencia]
    s = sum(vals)
    m = statistics.mean(vals)
    md += f'| {agencia} | {len(vals)} | R\$ {s:,.2f} | R\$ {m:,.2f} |\n'

md += f"""
---

## 3. Sumario por Categoria

| Categoria | Qtd Editais | Total Estimado (R\$) | Media (R\$) |
|-----------|-------------|---------------------|-------------|
"""

for cat in sorted(por_categoria.keys()):
    vals = por_categoria[cat]
    s = sum(vals)
    m = statistics.mean(vals)
    md += f'| {cat} | {len(vals)} | R\$ {s:,.2f} | R\$ {m:,.2f} |\n'

md += f"""

---

## 4. Media Ponderada por Perfil

### Perfil: Pesquisa

Valor medio de um edital de **pesquisa**: **R\$ {pesquisa_avg:,.2f}**

Distribuicao por categoria de interesse do pesquisador:

| Categoria | Qtd | Total | Media |
|-----------|-----|-------|-------|
"""

# Add distribution for research profile
cats_interesse = ['pesquisa', 'bolsa', 'internacional', 'inovacao']
for cat in cats_interesse:
    vals = [v for e in rows if e['categoria'] == cat and (v := e.get('valor_anual_estimado')) is not None]
    if vals:
        md += f'| {cat} | {len(vals)} | R\$ {sum(vals):,.2f} | R\$ {statistics.mean(vals):,.2f} |\n'
    else:
        md += f'| {cat} | 0 | R\$ 0,00 | R\$ 0,00 |\n'

md += f"""
---

## 5. Tabela Detalhada de Editais

{tabela}

---

## 6. Editais com Valor TBD

Os seguintes {n_tbd} editais nao puderam ter seu valor estimado:
"""

for e in tbds:
    md += f'- **{e["nome"]}** ({e["agencia"]}): {e["valor_declarado"]} — {e["nota"]}\n'

md += f"""

---

## 7. Notas Metodologicas

1. **Valores em R\$:** Todos os valores foram convertidos para reais (R\$). Valores em US\$ usaram taxa de câmbio de R\$ 5,00/US\$.
2. **Valores mensais:** Bolsas mensais foram anualizadas: mestrado (24 meses), doutorado (48 meses), pos-doc (12 meses), sanduiche (12 meses).
3. **Ranges:** Para valores declarados como faixa (ex.: "R\$ 30.000 a R\$ 200.000"), utilizou-se o ponto medio.
4. **Valores compostos:** "Bolsa + auxilio" foram somados em um unico valor anual.
5. **Total teorico maximo:** Representa a soma se todos os editais fossem integralmente contratados — nao reflete a capacidade fiscal do Estado.
6. **TBD:** Editais com "a definir", "incentivo fiscal" ou valores nao determinaveis foram marcados como TBD e excluidos dos calculos numericos.
7. **Fontes:** Os valores baseiam-se nas tabelas oficiais das agencias (CNPq, CAPES, FINEP, FAPs) e em chamadas publicas historicas de 2024-2026.

---

*Relatorio gerado em {__import__('datetime').datetime.now().strftime('%d/%m/%Y as %H:%M')} | {n_total} editais curados | editais-br v7.2*
"""

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, 'w', encoding='utf-8') as f:
    f.write(md)

print(f'Relatorio salvo em: {OUT_PATH}')
print(f'Total teorico maximo: R$ {total:,.2f}')
print(f'Editais com valor: {n_valued}, TBD: {n_tbd}')
print(f'Media edital pesquisa: R$ {pesquisa_avg:,.2f}')
