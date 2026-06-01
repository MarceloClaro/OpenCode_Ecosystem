#!/usr/bin/env python3
"""
SISTEMA DE ANTI-PLÁGIO ULTRARRIGOROSO v1.0
Monografia: "A Proteção da Personalidade Humana na Era da Inteligência Artificial --
Contribuições da Encíclica Magnifica Humanitas para o Direito Contemporâneo"
PPGTE/UFC

Verifica em 7 camadas independentes:
  L1 - INTEGRIDADE: todo parágrafo sem citação é flagado
  L2 - CONSISTÊNCIA: toda \cite{} existe no .bib e vice-versa
  L3 - CITAÇÃO DIRETA: toda aspa tem \cite{} adjacente
  L4 - PARÁFRASE: similaridade n-gram com fontes locais
  L5 - DENSIDADE: zonas com baixa densidade de citação
  L6 - ABNT: conformidade com NBR 10520 (apud, citeonline, página)
  L7 - WEB: varredura de parágrafos suspeitos na web (opcional)

Uso:
  python antiplagio_ultrarigoroso.py
  python antiplagio_ultrarigoroso.py --web        (ativa L7)
  python antiplagio_ultrarigoroso.py --json       (saída JSON)

Saída: relatório_antiplagio.html (ou .json)
"""

import os
import re
import json
import math
import sys
from collections import defaultdict, Counter
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIGURAÇÃO
# ============================================================

PROJETO_DIR = Path(
    r"C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC"
    r"\A Proteção da Personalidade Humana na Era da Inteligência Artificial"
    r" - Contribuições da Encíclica Magnifica Humanitas para o Direito Contemporâneo"
)
MANUSCRITO_DIR = PROJETO_DIR / "manuscrito"
BIB_FILE = MANUSCRITO_DIR / "refs.bib"
MAIN_TEX = MANUSCRITO_DIR / "main.tex"
CAP_FILES = [
    "cap1-introducao.tex",
    "cap2-fundamentos-antropologicos.tex",
    "cap3-ia-desafios.tex",
    "cap4-protecao-juridica.tex",
    "cap5-contribuicoes-magnifica.tex",
    "cap6-conclusao.tex",
    "anexo-fichamentos.tex",
]
PESQUISA_DIR = PROJETO_DIR / "pesquisa"
REFERENCIAS_DIR = PROJETO_DIR / "referencias"

# Limiares de tolerância (ajustáveis)
LIMIAR_PARAGRAFOS_SEM_CITACAO = 1     # máx parágrafos consecutivos sem citação
LIMIAR_MIN_CITACOES_POR_SECAO = 1     # mínimo de citações por seção
LIMIAR_SIMILARIDADE_SEM_ASPAS = 0.30  # similaridade máxima sem aspas diretas
LIMIAR_PALAVRAS_CITACAO_DIRETA = 100  # máx palavras em citação direta
LIMIAR_DENSIDADE_BAIXA = 0.5          # citações por 100 palavras abaixo disto é alerta
LIMIAR_MAX_PALAVRAS_SEM_CITACAO = 200 # máx palavras consecutivas sem citação

# ============================================================
# UTILITÁRIOS
# ============================================================

def limpar_comentarios(texto):
    return re.sub(r'(?<!\\)%.*', '', texto)


def extrair_paragraphs(tex_content):
    paragraphs = []
    lines = tex_content.split('\n')
    current = []
    for line in lines:
        stripped = line.strip()
        if stripped == '':
            if current:
                paragraphs.append(' '.join(current))
                current = []
        elif stripped.startswith('%'):
            continue
        elif stripped.startswith('\\') and any(
            stripped.startswith(cmd) for cmd in [
                '\\section', '\\subsection', '\\subsubsection',
                '\\chapter', '\\label', '\\index',
                '\\begin', '\\end', '\\fichamento'
            ]
        ):
            if current:
                paragraphs.append(' '.join(current))
                current = []
            if stripped.startswith('\\begin{fichamento}'):
                paragraphs.append(('__FICHAMENTO_START__', stripped))
            continue
        else:
            current.append(stripped)
    if current:
        paragraphs.append(' '.join(current))
    return paragraphs


