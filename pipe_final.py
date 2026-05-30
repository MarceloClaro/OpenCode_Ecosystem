#!/usr/bin/env python3
"""Pipeline final: reescrita + .tex + TSAC verificacao"""

import re, json

with open(r"C:\Users\marce\Downloads\Cópia de TRABALHO DE CONCLUSÃO DE CURSO.docx (2).md", "r", encoding="utf-8") as f:
    texto = f.read()

original = texto

# --- 11 substituicoes robustas ---
pairs = [
    ("O bem estar psicol\u00f3gico configura-se atualmente como um dos campos mais urgentes no \u00e2mbito  das pol\u00edticas p\u00fablicas, necessitando de um olhar integral que v\u00e1 al\u00e9m da atua\u00e7\u00e3o m\u00e9dica visando os \u00e2mbitos social e cultural do sofrimento humano.",
     "O campo do bem-estar psicol\u00f3gico figura entre as prioridades contempor\u00e2neas das pol\u00edticas p\u00fablicas, exigindo uma abordagem integral que ultrapasse a dimens\u00e3o meramente m\u00e9dica e alcance os planos social e cultural do sofrimento humano."),

    ("Em um contexto onde as respostas terap\u00eauticas convencionais tornam-se insuficientes a arteterapia surge como \u00e1rea de conhecimento e abordagem que caminha entre diversos campos com arte, psicologia e ci\u00eancias sociais",
     "Quando as respostas terap\u00eauticas tradicionais mostram seus limites, a arteterapia emerge como campo de conhecimento que transita entre a arte, a psicologia e as ci\u00eancias sociais"),

    ("\u00c9 precisamente focando nessa dist\u00e2ncia que este estudo mobiliza a perspectiva decolonial.",
     "\u00c9 justamente a partir dessa lacuna que esta pesquisa recorre \u00e0 perspectiva decolonial."),

    ("Tendo delimitado o problema central e os objetivos deste estudo, torna-se necess\u00e1rio mapear o estado atual do conhecimento sobre os campos te\u00f3ricos que fundamentam esta investiga\u00e7\u00e3o. A presente revis\u00e3o n\u00e3o se configura como um invent\u00e1rio exaustivo da literatura",
     "Uma vez circunscritos o problema e os objetivos, faz-se oportuno examinar o estado da arte dos campos te\u00f3ricos que alicer\u00e7am esta investiga\u00e7\u00e3o. A presente revis\u00e3o n\u00e3o se pretende um invent\u00e1rio exaustivo da literatura"),

    ("A literatura documenta que esses familiares, predominantemente m\u00e3es, apresentam n\u00edveis de estresse expressivamente mais elevados do que cuidadores de crian\u00e7as neurot\u00edpicas, com manifesta\u00e7\u00f5es de ansiedade, depress\u00e3o e exaust\u00e3o emocional (Alves; Gameiro; Bazi, 2022; Zanatta et al., 2014, p. 275).",
     "Estudos indicam que esses familiares \u2014 em sua maioria m\u00e3es \u2014 exibem n\u00edveis de estresse significativamente superiores aos de cuidadores de crian\u00e7as neurot\u00edpicas, com quadros de ansiedade, depress\u00e3o e exaust\u00e3o emocional (Alves; Gameiro; Bazi, 2022; Zanatta et al., 2014, p. 275)."),

    ("mundo interior rico e complexo (Silveira, 1992, p. 21).",
     "universo interior repleto de significados (Silveira, 1992, p. 21)."),

    ("n\u00e3o \u00e9, portanto, uma imposi\u00e7\u00e3o, mas o reconhecimento de uma afinidade entre duas correntes que compartilham do mesmo inc\u00f4modo, a recusa em aceitar a colonialidade do saber",
     "n\u00e3o configura um artif\u00edcio externo: trata-se do reconhecimento de uma converg\u00eancia entre duas correntes que partilham do mesmo desconforto \u2014 a recusa em aceitar a colonialidade do saber"),

    ("n\u00e3o se restringe \u00e0 domina\u00e7\u00e3o pol\u00edtica ou econ\u00f4mica, mas opera fundamentalmente no terreno da produ\u00e7\u00e3o e valida\u00e7\u00e3o do conhecimento.",
     "n\u00e3o se limita ao controle pol\u00edtico ou econ\u00f4mico: ela atua sobretudo no \u00e2mbito da gera\u00e7\u00e3o e legitima\u00e7\u00e3o do saber."),

    ("Dados da Organiza\u00e7\u00e3o Mundial da Sa\u00fade apontam que cerca de  970 milh\u00f5es de pessoas carregam algum tipo de sofrimento mental, tendo como consequ\u00eancia, custos de dimens\u00f5es globais,  podendo estes custos  chegar a 6 trilh\u00f5es de d\u00f3lares anuais at\u00e9 2030 (World Health Organization, 2022, p. 8).",
     "Segundo a Organiza\u00e7\u00e3o Mundial da Sa\u00fade, aproximadamente 970 milh\u00f5es de pessoas em todo o mundo convivem com alguma forma de sofrimento mental, gerando custos globais que podem atingir 6 trilh\u00f5es de d\u00f3lares por ano at\u00e9 2030 (World Health Organization, 2022, p. 8)."),

    ('Boaventura de Sousa Santos denomina esse processo "epistemic\u00eddio": a destrui\u00e7\u00e3o sistem\u00e1tica de formas de conhecimento que n\u00e3o se enquadram nos padr\u00f5es da modernidade ocidental. Padr\u00f5es que invalidam saberes como: ind\u00edgenas, africanos, populares e comunit\u00e1rios que, durante s\u00e9culos, sustentaram pr\u00e1ticas de cuidado e de cura em contextos n\u00e3o-europeus.',
     'Boaventura de Sousa Santos batiza esse fen\u00f4meno de "epistemic\u00eddio" \u2014 o exterm\u00ednio sistem\u00e1tico de saberes que n\u00e3o se ajustam aos c\u00e2nones da modernidade ocidental. S\u00e3o conhecimentos ind\u00edgenas, africanos, populares e comunit\u00e1rios que, por s\u00e9culos, ampararam pr\u00e1ticas de cuidado e cura em contextos extra-europeus.'),

    ("Kwek (2024), ao investigar interven\u00e7\u00f5es comunit\u00e1rias baseadas em artes entre migrantes em Cingapura, identificou que as atividades art\u00edsticas coletivas contribuem para:  aliviar o sofrimento emocional, estabelecer conex\u00f5es significativas, facilitar a comunica\u00e7\u00e3o na busca por ajuda e construir redes de apoio s\u00f3lidas.",
     "Em estudo sobre interven\u00e7\u00f5es comunit\u00e1rias mediadas pela arte junto a migrantes em Cingapura, Kwek (2024) constatou que as atividades art\u00edsticas em grupo favorecem o al\u00edvio do sofrimento emocional, a cria\u00e7\u00e3o de v\u00ednculos significativos, a comunica\u00e7\u00e3o na busca por suporte e a forma\u00e7\u00e3o de redes consistentes de apoio."),
]

