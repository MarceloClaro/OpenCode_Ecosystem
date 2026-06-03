---
name: spec-013-d4-quimica
description: "Suite TDD para D4 (Raciocinio Quimico) do CORA-Eval. 3 CTs em nivel N1: Balanceamento, Massa Molar, Concentracao. Validacao via TDD com massas atomicas IUPAC 2021. Use quando precisar validar raciocinio quimico fundamental do ecossistema OpenCode."
spec: "SPEC-013"
version: "1.0"
category: research
tags: [cora-eval, d4, quimica, tdd, validacao]
dependencies: [SPEC-001, CORA-Eval]
tdd_suite: "artigo/evaluations/tests/test_d4_quimica.py"
ct_count: 3
status: active
---

# SPEC-013 — Suite D4: Raciocínio Químico

## Objetivo
Validar a capacidade de raciocínio químico fundamental (D4 do CORA-Eval)
via 3 critérios de teste N1 (Básico) com massas atômicas IUPAC 2021.

## CTs

| CT | Descrição | Nível |
|:--:|-----------|:-----:|
| D4-N1-01 | Balanceamento — verifica conservação de massa em reações de combustão (C₃H₈+O₂→CO₂+H₂O) | N1 |
| D4-N1-02 | Massa Molar — cálculo de massa molar para H₂SO₄, C₆H₁₂O₆, CaCO₃ | N1 |
| D4-N1-03 | Concentração — conversão entre %m/m, molaridade e vice-versa para soluções | N1 |

## Funções Implementadas
`parse_formula`, `molar_mass`, `balance_combustion`, `percent_to_molarity`, `molarity_to_percent`

## Execução
```bash
python artigo/evaluations/tests/test_d4_quimica.py
```

## Integração CORA-Eval
D4 cobre os fundamentos da química estequiométrica em nível N1 (Básico),
utilizando massas atômicas oficiais IUPAC 2021 para garantir precisão
nos cálculos de massa molar e concentração.
