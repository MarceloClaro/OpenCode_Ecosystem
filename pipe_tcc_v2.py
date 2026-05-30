#!/usr/bin/env python3
"""Pipeline v2: robusto para escapes \(\) no MD fonte"""

import re, json

with open(r"C:\Users\marce\Downloads\Cópia de TRABALHO DE CONCLUSÃO DE CURSO.docx (2).md", "r", encoding="utf-8") as f:
    texto = f.read()

original = texto

# ── Substituições robustas (usando fragmentos únicos) ──
pairs = [
    # 1: O bem estar psicológico configura-se atualmente
    ("O bem estar psicol\u00f3gico configura-se atualmente como um dos campos mais urgentes",
     "O campo do bem-estar psicol\u00f3gico figura entre as prioridades contempor\u00e2neas das pol\u00edticas p\u00fablicas"),
    
    # 2: Em um contexto onde as respostas terapêuticas convencionais tornam-se insuficientes
    ("Em um contexto onde as respostas terap\u00eauticas convencionais tornam-se insuficientes",
     "Quando as respostas terap\u00eauticas tradicionais mostram seus limites"),
    
    # 3: É precisamente focando nessa distância
    ("\u00c9 precisamente focando nessa dist\u00e2ncia que este estudo mobiliza a perspectiva decolonial",
     "\u00c9 justamente a partir dessa lacuna que esta pesquisa recorre \u00e0 perspectiva decolonial"),
    
    # 4: torna-se necessário mapear o estado atual
    ("torna-se necess\u00e1rio mapear o estado atual do conhecimento sobre os campos te\u00f3ricos que fundamentam esta investiga\u00e7\u00e3o",
     "faz-se oportuno examinar o estado da arte dos campos te\u00f3ricos que alicer\u00e7am esta investiga\u00e7\u00e3o"),
    
    # 5: A literatura documenta que esses familiares
    ("A literatura documenta que esses familiares, predominantemente m\u00e3es, apresentam n\u00edveis de estresse expressivamente mais elevados",
     "Estudos indicam que esses familiares \u2014 em sua maioria m\u00e3es \u2014 exibem n\u00edveis de estresse significativamente superiores"),
    
    # 6: mundo interior rico e complexo
    ("mundo interior rico e complexo (Silveira, 1992, p. 21)",
     "universo interior repleto de significados (Silveira, 1992, p. 21)"),
    
    # 7: Articular a arteterapia de base niseana ... portanto
    ("n\u00e3o \u00e9, portanto, uma imposi\u00e7\u00e3o, mas o reconhecimento de uma afinidade entre duas correntes que compartilham do mesmo inc\u00f4modo, a recusa em aceitar a colonialidade do saber",
     "n\u00e3o configura um artif\u00edcio externo: trata-se do reconhecimento de uma converg\u00eancia entre duas correntes que partilham do mesmo desconforto \u2014 a recusa em aceitar a colonialidade do saber"),
    
    # 8: A contribuição de Quijano ... reside na demonstração
    ("reside na demonstra\u00e7\u00e3o de que a colonialidade n\u00e3o se restringe \u00e0 domina\u00e7\u00e3o pol\u00edtica ou econ\u00f4mica, mas opera fundamentalmente no terreno da produ\u00e7\u00e3o e valida\u00e7\u00e3o do conhecimento",
     "sua tese de que a colonialidade n\u00e3o se limita ao controle pol\u00edtico ou econ\u00f4mico: ela atua sobretudo no \u00e2mbito da gera\u00e7\u00e3o e legitimação do saber"),
    
    # 9: Dados da Organização Mundial da Saúde apontam
    ("Dados da Organiza\u00e7\u00e3o Mundial da Sa\u00fade apontam que cerca de  970 milh\u00f5es de pessoas carregam algum tipo de sofrimento mental, tendo como consequ\u00eancia, custos de dimens\u00f5es globais,  podendo estes custos  chegar a 6 trilh\u00f5es de d\u00f3lares anuais at\u00e9 2030",
     "Segundo a Organiza\u00e7\u00e3o Mundial da Sa\u00fade, aproximadamente 970 milh\u00f5es de pessoas em todo o mundo convivem com alguma forma de sofrimento mental, gerando custos globais que podem atingir 6 trilh\u00f5es de d\u00f3lares por ano at\u00e9 2030"),
    
    # 10: Boaventura de Sousa Santos denomina esse processo "epistemicídio"
    ("Boaventura de Sousa Santos denomina esse processo \u201cepistemic\u00eddio\u201d: a destrui\u00e7\u00e3o sistem\u00e1tica de formas de conhecimento que n\u00e3o se enquadram nos padr\u00f5es da modernidade ocidental. Padr\u00f5es que invalidam saberes como: ind\u00edgenas, africanos, populares e comunit\u00e1rios que, durante s\u00e9culos, sustentaram pr\u00e1ticas de cuidado e de cura em contextos n\u00e3o-europeus",
     "Boaventura de Sousa Santos batiza esse fen\u00f4meno de \u201cepistemic\u00eddio\u201d \u2014 o exterm\u00ednio sistem\u00e1tico de saberes que n\u00e3o se ajustam aos c\u00e2nones da modernidade ocidental. S\u00e3o conhecimentos ind\u00edgenas, africanos, populares e comunit\u00e1rios que, por s\u00e9culos, ampararam pr\u00e1ticas de cuidado e cura em contextos extra-europeus"),
    
    # 11: Kwek (2024), ao investigar intervenções comunitárias
    ("Kwek (2024), ao investigar interven\u00e7\u00f5es comunit\u00e1rias baseadas em artes entre migrantes em Cingapura, identificou que as atividades art\u00edsticas coletivas contribuem para:  aliviar o sofrimento emocional, estabelecer conex\u00f5es significativas, facilitar a comunica\u00e7\u00e3o na busca por ajuda e construir redes de apoio s\u00f3lidas",
     "Em estudo sobre interven\u00e7\u00f5es comunit\u00e1rias mediadas pela arte junto a migrantes em Cingapura, Kwek (2024) constatou que as atividades art\u00edsticas em grupo favorecem o al\u00edvio do sofrimento emocional, a cria\u00e7\u00e3o de v\u00ednculos significativos, a comunica\u00e7\u00e3o na busca por suporte e a forma\u00e7\u00e3o de redes consistentes de apoio"),
]

