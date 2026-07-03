---
name: metodos-mistos
description: "Skill para design e execução de Métodos Mistos: sequencial (QUAN→qual ou qual→QUAN) e convergente paralelo, integrando análises quantitativas e qualitativas com triangulação."
spec: "SPEC-066"
version: "1.0"
category: research
tags: [metodos-mistos, sequencial, convergente, triangulacao, quan, qual]
dependencies: [SPEC-066, SPEC-064]
tdd_suite: "tests/test_metodos_mistos.py"
ct_count: 3
status: active
---

# SPEC-066 — Skill: Métodos Mistos

## Objetivo
Executar designs de métodos mistos com integração rigorosa entre fases.

## CTs

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SKILL.md existe com frontmatter válido | ✅ |
| CT-02 | Template para design sequencial disponível | ✅ |
| CT-03 | Protocolo de triangulação implementado | ✅ |

## Designs Suportados
1. Sequencial Explanatório (QUAN → qual)
2. Sequencial Exploratório (qual → QUAN)
3. Convergente Paralelo
