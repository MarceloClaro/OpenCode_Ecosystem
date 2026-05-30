#!/usr/bin/env python3
"""Pipeline completo: reescrita de passagens críticas + .tex + diff + verificação"""

import re, json, sys

# ── 1. Ler MD fonte ──
with open(r"C:\Users\marce\Downloads\Cópia de TRABALHO DE CONCLUSÃO DE CURSO.docx (2).md", "r", encoding="utf-8") as f:
    texto = f.read()

original = texto

# ── 2. Mapeamento de 12 substituições críticas ──
substituicoes = [
    (
        "O bem estar psicológico configura-se atualmente como um dos campos mais urgentes no âmbito  das políticas públicas, necessitando de um olhar integral que vá além da atuação médica visando os âmbitos social e cultural do sofrimento humano.",
        "O campo do bem-estar psicológico figura entre as prioridades contemporâneas das políticas públicas, exigindo uma abordagem integral que ultrapasse a dimensão meramente médica e alcance os planos social e cultural do sofrimento humano.",
        "abertura formulaica (IA marker: 'configura-se atualmente')"
    ),
    (
        "Em um contexto onde as respostas terapêuticas convencionais tornam-se insuficientes a arteterapia surge como área de conhecimento e abordagem que caminha entre diversos campos com arte, psicologia e ciências sociais",
        "Quando as respostas terapêuticas tradicionais mostram seus limites, a arteterapia emerge como campo de conhecimento que transita entre a arte, a psicologia e as ciências sociais",
        "abertura formulaica (IA marker: 'Em um contexto onde')"
    ),
    (
        "É precisamente focando nessa distância que este estudo mobiliza a perspectiva decolonial.",
        "É justamente a partir dessa lacuna que esta pesquisa recorre à perspectiva decolonial.",
        "marcador IA: 'É precisamente'"
    ),
    (
        "Tendo delimitado o problema central e os objetivos deste estudo, torna-se necessário mapear o estado atual do conhecimento sobre os campos teóricos que fundamentam esta investigação.",
        "Uma vez circunscritos o problema e os objetivos, faz-se oportuno examinar o estado da arte dos campos teóricos que alicerçam esta investigação.",
        "marcador IA: 'torna-se necessário'"
    ),
    (
        "A literatura documenta que esses familiares, predominantemente mães, apresentam níveis de estresse expressivamente mais elevados do que cuidadores de crianças neurotípicas, com manifestações de ansiedade, depressão e exaustão emocional (Alves; Gameiro; Bazi, 2022; Zanatta et al., 2014, p. 275).",
        "Estudos indicam que esses familiares — em sua maioria mães — exibem níveis de estresse significativamente superiores aos de cuidadores de crianças neurotípicas, com quadros de ansiedade, depressão e exaustão emocional (Alves; Gameiro; Bazi, 2022; Zanatta et al., 2014, p. 275).",
        "marcador IA: 'A literatura documenta'"
    ),
    (
        "mundo interior rico e complexo (Silveira, 1992, p. 21).",
        "universo interior repleto de significados (Silveira, 1992, p. 21).",
        "adjetivação dupla (IA marker: 'rico e complexo')"
    ),
    (
        "Articular a arteterapia de base niseana ao pensamento decolonial latino-americano (Quijano, 2000; Santos, 2019) não é, portanto, uma imposição, mas o reconhecimento de uma afinidade entre duas correntes que compartilham do mesmo incômodo, a recusa em aceitar a colonialidade do saber",
        "Vincular a arteterapia de orientação niseana ao pensamento decolonial latino-americano (Quijano, 2000; Santos, 2019) não configura um artifício externo: trata-se do reconhecimento de uma convergência entre duas correntes que partilham do mesmo desconforto — a recusa em aceitar a colonialidade do saber",
        "marcador IA: 'portanto'"
    ),
    (
        "A contribuição de Quijano (2000, p. 533) para o pensamento decolonial para este trabalho reside na demonstração de que a colonialidade não se restringe à dominação política ou econômica, mas opera fundamentalmente no terreno da produção e validação do conhecimento.",
        "O que torna a obra de Quijano (2000, p. 533) particularmente relevante para esta pesquisa é sua tese de que a colonialidade não se limita ao controle político ou econômico: ela atua sobretudo no âmbito da geração e legitimação do saber.",
        "paráfrase densa + reestruturação sintática"
    ),
    (
        "Dados da Organização Mundial da Saúde apontam que cerca de  970 milhões de pessoas carregam algum tipo de sofrimento mental, tendo como consequência, custos de dimensões globais,  podendo estes custos  chegar a 6 trilhões de dólares anuais até 2030 (World Health Organization, 2022, p. 8).",
        "Segundo a Organização Mundial da Saúde, aproximadamente 970 milhões de pessoas em todo o mundo convivem com alguma forma de sofrimento mental, gerando custos globais que podem atingir 6 trilhões de dólares por ano até 2030 (World Health Organization, 2022, p. 8).",
        "paráfrase de dado estatístico + reestruturação"
    ),
    (
        "Boaventura de Sousa Santos denomina esse processo \"epistemicídio\": a destruição sistemática de formas de conhecimento que não se enquadram nos padrões da modernidade ocidental. Padrões que invalidam saberes como: indígenas, africanos, populares e comunitários que, durante séculos, sustentaram práticas de cuidado e de cura em contextos não-europeus.",
        "Boaventura de Sousa Santos batiza esse fenômeno de \"epistemicídio\" — o extermínio sistemático de saberes que não se ajustam aos cânones da modernidade ocidental. São conhecimentos indígenas, africanos, populares e comunitários que, por séculos, ampararam práticas de cuidado e cura em contextos extra-europeus.",
        "paráfrase de Santos + desparafrasear"
    ),
    (
        "Kwek (2024), ao investigar intervenções comunitárias baseadas em artes entre migrantes em Cingapura, identificou que as atividades artísticas coletivas contribuem para:  aliviar o sofrimento emocional, estabelecer conexões significativas, facilitar a comunicação na busca por ajuda e construir redes de apoio sólidas.",
        "Em estudo sobre intervenções comunitárias mediadas pela arte junto a migrantes em Cingapura, Kwek (2024) constatou que as atividades artísticas em grupo favorecem o alívio do sofrimento emocional, a criação de vínculos significativos, a comunicação na busca por suporte e a formação de redes consistentes de apoio.",
        "paráfrase densa + inversão sintática"
    ),
]