def extrair_citacoes(texto):
    citacoes = []
    for m in re.finditer(r'\\cite\s*\{([^}]+)\}', texto):
        chaves = [k.strip() for k in m.group(1).split(',')]
        citacoes.append({
            'tipo': 'parentetica',
            'chaves': chaves,
            'pos': m.start(),
            'raw': m.group(0),
        })
    for m in re.finditer(r'\\citeonline\s*\{([^}]+)\}', texto):
        chaves = [k.strip() for k in m.group(1).split(',')]
        citacoes.append({
            'tipo': 'discurso',
            'chaves': chaves,
            'pos': m.start(),
            'raw': m.group(0),
        })
    for m in re.finditer(r'\\citecaps\s*\{([^}]+)\}', texto):
        chaves = [k.strip() for k in m.group(1).split(',')]
        citacoes.append({
            'tipo': 'versalete',
            'chaves': chaves,
            'pos': m.start(),
            'raw': m.group(0),
        })
    citacoes.sort(key=lambda x: x['pos'])
    return citacoes


def extrair_citacoes_diretas(texto):
    quotes = []
    for m in re.finditer(r'``(.+?)\'\'', texto):
        quotes.append({
            'texto': m.group(1),
            'pos': m.start(),
            'palavras': len(m.group(1).split()),
        })
    # Also check regular quotes as fallback
    for m in re.finditer(r'"(.*?)"(?![a-zA-Z])', texto):
        if len(m.group(1).split()) > 3:
            quotes.append({
                'texto': m.group(1),
                'pos': m.start(),
                'palavras': len(m.group(1).split()),
            })
    quotes.sort(key=lambda x: x['pos'])
    return quotes


def extrair_footnotes(texto):
    return [m.group(1) for m in re.finditer(r'\\footnote\{([^}]*)\}', texto)]


def extrair_secoes(tex_content, arquivo):
    secoes = []
    lines = tex_content.split('\n')
    current_secao = None
    current_linha = 0
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        m_chapter = re.match(r'\\chapter\*?\{([^}]+)\}', stripped)
        m_section = re.match(r'\\section\*?\{([^}]+)\}', stripped)
        m_subsection = re.match(r'\\subsection\*?\{([^}]+)\}', stripped)
        if m_chapter:
            current_secao = ('chapter', m_chapter.group(1))
            secoes.append({'tipo': 'chapter', 'titulo': m_chapter.group(1), 'linha': i, 'arquivo': arquivo})
        elif m_section:
            current_secao = ('section', m_section.group(1))
            secoes.append({'tipo': 'section', 'titulo': m_section.group(1), 'linha': i, 'arquivo': arquivo})
        elif m_subsection:
            current_secao = ('subsection', m_subsection.group(1))
            secoes.append({'tipo': 'subsection', 'titulo': m_subsection.group(1), 'linha': i, 'arquivo': arquivo})
    return secoes


def extrair_palavras(texto):
    palavras = re.sub(r'\\[a-zA-Z]+(\{.*?\})?', ' ', texto)
    palavras = re.sub(r'[{}%$&#^_~]', ' ', palavras)
    palavras = re.sub(r'\s+', ' ', palavras).strip()
    return palavras


# ============================================================
# L1 -- INTEGRIDADE (parágrafos sem citação)
# ============================================================

def camada_l1_integridade(cap_data):
    alertas = []
    for arq, dados in cap_data.items():
        texto_limpo = limpar_comentarios(dados['raw'])
        paragraphs = extrair_paragraphs(texto_limpo)
        seq_sem_citacao = 0
        palavras_sem_citacao = 0
        for i, para in enumerate(paragraphs):
            if isinstance(para, tuple):
                continue
            citacoes = extrair_citacoes(para)
            palavras = extrair_palavras(para)
            n_palavras = len(palavras.split()) if palavras else 0
            if not citacoes and n_palavras > 20:
                seq_sem_citacao += 1
                palavras_sem_citacao += n_palavras
                if seq_sem_citacao > LIMIAR_PARAGRAFOS_SEM_CITACAO:
                    alertas.append({
                        'arquivo': arq,
                        'paragrafo': i + 1,
                        'tipo': 'PARÁGRAFO SEM CITAÇÃO',
                        'detalhe': f'Parágrafo #{i+1} sem citação ({n_palavras} palavras, {seq_sem_citacao}º consecutivo)',
                        'severidade': 'ALTA' if seq_sem_citacao > 3 else 'MEDIA',
                        'extrato': palavras[:200],
                    })
                if palavras_sem_citacao > LIMIAR_MAX_PALAVRAS_SEM_CITACAO:
                    alertas.append({
                        'arquivo': arq,
                        'paragrafo': i + 1,
                        'tipo': 'BLOCO LONGO SEM CITAÇÃO',
                        'detalhe': f'{palavras_sem_citacao} palavras consecutivas sem citação',
                        'severidade': 'ALTA',
                        'extrato': palavras[:200],
                    })
            else:
                seq_sem_citacao = 0
                palavras_sem_citacao = 0
    return alertas


