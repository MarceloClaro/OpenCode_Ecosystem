---
name: spec-010-d2-fisica
description: "Suite TDD para D2 (Modelagem de Sistemas Fisicos) do CORA-Eval. 8 CTs: MRU, Queda Livre, Conservacao de Energia, Analise Dimensional, Hooke, Pendulo, Conservacao de Momento, Gases. Use quando precisar validar modelagem de sistemas fisicos."
spec: "SPEC-010"
version: "1.0"
category: research
tags: [cora-eval, d2, fisica, tdd, validacao]
dependencies: [SPEC-001, CORA-Eval]
tdd_suite: "artigo/evaluations/tests/test_d2_fisica.py"
ct_count: 8
status: active
---

# SPEC-010 — Suite D2: Modelagem de Sistemas Físicos

## Objetivo
Validar a capacidade de modelagem de sistemas físicos (D2 do CORA-Eval)
via 8 critérios de teste automatizados com pytest.

## CTs

| CT | Descrição | Tipo |
|:--:|-----------|:----:|
| D2-1 | MRU — x = x₀ + v·t, verificar com 100 valores aleatórios de t | Cinemática |
| D2-2 | Queda livre — y = (1/2)g·t², erro < 1% vs integração numérica | Dinâmica |
| D2-3 | Conservação de energia — E_ini = E_fin para pêndulo simples | Conservação |
| D2-4 | Análise dimensional — verificar que [F]=MLT⁻² em F=ma | V1 Dimensional |
| D2-5 | Lei de Hooke — F = -k·x, linearidade R² > 0.999 | Elasticidade |
| D2-6 | Período pêndulo — T = 2π√(L/g), 5 valores de L verificados | Oscilações |
| D2-7 | Conservação momento — m1v1+m2v2 = constante em colisão elástica | Conservação |
| D2-8 | Lei dos gases — PV = nRT, 10 pontos PV vs T com R² > 0.99 | Termodinâmica |

## Execução
```bash
cd artigo/evaluations/tests
python -m pytest test_d2_fisica.py -v
```
