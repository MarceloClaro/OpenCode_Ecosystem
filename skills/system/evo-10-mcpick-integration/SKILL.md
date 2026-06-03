---
name: evo-10-mcpick-integration
category: system
version: "1.0.0"
kind: python
description: >-
  Skill evoluida no Round 10 do AutoEvolve. Integra mcpick (MCP config
  manager), gerencia versoes do SDK OpenCode, audita MCPs via CLI externa,
  e aplica progressive disclosure em skills >2.5KB.
---

# evo-10-mcpick-integration

## Contexto
Evoluida automaticamente pelo AutoEvolve em 2026-05-12 (Round 10).
Ecossistema saudavel (100%), 20 MCPs ativos, 74+ skills, 118 agentes.

## Capacidades

### 1. Gerenciamento de MCPs com mcpick
- Usar `mcpick list --client opencode --json` para auditoria de todos MCPs
- Usar `mcpick clients` para descobrir configs em todos os clientes
- Usar `mcpick enable/disable <server>` para toggle rapido
- Suporta: OpenCode, Claude Code, Gemini CLI, VS Code, Cursor, Windsurf, Pi

### 2. Sync de SDK OpenCode
- SDK `@opencode-ai/sdk` e `opencode-ai` devem estar na mesma versao
- Verificar com: `npm outdated -g`
- Atualizar com: `npm update -g @opencode-ai/sdk opencode-ai`
- chrome-devtools-mcp deve estar >= 0.26.0

### 3. Progressive Disclosure
- Skills locais: SKILL.md < 2.5KB
- Skills externas >15KB: usar arquivos de referencia
- Ideal: 6 skills locais acessiveis (~10KT budget)
- Descricao < 100t, conteudo < 250t

### 4. Health Checks
- score >=95 saudavel, >=85 atencao, >=70 alerta, <70 critico
- Verificacoes: mcpick + npm outdated + runtimes
- 9 skills locais com frontmatter valido, 0 anomalias

## Metricas do Round 10
- npm packages atualizados: 8 (SDK 1.14.33 -> 1.14.48)
- mcpick instalado: v0.0.25
- MCPs auditorados: 20 ativos
- Health pos-evolucao: 100%
- Novas descobertas: mcp-use, awesome-claude, ask-user-questions-mcp
