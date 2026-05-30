---
name: spec-009-d1-matematica
description: "Suite TDD para D1 (Raciocinio Matematico Formal) do CORA-Eval. 8 CTs: Pitagoras, Gauss, Fatorial, Fibonacci, Primos, MDC, Trigonometria, Derivada. Validacao via TDD com pytest. Use quando precisar validar raciocinio matematico formal do ecossistema OpenCode no dominio da matematica pura."
spec: "SPEC-009"
version: "1.0"
category: research
tags: [cora-eval, d1, matematica, tdd, validacao]
dependencies: [SPEC-001, CORA-Eval]
tdd_suite: "artigo/evaluations/tests/test_d1_matematica.py"
ct_count: 8
status: active
---

# SPEC-009 — Suite D1: Raciocínio Matemático Formal

## Objetivo
Validar a capacidade de raciocínio matemático formal (D1 do CORA-Eval)
via 8 critérios de teste automatizados com pytest.

## CTs

| CT | Descrição | Tipo |
|:--:|-----------|:----:|
| D1-1 | Teorema de Pitágoras — prova algébrica verifica identidade a²+b²=c² | Álgebra |
| D1-2 | Soma de Gauss — n(n+1)/2 verificado para n=1..1000 | Séries |
| D1-3 | Fatorial — definição recursiva confere com math.factorial até 20 | Recursão |
| D1-4 | Fibonacci — fórmula fechada de Binet confere com iteração até n=30 | Sequências |
| D1-5 | Números primos — crivo de Eratóstenes bate com lista conhecida até 100 | Teoria dos Números |
| D1-6 | MDC — algoritmo de Euclides confere com math.gcd para 1000 pares | Teoria dos Números |
| D1-7 | Identidade trigonométrica — sin²θ+cos²θ=1 para 1000 ângulos aleatórios | Trigonometria |
| D1-8 | Derivada — (x^n)' = n·x^(n-1) via definição de limite com h=1e-7 | Cálculo |

## Execução
```bash
cd artigo/evaluations/tests
python -m pytest test_d1_matematica.py -v
```

## Integração CORA-Eval
D1 é a única dimensão em N4 (Pesquisa) sem teste automatizado próprio
antes desta spec. A suite supre essa lacuna.