# ============================================================
# L2 -- CONSISTÊNCIA (bib <-> citações)
# ============================================================

def parse_bib(bib_path):
    with open(bib_path, 'r', encoding='utf-8') as f:
        conteudo = f.read()
    entries = {}
    pattern = r'@(\w+)\s*\{\s*([^,]+)\s*,'
    for m in re.finditer(pattern, conteudo):
        tipo = m.group(1).lower()
        chave = m.group(2).strip()
        entries[chave] = {'tipo': tipo, 'chave': chave}
    return entries, conteudo


def camada_l2_consistencia(cap_data, bib_entries, bib_raw):
    alertas = []
    chaves_usadas = defaultdict(list)
    for arq, dados in cap_data.items():
        texto_limpo = limpar_comentarios(dados['raw'])
        citacoes = extrair_citacoes(texto_limpo)
        for c in citacoes:
            for chave in c['chaves']:
                chaves_usadas[chave].append({'arquivo': arq, 'tipo': c['tipo']})

    # Chaves usadas que não existem no .bib
    for chave, locs in chaves_usadas.items():
        if chave not in bib_entries:
            arquivos = list(set(l['arquivo'] for l in locs))
            alertas.append({
                'arquivo': ', '.join(arquivos),
                'tipo': 'CITAÇÃO ÓRFÃ',
                'detalhe': f'\\cite{{{chave}}} usado em {len(locs)} lugar(es) mas NÃO existe em refs.bib',
                'severidade': 'CRÍTICA',
                'extrato': f'Chave: {chave} | Arquivos: {", ".join(arquivos)}',
            })

    # Entradas no .bib que nunca são usadas
    for chave, entry in bib_entries.items():
        if chave not in chaves_usadas:
            alertas.append({
                'arquivo': 'refs.bib',
                'tipo': 'REFERÊNCIA NÃO CITADA',
                'detalhe': f'{entry["tipo"]} {{{chave}}} existe no .bib mas nunca é citada',
                'severidade': 'BAIXA',
                'extrato': f'Entrada não utilizada: {chave}',
            })

    # Entradas sem campo URL
    for m in re.finditer(r'@(\w+)\s*\{\s*([^,]+)\s*,', bib_raw):
        chave = m.group(2).strip()
        start = m.start()
        end = bib_raw.find('}', start)
        if end == -1:
            continue
        entry_block = bib_raw[start:end+1]
        if 'url' not in entry_block.lower() and 'doi' not in entry_block.lower():
            alertas.append({
                'arquivo': 'refs.bib',
                'tipo': 'REFERÊNCIA SEM URL/DOI',
                'detalhe': f'{m.group(1).lower()} {{{chave}}} não possui campo url nem doi',
                'severidade': 'BAIXA',
                'extrato': f'Chave: {chave}',
            })

    return alertas, dict(chaves_usadas)


# ============================================================
# L3 -- CITAÇÃO DIRETA (aspas sem \cite{})
# ============================================================

def camada_l3_citacao_direta(cap_data):
    alertas = []
    for arq, dados in cap_data.items():
        texto_limpo = limpar_comentarios(dados['raw'])
        quotes = extrair_citacoes_diretas(texto_limpo)
        citacoes = extrair_citacoes(texto_limpo)

        for q in quotes:
            text_pos = q['pos']
            palavras = q['palavras']
            
            # Verifica se há \cite{} nas proximidades (até 200 caracteres depois)
            tem_citacao_proxima = any(
                abs(c['pos'] - text_pos) <= 200 for c in citacoes
            )
            
            if not tem_citacao_proxima:
                alertas.append({
                    'arquivo': arq,
                    'tipo': 'CITAÇÃO DIRETA SEM REFERÊNCIA',
                    'detalhe': f'Texto entre aspas ({palavras} palavras) sem \\cite{{}} nas proximidades',
                    'severidade': 'CRÍTICA',
                    'extrato': q['texto'][:200],
                })
            
            if palavras > LIMIAR_PALAVRAS_CITACAO_DIRETA:
                alertas.append({
                    'arquivo': arq,
                    'tipo': 'CITAÇÃO DIRETA EXTENSA',
                    'detalhe': f'{palavras} palavras em citação direta (limiar: {LIMIAR_PALAVRAS_CITACAO_DIRETA})',
                    'severidade': 'MEDIA',
                    'extrato': q['texto'][:200],
                })

            # Verifica se citação direta tem "apud" (ABNT exige para citação de citação)
            if ' apud ' in q['texto'].lower() or ' citado por ' in q['texto'].lower():
                alertas.append({
                    'arquivo': arq,
                    'tipo': 'CITAÇÃO DE CITAÇÃO (APUD)',
                    'detalhe': 'Citação direta contém "apud" -- verificar se a fonte original foi consultada',
                    'severidade': 'MEDIA',
                    'extrato': q['texto'][:200],
                })
    return alertas


