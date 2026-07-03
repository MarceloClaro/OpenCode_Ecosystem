---
name: analise-qualitativa
description: "Skill para Análise Qualitativa de dados textuais usando Análise Temática (Braun & Clarke) e Grounded Theory. Suporta codificação aberta, axial e seletiva com geração de categorias emergentes."
spec: "SPEC-065"
version: "1.0"
category: research
tags: [qualitativo, analise-tematica, grounded-theory, entrevistas, codificacao]
dependencies: [SPEC-065]
tdd_suite: "tests/test_analise_qualitativa.py"
ct_count: 4
status: active
---

# Skill: Análise Qualitativa

## Objetivo
Analisar dados qualitativos (entrevistas, observações, documentos) com rigor metodológico.

## CTs

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SKILL.md existe com frontmatter válido | ✅ |
| CT-02 | Template de codificação temática disponível | ✅ |
| CT-03 | Roteiro de entrevista semiestruturada implementado | ✅ |
| CT-04 | Matriz de categorias e temas gerada | ✅ |

## Métodos Suportados
- Análise Temática Reflexiva (Braun & Clarke, 2006)
- Grounded Theory (Corbin & Strauss, 2015)
- Análise de Conteúdo (Bardin, 2011)