sub_ok = 0
sub_fail = 0
for old, new in pairs:
    if old in texto:
        texto = texto.replace(old, new)
        sub_ok += 1
    else:
        sub_fail += 1
        # Mostrar tentativa
        idx = texto.find(old[:20])
        if idx >= 0:
            print(f"FAIL: fragmento encontrado mas nao corresponde exatamente")
            print(f"  Esperado: {repr(old[:80])}")
            print(f"  Encontrado: {repr(texto[idx:idx+80])}")
        else:
            print(f"FAIL: fragmento nao encontrado: {old[:50]}")

# Correcoes adicionais
for old, new in {"fam\u00edliares": "familiares", "ultilizando": "utilizando",
                 "adiverte": "adverte", "neurodivergia": "neurodiverg\u00eancia"}.items():
    texto = texto.replace(old, new)

print(f"\nSubstituicoes: {sub_ok}/{sub_ok+sub_fail} OK")

# --- TSAC-87 re-verificacao ---
tsac = {
    "abertura formulaica": [r'(Em um contexto onde|Observa-se que|torna-se necess[áa]rio|faz-se necess[áa]rio|É precisamente|É justamente|No contexto atual)'],
    "advérbios modais": [r'\b(significativamente|expressivamente|substancialmente|fundamentalmente)\b'],
    "conectivos excessivos": [r'\b(portanto|contudo|todavia|sobretudo|ademais)\b'],
    "neste contexto": [r'\b(neste contexto|nesse contexto|no [âa]mbito)\b'],
}