log = []
for old, new in pairs:
    if old in texto:
        texto = texto.replace(old, new)
        log.append((old[:100], new[:100], "OK"))
    else:
        log.append((old[:100], new[:100], "FALHOU"))

# ── Correções adicionais ──
fixes = {"famíliares": "familiares", "ultilizando": "utilizando", "adiverte": "adverte", "neurodivergia": "neurodivergência"}
for old, new in fixes.items():
    if old in texto:
        texto = texto.replace(old, new)

# ── TSAC-87 ──
patterns = {
    "abertura formulaica": [r'(Em um contexto onde|No contexto atual|Observa-se que|É precisamente|É justamente|torna-se necessário|faz-se necessário)'],
    "advérbios modais": [r'\b(significativamente|expressivamente|substancialmente|fundamentalmente)\b'],
    "conectivos excessivos": [r'\b(portanto|contudo|todavia|sobretudo|ademais)\b'],
    "neste contexto": [r'\b(neste contexto|nesse contexto|no âmbito)\b'],
}
pre_total = 0
pos_total = 0
for cat, pats in patterns.items():
    pre_c = sum(len(re.findall(p, original, re.I)) for p in pats)
    pos_c = sum(len(re.findall(p, texto, re.I)) for p in pats)
    pre_total += pre_c
    pos_total += pos_c
    print(f"{cat:<25} {pre_c:>3} -> {pos_c:<3}")

print(f"{'TOTAL':<25} {pre_total:>3} -> {pos_total:<3}")
print(f"Redução: {pre_total-pos_total} ({100*(pre_total-pos_total)//max(pre_total,1)}%)")
print(f"Substituições: {sum(1 for x in log if x[2]=='OK')}/{len(pairs)}")
for o, n, status in log:
    flag = "⚠️" if status == "FALHOU" else "✓"
    print(f"  {flag} {status}: {o[:60]}...")

# ── Salvar .tex (versão simplificada mas funcional) ──
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

\section*{RESUMO}
""" + texto.split('\n')[76].strip() + """

\noindent\textbf{Palavras-chave:} Arteterapia decolonial. Neurodivergencia. Parentalidade atipica. Atendimento pedagogico especializado.

"""
# Seções
linhas = texto.split('\n')
corpo = []
capturar = False
for l in linhas:
    if '# 1 INTRODUCAO' in l:
        capturar = True
    if not capturar:
        continue
    corpo.append(l)

tex += '\n'.join(corpo)

tex += r"""
\begin{thebibliography}{99}
\bibitem{WHO2022} WHO. World mental health report. Geneva, 2022.
\bibitem{Quijano2000} QUIJANO, A. Coloniality of power. Nepantla, v.1, n.3, 2000.
\bibitem{Silveira1992} SILVEIRA, N. O mundo das imagens. Sao Paulo: Atica, 1992.
\bibitem{Mello2014} MELLO, L.C. Nise da Silveira. 3.ed. Rio: Versal, 2014.
\bibitem{Santos2019} SANTOS, B.S. O fim do imperio cognitivo. BH: Autentica, 2019.
\end{thebibliography}
\end{document}
"""

out = r"C:\Users\marce\OneDrive\Documentos\Antiprojeto UFC\tcc_arteterapia_corrigido.tex"
with open(out, "w", encoding="utf-8") as f:
    f.write(tex)
print(f"\n.tex salvo: {out}")