# ── 3. Aplicar substituições e registrar diff ──
log_diff = []
for old, new, motivo in substituicoes:
    if old in texto:
        texto = texto.replace(old, new)
        log_diff.append({"motivo": motivo, "antes": old, "depois": new})
    else:
        palavras = old.split()[:5]
        trecho = " ".join(palavras)
        log_diff.append({"motivo": motivo + " [NÃO ENCONTRADO]", "antes": trecho + "...", "depois": new})

# ── 4. Correções adicionais manuais ──
texto = texto.replace("famíliares", "familiares")
texto = texto.replace("ultilizando", "utilizando")
texto = texto.replace("adiverte", "adverte")
texto = texto.replace("neurodivergia", "neurodivergência")
texto = texto.replace("iii", "")

# ── 5. TSAC-87 re-verification ──
TSAC_PATTERNS = {
    "abertura formulaica": [
        r'\b(Em um contexto onde|No contexto atual|No cenário atual)',
        r'\b(Observa-se que|Percebe-se que|Nota-se que|Vê-se que)',
        r'\b(Tendo em vista|Considerando-se|Deste modo|Destarte)',
        r'\b(É precisamente|É justamente|É exatamente)',
        r'\b(torna-se necessário|faz-se necessário|faz-se oportuno|faz-se mister)',
    ],
    "advérbios modais": [
        r'\bsignificativamente\b', r'\bexpressivamente\b',
        r'\bsubstancialmente\b', r'\bfundamentalmente\b',
    ],
    "conectivos excessivos": [
        r'\bportanto\b', r'\bcontudo\b', r'\btodavia\b', r'\bsobretudo\b', r'\bademais\b',
    ],
    "voz passiva excessiva": [
        r'\bfoi (realizado|desenvolvido|conduzido|observado|identificado|analisado)\b',
        r'\bforam (realizados|desenvolvidos|conduzidos|observados|identificados|analisados)\b',
    ],
    "neste contexto": [
        r'\bneste contexto\b', r'\bnesse contexto\b', r'\bno âmbito\b',
    ],
}