print("\nTSAC-87: PRE vs POS")
print(f"{'Categoria':<25} {'Antes':>8} {'Depois':>8}")
pre_t, pos_t = 0, 0
for cat, pats in tsac.items():
    pc = sum(len(re.findall(p, original, re.I)) for p in pats)
    pt = sum(len(re.findall(p, texto, re.I)) for p in pats)
    pre_t += pc; pos_t += pt
    print(f"{cat:<25} {pc:>8} {pt:>8}")
print(f"{'TOTAL':<25} {pre_t:>8} {pos_t:>8}")
print(f"Reducao: {pre_t-pos_t} ({100*(pre_t-pos_t)//max(pre_t,1)}%)")

# --- Gerar .tex ---
linhas = texto.split('\n')
corpo = []
capturar = False
for l in linhas:
    if '1 INTRODU' in l.upper():
        capturar = True
    if capturar:
        corpo.append(l)

body = '\n'.join(corpo)

# Limpeza basica para .tex
body = body.replace('\\', '')  # remove backslashes soltos
body = re.sub(r'[ \t]+', ' ', body)  # normaliza espacos
body = re.sub(r'\n{3,}', '\n\n', body)
body = re.sub(r'\biii\b', '', body)

# Converter marcadores de secao para comandos LaTeX
def secao_level(texto):
    """Determina nivel de secao pelo numero: 1, 2.1, 4.4.3 etc."""
    m = re.match(r'^([\d]+)', texto)
    return 1 if m else 2

linhas_tex = []
for l in body.split('\n'):
    s = l.strip()
    # Pattern 1: # **SECTION** or ## **SECTION**
    m1 = re.match(r'^#+\s*\*\*(.+?)\*\*\s*$', s)
    # Pattern 2: **SECTION** (plain bold header)
    m2 = re.match(r'^\*\*(.+?)\*\*\s*$', s)
    
    m = m1 or m2
    if m:
        texto = m.group(1).strip()
        hash_match = re.match(r'^#*', s)
        hashes = len(hash_match.group()) if (s.startswith('#') and hash_match) else 0
        has_bold = s.startswith('**') or s.startswith('#')
        
        if hashes >= 2:
            level = 3
        elif hashes == 1:
            level = 1
        elif has_bold:
            # Inferir de "1 TITULO" vs "2.1 Subtitulo" vs "4.4.3 Subsub"
            dots = texto.count('.')
            level = {0: 1, 1: 2, 2: 3}.get(dots, 3)
        else:
            level = 2
        
        # Extrair titulo sem numero
        num_tit = re.match(r'^[\d.]+\s+(.+)$', texto)
        titulo = num_tit.group(1) if num_tit else texto
        
        cmd = {1: r'\section', 2: r'\subsection', 3: r'\subsubsection'}.get(level, r'\section')
        linhas_tex.append(f'{cmd}{{{titulo}}}')
        continue
    
    # Escapar & (mas nao em URLs)
    l = l.replace('&', r'\&')
    linhas_tex.append(l)
body = '\n'.join(linhas_tex)

tex = r"""\documentclass[12pt,a4paper]{article}
\usepackage[brazil]{babel}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{times}
\usepackage{setspace}
\usepackage[top=3cm,bottom=2cm,left=3cm,right=2cm]{geometry}
\usepackage{indentfirst}
\usepackage{natbib}
\usepackage{hyperref}
\usepackage{booktabs}
\usepackage{longtable}
\onehalfspacing

\begin{document}

\title{ARTETERAPIA E DESCOLONIZACAO DO CUIDADO:\\
TECENDO EXPERIENCIAS COM FAMILIARES DE CRIANCAS NEURODIVERGENTES}
\author{Nadielle Darc Batista Dias}
\date{2026}

\maketitle
\newpage

"""
tex += body

tex += r"""
\newpage
\begin{thebibliography}{99}

\bibitem{who2022} WORLD HEALTH ORGANIZATION. \emph{World mental health report}: transforming mental health for all. Geneva: WHO, 2022.

\end{thebibliography}

\end{document}
"""

out = r"C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC\tcc_arteterapia_corrigido.tex"
with open(out, "w", encoding="utf-8") as f:
    f.write(tex)

print(f"\n.tex salvo: {out}")
print(f"Tamanho: {len(tex)} chars")
