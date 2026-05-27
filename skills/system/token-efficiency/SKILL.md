---
name: token-efficiency
description: "Otimizacao de tokens para ecossistema OpenCode - Chines + PT-BR + deepseek-v4-pro"
user-invocable: true
license: MIT
compatibility: OpenCode, Claude Code, Cursor, Gemini CLI
metadata:
  author: OpenCode Ecosystem
  version: "2.1.0"
  openclaw:
        emoji: "⚡"
    homepage: https://github.com/anomalyco/opencode
allowed-tools: Read Edit Write Glob Grep Bash
---

# Token Efficiency v2.0

## Objetivo
Maximizar eficiencia de tokens mantendo saida em portugues brasileiro formal.

## Principios (Resumo)

| # | Principio | Economia |
|---|-----------|----------|
| 1 | Contexto em chines simplificado | 30-40% |
| 2 | Saida obrigatoria PT-BR formal | - |
| 3 | Modelo deepseek-v4-pro (200K ctx, gratuito) | -100% custo |
| 4 | Tabelas vs paragrafos | 25-35% |
| 5 | Referencia vs copia | 50-70% |

## Quick Reference Files

| File | Content |
|------|---------|
| `reference.md` | Detailed principles, compression patterns, workflow |
| `reference/linguistic-corrector.md` | PT-BR corrector pipeline, commands, metrics |

## Skills Complementares

| Skill | Relação |
|-------|---------|
| `skills/juridico/edicao-cirurgica` | **Escopo universal** — retorna apenas o delta modificado, nunca reescreve o artefato inteiro. Principal técnica de economia de tokens em edições iterativas. |