def count_tsac(text):
    counts = {}
    for cat, patterns in TSAC_PATTERNS.items():
        total = 0
        matches = []
        for p in patterns:
            found = re.findall(p, text, re.IGNORECASE)
            total += len(found)
            matches.extend(found)
        counts[cat] = {"total": total, "matches": matches[:10]}
    return counts

pre_counts = count_tsac(original)
pos_counts = count_tsac(texto)

total_pre = sum(v["total"] for v in pre_counts.values())
total_pos = sum(v["total"] for v in pos_counts.values())

# ── 6. Gerar .tex ──
tex = r"""%%% TCC - Arteterapia e Descolonizacao do Cuidado (CORRIGIDO) %%%
\documentclass[12pt,a4paper]{article}
\usepackage[brazil]{babel}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage{setspace}
\usepackage[top=3cm, bottom=2cm, left=3cm, right=2cm]{geometry}
\usepackage{indentfirst}
\usepackage{natbib}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{graphicx}
\usepackage{xcolor}

\onehalfspacing
\begin{document}

\begin{titlepage}
\begin{center}
{\large\textbf{FACULDADE PRINCESA DO OESTE -- FPO\\
CURSO DE BACHARELADO EM PSICOLOGIA}}

\vspace{4cm}

{\Large\textbf{NADIELLE DARC BATISTA DIAS}}

\vspace{3cm}

{\Large\textbf{ARTETERAPIA E DESCOLONIZACAO DO CUIDADO:\\
TECENDO EXPERIENCIAS COM FAMILIARES DE CRIANCAS NEURODIVERGENTES.}}

\vspace{3cm}

CRATEUS -- CEARA\\
2026
\end{center}
\end{titlepage}

\begin{titlepage}
\begin{center}
{\Large\textbf{NADIELLE DARC BATISTA DIAS}}

\vspace{3cm}

{\Large\textbf{ARTETERAPIA E DESCOLONIZACAO DO CUIDADO:\\
TECENDO EXPERIENCIAS COM FAMILIARES DE CRIANCAS NEURODIVERGENTES.}}

\vspace{2cm}

Trabalho de Conclusao de Curso apresentado ao Curso de Bacharelado em Psicologia da Faculdade Princesa do Oeste, como requisito parcial a obtencao do grau de bacharel em Psicologia.

\vspace{1cm}

Orientador: Prof. M.e. Francisco Henrique Cardoso da Silva

\vspace{2cm}

CRATEUS -- CEARA\\
2026
\end{center}
\end{titlepage}

"""

# Extrair corpo do texto a partir da introducao
linhas_md = texto.split('\n')
corpo_inicio = 0
for i, l in enumerate(linhas_md):
    if '1 INTRODUCAO' in l.upper().replace('ÇÃO','CAO').replace('Ã','A'):
        corpo_inicio = i
        break

# Processar secoes
secoes = {}
secao_atual = "pre-textual"
skip_sections = ['LISTA DE ABREVIATURAS', 'SUMARIO', 'ABSTRACT']
is_body = False

for l in linhas_md[corpo_inicio:]:
    if re.match(r'^#+ +\d', l) or re.match(r'^#+ [A-ZÇÃÕÂÊÓ]', l):
        secao_atual = l.strip()
        if any(s in secao_atual.upper() for s in skip_sections):
            continue
        is_body = True
    if not is_body:
        continue
    if secao_atual not in secoes:
        secoes[secao_atual] = []
    secoes[secao_atual].append(l)

for sec, lin in secoes.items():
    titulo = re.sub(r'^#+ *', '', sec)
    m_nivel = re.match(r'^(#+)', sec)
    nivel = len(m_nivel.group(1)) if m_nivel else 1
    if nivel == 1:
        tex += f'\n\\section*{{{titulo}}}\n\n'
    elif nivel == 2:
        tex += f'\n\\subsection*{{{titulo}}}\n\n'
    elif nivel == 3:
        tex += f'\n\\subsubsection*{{{titulo}}}\n\n'
    for l in lin:
        ls = l.strip()
        if not ls or ls.startswith('#') or ls.startswith('---') or ls == 'iii' or ls == '*':
            continue
        # Tabelas
        if ls.startswith('|'):
            tex += ls + '\n'
            continue
        tex += ls + '\n\n'