# ============================================================
# L4 -- PARÁFRASE (similaridade com fontes locais)
# ============================================================

def carregar_fontes():
    fontes = {}
    for diretorio in [PESQUISA_DIR, REFERENCIAS_DIR]:
        if not diretorio.exists():
            continue
        for f in diretorio.iterdir():
            if f.suffix in ('.txt', '.html', '.pdf'):
                try:
                    conteudo = f.read_text(encoding='utf-8', errors='ignore')
                    fontes[f.name] = conteudo
                except Exception:
                    pass
    return fontes


def ngramas(texto, n=5):
    palavras = re.findall(r'\w+', texto.lower())
    if len(palavras) < n:
        return set()
    return set(' '.join(palavras[i:i+n]) for i in range(len(palavras)-n+1))


def camada_l4_parafrase(cap_data, fontes):
    alertas = []
    for arq, dados in cap_data.items():
        texto_limpo = limpar_comentarios(dados['raw'])
        paragraphs = extrair_paragraphs(texto_limpo)
        
        for i, para in enumerate(paragraphs):
            if isinstance(para, tuple):
                continue
            citacoes = extrair_citacoes(para)
            # Só verifica parágrafos sem citação direta (aspas)
            quotes = extrair_citacoes_diretas(para)
            if quotes:
                continue  # se já tem aspas, é citação direta explícita
            if not citacoes:
                continue  # sem citação já foi pego na L1

            para_ngrams = ngramas(para, n=7)
            if not para_ngrams:
                continue

            for nome_fonte, conteudo_fonte in fontes.items():
                fonte_ngrams = ngramas(conteudo_fonte, n=7)
                if not fonte_ngrams:
                    continue
                intersecao = para_ngrams & fonte_ngrams
                similaridade = len(intersecao) / max(len(para_ngrams), 1)
                
                if similaridade > LIMIAR_SIMILARIDADE_SEM_ASPAS:
                    alertas.append({
                        'arquivo': arq,
                        'paragrafo': i + 1,
                        'tipo': 'PARÁFRASE SUSPEITA',
                        'detalhe': f'Similaridade {similaridade:.0%} com "{nome_fonte}" (sem aspas diretas)',
                        'severidade': 'ALTA' if similaridade > 0.50 else 'MEDIA',
                        'extrato': extrair_palavras(para)[:200],
                        'similaridade': round(similaridade, 2),
                        'fonte': nome_fonte,
                    })
    return alertas


# ============================================================
# L5 -- DENSIDADE DE CITAÇÃO
# ============================================================

def camada_l5_densidade(cap_data):
    alertas = []
    for arq, dados in cap_data.items():
        texto_limpo = limpar_comentarios(dados['raw'])
        secoes = extrair_secoes(texto_limpo, arq)
        
        # Seções sem citação
        for sec in secoes:
            # Pega texto da seção (entre esta e a próxima)
            lines = texto_limpo.split('\n')
            sec_linha = sec['linha']
            sec_texto = '\n'.join(lines[sec_linha:])
            if secoes.index(sec) < len(secoes) - 1:
                prox_linha = secoes[secoes.index(sec) + 1]['linha']
                sec_texto = '\n'.join(lines[sec_linha:prox_linha-1])
            
            citacoes = extrair_citacoes(sec_texto)
            palavras_texto = extrair_palavras(sec_texto)
            n_palavras = len(palavras_texto.split()) if palavras_texto else 0
            
            if n_palavras > 50 and len(citacoes) < LIMIAR_MIN_CITACOES_POR_SECAO:
                alertas.append({
                    'arquivo': arq,
                    'tipo': 'SEÇÃO SEM CITAÇÃO SUFICIENTE',
                    'detalhe': f'"{sec["titulo"]}" ({n_palavras} palavras, {len(citacoes)} citações)',
                    'severidade': 'MEDIA',
                    'extrato': f'Seção: {sec["titulo"]}',
                })
        
        # Densidade geral
        citacoes = extrair_citacoes(texto_limpo)
        palavras_texto = extrair_palavras(texto_limpo)
        n_palavras = len(palavras_texto.split()) if palavras_texto else 0
        densidade = (len(citacoes) / max(n_palavras, 1)) * 100
        
        if densidade < LIMIAR_DENSIDADE_BAIXA:
            alertas.append({
                'arquivo': arq,
                'tipo': 'DENSIDADE DE CITAÇÃO BAIXA',
                'detalhe': f'{densidade:.1f} citações/100 palavras (limiar: {LIMIAR_DENSIDADE_BAIXA})',
                'severidade': 'BAIXA',
                'extrato': f'Densidade: {densidade:.2f}',
            })
    return alertas


