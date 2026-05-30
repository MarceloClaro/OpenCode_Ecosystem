#!/usr/bin/env python3
"""
Merge CURATED_EDITAIS.json (financial) + CURATED_EDITAIS_SCORES.json (scores)
into a unified CURATED_EDITAIS_FULL.json with 65 complete entries.

Each entry: {id, nome, agencia, categoria, valor_declarado, valor_anual_estimado,
             nota_financeira, scores: {pesquisa, mestrado, doutorado, startup}, nota_score}
"""

import json, os, re, statistics
from difflib import SequenceMatcher

# --- BRL Parser (same logic as analise_financeira.py) ---
def parse_brl(s: str) -> float | None:
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
            if '+' in p:
                for sp in p.split('+'):
                    v = _parse_single_brl(sp.strip())
                    if v is not None: vals.append(v)
            else:
                v = _parse_single_brl(p)
                if v is not None: vals.append(v)
        if len(vals) >= 2:
            mid = (min(vals) + max(vals)) / 2
        elif len(vals) == 1:
            mid = vals[0]
        else:
            return None
        if is_usd: mid *= 5.0
        if is_monthly: mid *= 12
        return mid
    elif is_monthly:
        v = _parse_single_brl(s_clean)
        if v is None: return None
        if is_usd: v *= 5.0
        return v * 12
    else:
        v = _parse_single_brl(s_clean)
        if v is None: return None
        if is_usd: v *= 5.0
        return v

def _parse_single_brl(s: str) -> float | None:
    s = s.strip().replace('.', '').replace(',', '.')
    m = re.search(r'[\d.]+', s)
    if m:
        try: return float(m.group())
        except: return None
    return None
# --- end parser ---

CURATED = r'C:\Users\marce\.config\opencode\skills\research\editais-br\curated\CURATED_EDITAIS.json'
SCORES  = r'C:\Users\marce\.config\opencode\skills\research\editais-br\curated\CURATED_EDITAIS_SCORES.json'
OUTPUT  = r'C:\Users\marce\.config\opencode\skills\research\editais-br\curated\CURATED_EDITAIS_FULL.json'

with open(CURATED, 'r', encoding='utf-8') as f:
    editais_fin = json.load(f)

with open(SCORES, 'r', encoding='utf-8') as f:
    scores_data = json.load(f)

scores_list = scores_data.get('scores', [])
top2 = scores_data.get('top_2_per_profile', {})
worker_a = set(scores_data.get('worker_A_editais', []))
worker_b = set(scores_data.get('worker_B_editais', []))