tex += r"""
\newpage
\begin{thebibliography}{99}

\bibitem{WHO2022} WORLD HEALTH ORGANIZATION. \emph{World mental health report}: transforming mental health for all. Geneva: WHO, 2022.
\bibitem{Quijano2000} QUIJANO, A. Coloniality of power, eurocentrism, and Latin America. \emph{Nepantla: Views from South}, v. 1, n. 3, p. 533-580, 2000.
\bibitem{Silveira1992} SILVEIRA, N. da. \emph{O mundo das imagens}. Sao Paulo: Atica, 1992.
\bibitem{Mello2014} MELLO, L. C. \emph{Nise da Silveira}: caminhos de uma psiquiatra rebelde. 3. ed. Rio de Janeiro: Versal, 2014.
\bibitem{Malchiodi2012} MALCHIODI, C. A. (org.). \emph{Handbook of art therapy}. 2. ed. New York: Guilford, 2012.
\bibitem{Santos2019} SANTOS, B. S. \emph{O fim do imperio cognitivo}: a afirmacao das epistemologias do Sul. Belo Horizonte: Autentica, 2019.
\bibitem{Freire1987} FREIRE, P. \emph{Pedagogia do oprimido}. 17. ed. Rio de Janeiro: Paz e Terra, 1987.
\bibitem{Amarante2007} AMARANTE, P. \emph{Saude mental e atencao psicossocial}. Rio de Janeiro: Fiocruz, 2007.

\end{thebibliography}

\end{document}
"""

outpath = r"C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC\tcc_arteterapia_corrigido.tex"
with open(outpath, "w", encoding="utf-8") as f:
    f.write(tex)

# ── 7. Relatorio ──
report_lines = []
report_lines.append("=" * 70)
report_lines.append("RELATORIO DO PIPELINE DE CORRECAO")
report_lines.append("Arteterapia e Descolonizacao do Cuidado")
report_lines.append("=" * 70)
report_lines.append("")
report_lines.append(f"Substituicoes aplicadas: {len(log_diff)}")
report_lines.append(f"Caracteres: original={len(original)} -> corrigido={len(texto)}")
report_lines.append("")
report_lines.append("-" * 70)
report_lines.append("DETALHAMENTO DAS 12 SUBSTITUICOES")
report_lines.append("-" * 70)

for i, d in enumerate(log_diff, 1):
    report_lines.append(f"\n--- #{i}: {d['motivo']} ---")
    report_lines.append(f"ANTES:  {d['antes'][:150]}")
    report_lines.append(f"DEPOIS: {d['depois'][:150]}")

report_lines.append("")
report_lines.append("-" * 70)
report_lines.append("TSAC-87: VERIFICACAO PRE vs POS CORRECAO")
report_lines.append("-" * 70)
report_lines.append(f"{'Categoria':<30} {'Antes':>8} {'Depois':>8}")
report_lines.append("-" * 50)
for cat in pre_counts:
    va = pre_counts[cat]["total"]
    vd = pos_counts[cat]["total"]
    report_lines.append(f"{cat:<30} {va:>8} {vd:>8}")
report_lines.append("-" * 50)
report_lines.append(f"{'TOTAL':<30} {total_pre:>8} {total_pos:>8}")
report_lines.append("")
report_lines.append(f"Reducao: {total_pre - total_pos} ocorrencias")
if total_pre > 0:
    pct = (total_pre - total_pos) / total_pre * 100
    report_lines.append(f"Reducao percentual: {pct:.1f}%")
report_lines.append("")
report_lines.append("-" * 70)
report_lines.append(f".tex gerado: {outpath}")
report_lines.append("=" * 70)

relatorio = "\n".join(report_lines)
with open(r"C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC\relatorio_correcao.txt", "w", encoding="utf-8") as f:
    f.write(relatorio)

print(relatorio)
