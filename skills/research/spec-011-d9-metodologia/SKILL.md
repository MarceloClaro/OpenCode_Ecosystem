---
name: spec-011-d9-metodologia
description: "Suite TDD para D9 (Desenho Experimental e Metodologia) do CORA-Eval. 8 CTs: ANOVA, Teste t, Randomizacao, Cohen's d, Poder estatistico, Shapiro-Wilk, Propagacao de erros, Delineamento fatorial 2^3. Use quando precisar validar metodologia experimental."
spec: "SPEC-011"
version: "1.0"
category: research
tags: [cora-eval, d9, metodologia, tdd, validacao, estatistica]
dependencies: [SPEC-001, CORA-Eval]
tdd_suite: "artigo/evaluations/tests/test_d9_metodologia.py"
ct_count: 8
status: active
---

# SPEC-011 — Suite D9: Desenho Experimental e Metodologia

## Objetivo
Validar a capacidade de desenho experimental e metodologia científica
(D9 do CORA-Eval) via 8 critérios de teste automatizados com pytest.

## CTs

| CT | Descrição | Tipo |
|:--:|-----------|:----:|
| D9-1 | ANOVA one-way — F significativo quando grupos têm médias diferentes | Estatística |
| D9-2 | Teste t — rejeita H0 quando diferença > 2 desvios padrão | Estatística |
| D9-3 | Randomização — grupos não diferem antes do tratamento (p > 0.05) | Método |
| D9-4 | Tamanho de efeito — Cohen's d > 0.8 para diferença grande | Método |
| D9-5 | Poder estatístico — 1-β > 0.8 para n=30, d=0.5 | Método |
| D9-6 | Normalidade — Shapiro-Wilk detecta não-normalidade em dados exponenciais | Diagnóstico |
| D9-7 | Propagação de erros — Δz = √((∂z/∂x)²Δx² + (∂z/∂y)²Δy²) | Metrologia |
| D9-8 | Delineamento fatorial 2³ — efeitos principais e interação calculados | Delineamento |

## Execução
```bash
cd artigo/evaluations/tests
python -m pytest test_d9_metodologia.py -v
```