def normalize(s: str) -> str:
    """Lowercase, remove accents, remove punctuation."""
    s = s.lower().strip()
    s = re.sub(r'[áàâãä]', 'a', s)
    s = re.sub(r'[éèêë]', 'e', s)
    s = re.sub(r'[íìîï]', 'i', s)
    s = re.sub(r'[óòôõö]', 'o', s)
    s = re.sub(r'[úùûü]', 'u', s)
    s = re.sub(r'[ç]', 'c', s)
    s = re.sub(r'[^a-z0-9 ]', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def match_score(nome_fin: str, scores_entries: list) -> dict | None:
    """Fuzzy-match a financial edital name to a scores entry."""
    nf = normalize(nome_fin)
    best = None
    best_ratio = 0.0
    for se in scores_entries:
        sn = normalize(se.get('nome', ''))
        # Also try matching against the scores entry id
        sid = normalize(se.get('id', '').replace('-', ' '))
        r1 = SequenceMatcher(None, nf, sn).ratio()
        r2 = SequenceMatcher(None, nf, sid).ratio()
        r = max(r1, r2)
        # Boost if key terms match
        terms_fin = set(nf.split())
        terms_s = set(sn.split())
        overlap = len(terms_fin & terms_s)
        if overlap >= 2:
            r += 0.1 * min(overlap / len(terms_fin), 1.0)
        if r > best_ratio:
            best_ratio = r
            best = se
    return best if best_ratio >= 0.3 else None

# Category-based default scores
CATEGORY_SCORES = {
    'pesquisa':      {'pesquisa': 70, 'mestrado': 30, 'doutorado': 45, 'startup': 15},
    'bolsa':         {'pesquisa': 15, 'mestrado': 70, 'doutorado': 68, 'startup': 5},
    'internacional': {'pesquisa': 40, 'mestrado': 50, 'doutorado': 65, 'startup': 10},
    'startup':       {'pesquisa': 20, 'mestrado': 10, 'doutorado': 12, 'startup': 80},
    'inovacao':      {'pesquisa': 35, 'mestrado': 10, 'doutorado': 15, 'startup': 65},
    'cultura':       {'pesquisa': 25, 'mestrado': 10, 'doutorado': 10, 'startup': 20},
    'social':        {'pesquisa': 40, 'mestrado': 20, 'doutorado': 25, 'startup': 35},
    'auxilio':       {'pesquisa': 65, 'mestrado': 10, 'doutorado': 20, 'startup': 30},
}

def generate_id(e: dict) -> str:
    """Generate a consistent ID from agencia + nome."""
    ag = e.get('agencia', '').upper().replace('/', '-').replace(' ', '-')
    nome_clean = re.sub(r'[^a-zA-Z0-9]', '', e.get('nome', ''))[:20]
    return f'{ag}-{nome_clean}'

results = []
matched_count = 0
auto_score_count = 0

for i, e in enumerate(editais_fin, 1):
    entry_id = e.get('id', generate_id(e))
    nome = e.get('nome', '')
    agencia = e.get('agencia', '')
    categoria = e.get('categoria', '')
    valor_dec = e.get('valor_declarado', '')
    valor_est = parse_brl(valor_dec)
    nota_fin = e.get('nota', '')

    # Try to match against scores
    se = match_score(nome, scores_list)

    if se:
        matched_count += 1
        scores_entry = {
            'pesquisa': se.get('pesquisa', 50),
            'mestrado': se.get('mestrado', 50),
            'doutorado': se.get('doutorado', 50),
            'startup': se.get('startup', 50),
        }
        score_note = f'Score carregado de: {se.get("id", "?")}'
        # Copy worker flags if they exist
        score_id = se.get('id', '')
        is_worker_a = score_id in worker_a or se.get('top_pesquisa') or se.get('top_mestrado')
        is_worker_b = score_id in worker_b or se.get('top_doutorado') or se.get('top_startup')
    else:
        auto_score_count += 1
        defaults = CATEGORY_SCORES.get(categoria, {'pesquisa': 50, 'mestrado': 30, 'doutorado': 35, 'startup': 25})
        scores_entry = defaults
        score_note = f'Score gerado automaticamente (categoria: {categoria})'
        is_worker_a = False
        is_worker_b = False

    entry = {
        'id': entry_id,
        'nome': nome,
        'agencia': agencia,
        'categoria': categoria,
        'valor_declarado': valor_dec,
        'valor_anual_estimado': valor_est,
        'nota_financeira': nota_fin,
        'scores': scores_entry,
        'nota_score': score_note,
        'worker_a': is_worker_a,
        'worker_b': is_worker_b,
    }
    results.append(entry)

# Build top 2 per profile (recalculated)
def top_n_by_profile(data, profile, n=2):
    scored = [(d['scores'].get(profile, 0), d) for d in data if d['scores'].get(profile, 0) > 0]
    scored.sort(key=lambda x: -x[0])
    return [{'rank': i+1, 'id': d['id'], 'nome': d['nome'], 'score': s}
            for i, (s, d) in enumerate(scored[:n])]

full_output = {
    'metadata': {
        'description': 'Dataset unificado de 65 editais de fomento brasileiros com scores e dados financeiros',
        'version': 'v7.2',
        'total_editais': len(results),
        'com_scores_de_curated': matched_count,
        'com_scores_automaticos': auto_score_count,
        'profiles': ['pesquisa', 'mestrado', 'doutorado', 'startup'],
        'scoring_criteria': {
            'pesquisa': 'Adequação a pesquisadores doutores: valor do projeto, tempo de execução, exigência de produção científica, abrangência multidisciplinar',
            'mestrado': 'Adequação a estudantes de mestrado: valor da bolsa, duração, requisitos de ingresso, possibilidade de vínculo com programa de pós',
            'doutorado': 'Adequação a doutorandos: valor da bolsa, duração, exigências acadêmicas, prestígio da agência',
            'startup': 'Adequação a startups e empresas de base tecnológica: valor do aporte, TRL exigido, contrapartida, prazo de execução, setor-alvo',
        },
        'financial_note': 'Valores anuais estimados em R$. Inclui anualizacao de bolsas mensais. Ranges usam ponto medio. Conversao US$→R$ a R$5,00.',
        'source_files': ['CURATED_EDITAIS.json', 'CURATED_EDITAIS_SCORES.json'],
        'financial_report': 'editais-br/relatorio_financeiro.md',
    },
    'editais': results,
    'top_2_per_profile': {
        'pesquisa': top_n_by_profile(results, 'pesquisa', 2),
        'mestrado': top_n_by_profile(results, 'mestrado', 2),
        'doutorado': top_n_by_profile(results, 'doutorado', 2),
        'startup': top_n_by_profile(results, 'startup', 2),
    },
    'worker_A_editais': [d['id'] for d in results if d.get('worker_a')],
    'worker_B_editais': [d['id'] for d in results if d.get('worker_b')],
    'resumo_financeiro': {
        'total_editais': len(results),
        'editais_com_valor': len([d for d in results if d['valor_anual_estimado'] is not None]),
        'total_teorico_maximo': sum(d['valor_anual_estimado'] for d in results if d['valor_anual_estimado'] is not None),
    },
}

os.makedirs(os.path.dirname(OUTPUT), exist_ok=True)
with open(OUTPUT, 'w', encoding='utf-8') as f:
    json.dump(full_output, f, ensure_ascii=False, indent=2)

print(f'[merge] {len(results)} editais salvos em:')
print(f'  {OUTPUT}')
print(f'  Scores matched (from curate scores): {matched_count}')
print(f'  Scores auto-generated: {auto_score_count}')
print(f'  Worker A: {len(full_output["worker_A_editais"])} editais')
print(f'  Worker B: {len(full_output["worker_B_editais"])} editais')
print(f'  Total teorico maximo: R$ {full_output["resumo_financeiro"]["total_teorico_maximo"]:,.2f}')
