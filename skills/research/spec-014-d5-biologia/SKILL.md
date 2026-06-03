---
name: spec-014-d5-biologia
description: "Suite TDD para D5 (Raciocinio Biologico) do CORA-Eval. 3 CTs em nivel N1: Transcricao, Traducao, GC Content. Validacao via TDD com codigo genetico padrao. Use quando precisar validar raciocinio biologico molecular do ecossistema OpenCode."
spec: "SPEC-014"
version: "1.0"
category: research
tags: [cora-eval, d5, biologia, tdd, validacao]
dependencies: [SPEC-001, CORA-Eval]
tdd_suite: "artigo/evaluations/tests/test_d5_biologia.py"
ct_count: 3
status: active
---

# SPEC-014 — Suite D5: Raciocínio Biológico

## Objetivo
Validar a capacidade de raciocínio biológico molecular (D5 do CORA-Eval)
via 3 critérios de teste N1 (Básico) com código genético padrão.

## CTs

| CT | Descrição | Nível |
|:--:|-----------|:-----:|
| D5-N1-01 | Transcrição — DNA→RNA (T→U) para sequências de 10+ nucleotídeos | N1 |
| D5-N1-02 | Tradução — RNA→proteína (códon→aminoácido) incluindo códon de parada | N1 |
| D5-N1-03 | GC Content — fração GC para múltiplas sequências, inclusive sem GC | N1 |

## Funções Implementadas
`transcribe`, `translate_codon`, `translate`, `gc_content`

## Execução
```bash
python artigo/evaluations/tests/test_d5_biologia.py
```

## Integração CORA-Eval
D5 cobre o dogma central da biologia molecular (transcrição e tradução)
em nível N1, validando a correta manipulação de sequências genéticas
segundo o código genético padrão universal.