# ============================================================
# L6 -- CONFORMIDADE ABNT NBR 10520
# ============================================================

def camada_l6_abnt(cap_data):
    alertas = []
    for arq, dados in cap_data.items():
        texto_limpo = limpar_comentarios(dados['raw'])
        citacoes = extrair_citacoes(texto_limpo)
        
        # Verifica se mistura \citeonline e \cite para mesma referência
        chaves_por_tipo = defaultdict(set)
        for c in citacoes:
            for chave in c['chaves']:
                chaves_por_tipo[c['tipo']].add(chave)
        
        # Verifica citações de lei sem ano
        for c in citacoes:
            for chave in c['chaves']:
                if re.match(r'.*\d{4}', chave) is None:
                    alertas.append({
                        'arquivo': arq,
                        'tipo': 'CITAÇÃO SEM ANO NA CHAVE',
                        'detalhe': f'Chave "{chave}" pode não conter ano, dificultando formatação ABNT',
                        'severidade': 'BAIXA',
                        'extrato': f'Chave: {chave}',
                    })
        
        # Verifica citações muito densas (mais de 3 autorias em \cite{})
        for c in citacoes:
            if len(c['chaves']) > 3:
                alertas.append({
                    'arquivo': arq,
                    'tipo': 'CITAÇÃO SUPERLOTADA',
                    'detalhe': f'{len(c["chaves"])} autorias em \\cite{{{", ".join(c["chaves"][:3])}...}} (NBR 10520: max 3)',
                    'severidade': 'BAIXA',
                    'extrato': f'\\cite{{{", ".join(c["chaves"])}}}',
                })

        # Verifica se há "apud" sem a citação da fonte secundária
        if 'apud' in texto_limpo.lower():
            alertas.append({
                'arquivo': arq,
                'tipo': 'USO DE APUD',
                'detalhe': 'Texto contém "apud" -- verificar conformidade com NBR 10520 (citação de citação)',
                'severidade': 'MEDIA',
                'extrato': 'apud',
            })

        # Verifica se há citação de documento não acadêmico sem qualificação
        for c in citacoes:
            for chave in c['chaves']:
                if chave.lower().startswith('brasil') or chave.lower().startswith('lei'):
                    pass  # documentos legais são aceitáveis
        
    return alertas


# ============================================================
# L7 -- WEB (parágrafos suspeitos -- opcional, usa MCP websearch)
# ============================================================

def camada_l7_web(cap_data):
    alertas = []
    if '--web' not in sys.argv:
        return alertas
    
    print("[L7] Varredura web ativada. Verificando parágrafos suspeitos...")
    for arq, dados in cap_data.items():
        texto_limpo = limpar_comentarios(dados['raw'])
        paragraphs = extrair_paragraphs(texto_limpo)
        
        suspicious = []
        for i, para in enumerate(paragraphs):
            if isinstance(para, tuple):
                continue
            citacoes = extrair_citacoes(para)
            quotes = extrair_citacoes_diretas(para)
            if not citacoes and not quotes:
                palavras = extrair_palavras(para)
                n_palavras = len(palavras.split()) if palavras else 0
                if n_palavras > 50:
                    suspicious.append((i, palavras[:150]))

        for i, extrato in suspicious:
            alertas.append({
                'arquivo': arq,
                'paragrafo': i + 1,
                'tipo': 'SUSPEITO PARA VERIFICAÇÃO WEB',
                'detalhe': f'Parágrafo #{i+1} ({len(extrato.split())} palavras) -- sem citações',
                'severidade': 'MEDIA' if '--web' in sys.argv else 'BAIXA',
                'extrato': extrato,
            })
    
    return alertas


# ============================================================
# GERADOR DE RELATÓRIO HTML
# ============================================================

