---
name: spec-016-d7-codigo
description: "Suite TDD para D7 (Verificacao de Codigo) do CORA-Eval. 5 CTs em nivel N3: Syntax, Logic, Types, Complexity, Security, Coverage. Validacao via TDD com pytest sobre codigo real de suites anteriores. Use quando precisar validar verificacao de codigo fonte do ecossistema OpenCode."
spec: "SPEC-016"
version: "1.0"
category: research
tags: [cora-eval, d7, codigo, tdd, validacao]
dependencies: [SPEC-001, CORA-Eval]
tdd_suite: "artigo/evaluations/tests/test_d7_codigo.py"
ct_count: 5
status: active
---

# SPEC-016 — Suite D7: Verificação de Código

## Objetivo
Validar a capacidade de verificação e análise de código fonte (D7 do CORA-Eval)
via 5 critérios de teste N3 (Pesquisa) executados com pytest, aplicando
6 verificadores (V7a-V7f) sobre código real das suites CORA-Eval.

## CTs

| CT | Verificador | Descrição | Nível |
|:--:|:-----------:|-----------|:-----:|
| D7-N3-01 | V7a — Syntax | AST parsing validation — verifica se o código é sintaticamente válido | N3 |
| D7-N3-02 | V7b — Logic | Idempotency check — execução dupla deve produzir mesmo resultado | N3 |
| D7-N3-03 | V7c — Types | Type annotation coverage — funções públicas devem ter type hints | N3 |
| D7-N3-04 | V7d — Complexity | O(n²) detection — identifica loops aninhados proibidos | N3 |
| D7-N3-05 | V7e+V7f — Security + Coverage | Security (eval/exec/subprocess) + Code coverage mínima de 70% | N3 |

## Verificadores Cora V7
V7a (Syntax): `compile()` + AST para validar gramática Python
V7b (Logic): idempotência — `f(f(x)) == f(x)` para funções determinísticas
V7c (Types): `typing.get_type_hints()` — coverage mínima de type annotations
V7d (Complexity): `ast.walk()` — detecção de complexidade O(n²) por loops aninhados
V7e (Security): proibição de `eval()`, `exec()`, `subprocess`, `os.system` em produção
V7f (Coverage): `coverage.py` — cobertura mínima de 70% em linhas de código

## Execução
```bash
python -m pytest artigo/evaluations/tests/test_d7_codigo.py -v
```

## Integração CORA-Eval
D7 é a dimensão de metacognição do CORA-Eval: valida a capacidade do
ecossistema de verificar seu próprio código fonte. Utiliza código real
das suites D1-D6 como material de análise, garantindo validade ecológica.
