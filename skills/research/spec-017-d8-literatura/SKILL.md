---
name: spec-017-d8-literatura
description: "Suite TDD para D8 (Revisao Sistematica de Literatura) do CORA-Eval. 3 CTs em nivel N1: Claims, Citations, Classification. Validacao via TDD com corpus de 7 artigos cientificos reais. Use quando precisar validar extracao e classificacao de literatura academica do ecossistema OpenCode."
spec: "SPEC-017"
version: "1.0"
category: research
tags: [cora-eval, d8, literatura, tdd, validacao]
dependencies: [SPEC-001, CORA-Eval]
tdd_suite: "artigo/evaluations/tests/test_d8_literatura.py"
ct_count: 3
status: active
---

# SPEC-017 — Suite D8: Revisão Sistemática de Literatura

## Objetivo
Validar a capacidade de revisão sistemática de literatura (D8 do CORA-Eval)
via 3 critérios de teste N1 (Básico) utilizando corpus de 7 artigos
científicos reais.

## CTs

| CT | Descrição | Nível |
|:--:|-----------|:-----:|
| D8-N1-01 | Extração de Claims — identifica a afirmação principal de cada artigo no corpus | N1 |
| D8-N1-02 | Contagem de Citações — extrai e conta referências bibliográficas de cada artigo | N1 |
| D8-N1-03 | Classificação por Área — classifica artigos por área de conhecimento (Exatas/Saúde/Humanas/Engenharias) | N1 |

## Corpus (7 Artigos Reais)
| # | Artigo | Área |
|:-:|--------|:----:|
| 1 | Farinelli et al. — GAT on noncompact symmetric spaces (arXiv:0910.1671) | Exatas |
| 2 | Black & Scholes — The Pricing of Options and Corporate Liabilities (JPE 1973) | Exatas |
| 3 | Nelson — Quantum Derivation of Black-Scholes (Physica A, 2001) | Exatas |
| 4 | Arnold — Geometrical Methods in the Theory of ODEs (Grundlehren 1988) | Exatas |
| 5 | Hénon & Heiles — Applicability of the Third Integral of Motion (AJ 1964) | Exatas |
| 6 | Jarzynski & Crooks — Nonequilibrium Equality for Free Energy Differences (PRL 1997) | Exatas |
| 7 | Moser — On Invariant Curves of Area-Preserving Maps (Crelle's Journal 1962) | Exatas |

## Funções Implementadas
`extract_main_claim`, `count_citations`, `classify_area`

## Execução
```bash
python artigo/evaluations/tests/test_d8_literatura.py
```

## Integração CORA-Eval
D8 cobre a capacidade de análise sistemática de literatura em nível N1.
O corpus é composto por artigos reais de física matemática, finanças
quânticas e sistemas dinâmicos. A função `count_citations` usa expressão
regular para extrair padrões bibliográficos comuns (ACM, IEEE, ABNT).