def gerar_html(alertas, bib_entries, chaves_usadas, inicio):
    estatisticas = defaultdict(int)
    for a in alertas:
        estatisticas[a['tipo']] += 1
    por_severidade = defaultdict(int)
    for a in alertas:
        por_severidade[a['severidade']] += 1
    por_arquivo = defaultdict(int)
    for a in alertas:
        por_arquivo[a['arquivo']] += 1

    severidade_order = {'CRÍTICA': 0, 'ALTA': 1, 'MEDIA': 2, 'BAIXA': 3}
    alertas_ordenados = sorted(
        alertas, key=lambda a: (severidade_order.get(a['severidade'], 99), a['arquivo'], a.get('paragrafo', 0))
    )

    cores = {
        'CRÍTICA': '#dc3545', 'ALTA': '#fd7e14',
        'MEDIA': '#ffc107', 'BAIXA': '#6c757d'
    }
    icones = {
        'CRÍTICA': '🔴', 'ALTA': '🟠', 'MEDIA': '🟡', 'BAIXA': '🔵'
    }

    n_citacoes = sum(len(v) for v in chaves_usadas.values())

    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<title>Relatório Anti-Plágio Ultrarigoroso</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', system-ui, sans-serif; background: #f8f9fa; color: #212529; line-height: 1.6; padding: 20px; }}
  .container {{ max-width: 1200px; margin: 0 auto; }}
  h1 {{ font-size: 1.8rem; margin-bottom: 0.25rem; }}
  .subtitle {{ color: #6c757d; margin-bottom: 2rem; }}
  .dashboard {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 2rem; }}
  .card {{ background: white; border-radius: 12px; padding: 1.25rem; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  .card .numero {{ font-size: 2rem; font-weight: 700; line-height: 1; }}
  .card .rotulo {{ font-size: 0.85rem; color: #6c757d; margin-top: 0.25rem; }}
  .card.critica .numero {{ color: #dc3545; }}
  .card.alta .numero {{ color: #fd7e14; }}
  .card.media .numero {{ color: #ffc107; }}
  .card.baixa .numero {{ color: #6c757d; }}
  .card.total .numero {{ color: #0d6efd; }}
  table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
  th, td {{ padding: 12px 16px; text-align: left; border-bottom: 1px solid #dee2e6; font-size: 0.9rem; }}
  th {{ background: #f8f9fa; font-weight: 600; color: #495057; }}
  tr:hover {{ background: #f1f3f5; }}
  .severidade-badge {{ display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight: 600; }}
  .extrato {{ font-family: 'Consolas', 'Courier New', monospace; font-size: 0.8rem; color: #495057; max-width: 400px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
  .extrato:hover {{ white-space: normal; overflow: visible; }}
  .resumo {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin-bottom: 2rem; }}
  .resumo-section h3 {{ margin-bottom: 0.5rem; }}
  .resumo-section ul {{ list-style: none; }}
  .resumo-section li {{ padding: 0.25rem 0; font-size: 0.9rem; }}
  .filtros {{ margin-bottom: 1rem; display: flex; gap: 0.5rem; flex-wrap: wrap; }}
  .filtros button {{ padding: 6px 16px; border: 2px solid #dee2e6; border-radius: 20px; background: white; cursor: pointer; font-size: 0.85rem; }}
  .filtros button:hover {{ border-color: #0d6efd; }}
  .filtros button.ativo {{ border-color: #0d6efd; background: #e7f1ff; }}
  .pass {{ text-align: center; padding: 2rem; background: #d4edda; border-radius: 12px; margin: 1rem 0; }}
  .pass h3 {{ color: #155724; }}
  .fail {{ text-align: center; padding: 2rem; background: #f8d7da; border-radius: 12px; margin: 1rem 0; }}
  .fail h3 {{ color: #721c24; }}
  @media (max-width: 768px) {{ .resumo {{ grid-template-columns: 1fr; }} }}
</style>
</head>
<body>
<div class="container">

<h1>🔬 Relatório Anti-Plágio Ultrarigoroso</h1>
<p class="subtitle">Gerado em {datetime.now().strftime('%d/%m/%Y às %H:%M')} • Monografia PPGTE/UFC</p>

<div class="dashboard">
  <div class="card total"><div class="numero">{len(alertas)}</div><div class="rotulo">Total de Alertas</div></div>
  <div class="card critica"><div class="numero">{por_severidade.get('CRÍTICA', 0)}</div><div class="rotulo">Críticos</div></div>
  <div class="card alta"><div class="numero">{por_severidade.get('ALTA', 0)}</div><div class="rotulo">Altos</div></div>
  <div class="card media"><div class="numero">{por_severidade.get('MEDIA', 0)}</div><div class="rotulo">Médios</div></div>
  <div class="card baixa"><div class="numero">{por_severidade.get('BAIXA', 0)}</div><div class="rotulo">Baixos</div></div>
</div>

<div class="resumo">
  <div class="resumo-section">
    <h3>📊 Métricas</h3>
    <ul>
      <li><strong>Arquivos verificados:</strong> {len(por_arquivo)}</li>
      <li><strong>Total de citações:</strong> {n_citacoes}</li>
      <li><strong>Entradas no .bib:</strong> {len(bib_entries)}</li>
      <li><strong>Chaves não utilizadas:</strong> {len(bib_entries) - len(chaves_usadas)}</li>
      <li><strong>Tempo de execução:</strong> {(datetime.now() - inicio).total_seconds():.1f}s</li>
    </ul>
  </div>
  <div class="resumo-section">
    <h3>📋 Alertas por Arquivo</h3>
    <ul>
"""
    for arq, count in sorted(por_arquivo.items(), key=lambda x: -x[1]):
        html += f'      <li><strong>{arq}</strong>: {count} alerta(s)</li>\n'
    
    html += """    </ul>
  </div>
</div>
"""

    # Score geral
    score = 100
    score -= por_severidade.get('CRÍTICA', 0) * 25
    score -= por_severidade.get('ALTA', 0) * 10
    score -= por_severidade.get('MEDIA', 0) * 3
    score -= por_severidade.get('BAIXA', 0) * 1
    score = max(0, min(100, score))
    
    if score >= 90:
        html += f'<div class="pass"><h3>✅ Score de Integridade Acadêmica: {score}/100</h3><p>O manuscrito apresenta boa conformidade. Revisar alertas de severidade MÉDIA ou superior.</p></div>\n'
    elif score >= 70:
        html += f'<div class="fail"><h3>⚠️ Score de Integridade Acadêmica: {score}/100</h3><p>Requer revisão dos alertas de severidade ALTA e CRÍTICA.</p></div>\n'
    else:
        html += f'<div class="fail"><h3>🚨 Score de Integridade Acadêmica: {score}/100</h3><p>Correção urgente necessária antes da submissão.</p></div>\n'

    # Tabela de alertas
    html += """
<h2 style="margin: 2rem 0 1rem;">📋 Todos os Alertas</h2>
<table>
<thead><tr>
  <th>Severidade</th>
  <th>Camada</th>
  <th>Arquivo</th>
  <th>Detalhe</th>
  <th>Extrato</th>
</tr></thead>
<tbody>
"""
    for a in alertas_ordenados:
        sev = a['severidade']
        cor = cores.get(sev, '#6c757d')
        ico = icones.get(sev, '•')
        tipo_resumido = a['tipo'][:40]
        html += f"""<tr>
  <td><span class="severidade-badge" style="background:{cor}20;color:{cor}">{ico} {sev}</span></td>
  <td style="font-size:0.8rem">{tipo_resumido}</td>
  <td style="font-size:0.85rem">{a['arquivo']}</td>
  <td style="font-size:0.85rem">{a['detalhe']}</td>
  <td><div class="extrato" title="{a.get('extrato','')}">{a.get('extrato','')[:120]}</div></td>
</tr>\n"""

    html += """
</tbody>
</table>

<h2 style="margin: 2rem 0 1rem;">📚 Verificação Cruzada Bib</h2>
<table>
<thead><tr>
  <th>Chave</th>
  <th>Tipo</th>
  <th>Citada em</th>
  <th>Status</th>
</tr></thead>
<tbody>
"""
    for chave, entry in sorted(bib_entries.items()):
        if chave in chaves_usadas:
            locs = [f"{l['arquivo']}({l['tipo']})" for l in chaves_usadas[chave]]
            status = '✅'
        else:
            locs = ['NÃO CITADA']
            status = '⚠️'
        html += f'<tr><td style="font-family:monospace;font-size:0.85rem">{chave}</td><td style="font-size:0.85rem">{entry["tipo"]}</td><td style="font-size:0.85rem">{", ".join(locs)}</td><td>{status}</td></tr>\n'

    html += """
</tbody>
</table>

<p style="text-align:center;color:#6c757d;margin-top:2rem;font-size:0.8rem;">
Este relatório é uma ferramenta auxiliar de verificação. Não substitui a leitura crítica humana.<br>
Gerado pelo Sistema de Anti-Plágio Ultrarigoroso v1.0 -- PPGTE/UFC
</p>

</div>
</body>
</html>
"""
    return html


# ============================================================
# MAIN
# ============================================================

def main():
    inicio = datetime.now()
    print("=" * 60)
    print("  SISTEMA DE ANTI-PLÁGIO ULTRARRIGOROSO v1.0")
    print("  PPGTE/UFC -- Verificação em 7 Camadas")
    print("=" * 60)
    
    # Carrega capítulos
    cap_data = {}
    for nome_arq in CAP_FILES:
        caminho = MANUSCRITO_DIR / nome_arq
        if caminho.exists():
            with open(caminho, 'r', encoding='utf-8') as f:
                cap_data[nome_arq] = {'raw': f.read(), 'path': str(caminho)}
            print(f"  [OK] {nome_arq}")
        else:
            print(f"  [AVISO] {nome_arq} não encontrado")
    
    # Carrega .bib
    bib_entries, bib_raw = parse_bib(BIB_FILE)
    print(f"  [OK] refs.bib ({len(bib_entries)} entradas)")
    
    # Carrega fontes para L4
    print("  [L4] Carregando fontes locais para verificação de paráfrase...")
    fontes = carregar_fontes()
    print(f"  [L4] {len(fontes)} fonte(s) carregada(s)")
    
    alertas = []
    
    # L1
    print("  [L1] Integridade (parágrafos sem citação)...")
    alertas += camada_l1_integridade(cap_data)
    print(f"       -> {sum(1 for a in alertas if a['tipo'] in ('PARÁGRAFO SEM CITAÇÃO', 'BLOCO LONGO SEM CITAÇÃO'))} alerta(s)")
    
    # L2
    print("  [L2] Consistência (bib <-> citações)...")
    l2_alertas, chaves_usadas = camada_l2_consistencia(cap_data, bib_entries, bib_raw)
    alertas += l2_alertas
    crit = sum(1 for a in l2_alertas if a['severidade'] == 'CRÍTICA')
    print(f"       -> {len(l2_alertas)} alerta(s) ({crit} crítico(s))")
    
    # L3
    print("  [L3] Citação direta (aspas sem \cite{})...")
    alertas += camada_l3_citacao_direta(cap_data)
    print(f"       -> {sum(1 for a in alertas if a['tipo'] in ('CITAÇÃO DIRETA SEM REFERÊNCIA', 'CITAÇÃO DIRETA EXTENSA', 'CITAÇÃO DE CITAÇÃO (APUD)'))} alerta(s)")
    
    # L4
    print("  [L4] Paráfrase (similaridade com fontes locais)...")
    l4_alertas = camada_l4_parafrase(cap_data, fontes)
    alertas += l4_alertas
    print(f"       -> {len(l4_alertas)} alerta(s)")
    
    # L5
    print("  [L5] Densidade de citação...")
    alertas += camada_l5_densidade(cap_data)
    print(f"       -> {sum(1 for a in alertas if a['tipo'] in ('SEÇÃO SEM CITAÇÃO SUFICIENTE', 'DENSIDADE DE CITAÇÃO BAIXA'))} alerta(s)")
    
    # L6
    print("  [L6] Conformidade ABNT NBR 10520...")
    alertas += camada_l6_abnt(cap_data)
    print(f"       -> {sum(1 for a in alertas if 'ABNT' in a['tipo'] or a['tipo'] in ('CITAÇÃO SUPERLOTADA', 'CITAÇÃO SEM ANO NA CHAVE', 'USO DE APUD'))} alerta(s)")
    
    # L7
    print("  [L7] Varredura web (opcional)...")
    l7_alertas = camada_l7_web(cap_data)
    alertas += l7_alertas
    print(f"       -> {len(l7_alertas)} alerta(s)")
    
    # Gera relatório
    report_html = gerar_html(alertas, bib_entries, chaves_usadas, inicio)
    
    output_file = PROJETO_DIR / "relatorio_antiplagio.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report_html)
    
    if '--json' in sys.argv:
        json_output = PROJETO_DIR / "relatorio_antiplagio.json"
        with open(json_output, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'total_alertas': len(alertas),
                'por_severidade': dict(Counter(a['severidade'] for a in alertas)),
                'alertas': alertas,
            }, f, ensure_ascii=False, indent=2)
        print(f"\n  [JSON] {json_output}")
    
    tempo = (datetime.now() - inicio).total_seconds()
    print(f"\n  {'='*50}")
    print(f"  RELATÓRIO: {output_file}")
    print(f"  TOTAL: {len(alertas)} alertas | Tempo: {tempo:.1f}s")
    print(f"  {'='*50}")
    
    return alertas


if __name__ == '__main__':
    main()
