---
name: revisao-sistematica
description: "Skill para conduzir Revisão Sistemática da Literatura seguindo protocolo PRISMA 2020. Inclui formulação PICOS, busca estruturada, triagem, extração e síntese narrativa."
spec: "SPEC-065"
version: "1.0"
category: research
tags: [metodo, revisao-sistematica, prisma, picos, evidencia]
dependencies: [SPEC-065, SEEKER]
tdd_suite: "tests/test_revisao_sistematica.py"
ct_count: 5
status: active
---

# SPEC-065 — Skill: Revisão Sistemática

## Objetivo
Conduzir revisões sistemáticas da literatura com rigor metodológico PRISMA.

## CTs

| CT | Descrição | Status |
|:--:|:----------|:------:|
| CT-01 | SKILL.md existe com frontmatter válido | ✅ |
| CT-02 | Template PRISMA flowchart disponível | ✅ |
| CT-03 | Critérios PICOS implementados | ✅ |
| CT-04 | Busca estruturada em 3+ bases funcionando | ✅ |
| CT-05 | Extração e síntese narrativa operacional | ✅ |

## Protocolo PRISMA
1. Formulação da pergunta (PICOS)
2. Busca sistemática em múltiplas bases
3. Triagem por título/resumo
4. Leitura integral e elegibilidade
5. Extração de dados
6. Síntese narrativa
7. Avaliação de risco de viés
