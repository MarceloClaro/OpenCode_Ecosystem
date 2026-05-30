<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

---
description: Modo autônomo do OpenCode — orquestra agentes, executa tarefas em loop, controla navegador, audita websites. Ative com /auto.
---

# OpenCode Autônomo

Ativa o modo de operação autônoma do OpenCode, integrando todas as ferramentas de autonomia.

## Stack de Autonomia

```
┌──────────────────────────────────────────────────────┐
│                  ORQUESTRAÇÃO                         │
│  ralph-tui: loop autônomo de tarefas                 │
│  superpowers/subagent-driven-development: dispatcher │
│  planning-with-files: tracking em arquivos           │
├──────────────────────────────────────────────────────┤
│                  PERCEPÇÃO                            │
│  browser-use: controle de navegador (web)            │
│  squirrelscan-audit: auditoria de sites              │
│  playwright (MCP): testes E2E                        │
├──────────────────────────────────────────────────────┤
│                  DESENVOLVIMENTO                      │
│  superpowers: brainstorming → plan → TDD → review    │
│  reversa: engenharia reversa de specs                │
│  agentic-mcp: servidores MCP                         │
├──────────────────────────────────────────────────────┤
│                  DOMÍNIOS                             │
│  react-native-best-practices: mobile                 │
│  vue-best-practices: Vue 3                           │
│  ui-ux-pro-max: design intelligence                  │
│  email-best-practices: email                         │
│  notebooklm: pesquisa com IA                         │
└──────────────────────────────────────────────────────┘
```

## Como ativar

```
/auto
```

## Fluxo autônomo

1. **Recebe tarefa** do usuário ou PRD
2. **Brainstorming** (superpowers) — refina requisitos
3. **Planning** (writing-plans) — quebra em tasks bite-sized
4. **Tracking** (planning-with-files) — registra em task_plan.md
5. **Execução** (subagent-driven-development) — dispatcher por task
   - Browser-use para interagir com web
   - squirrelscan para auditar outputs
   - playwright para testes E2E
6. **Revisão** (requesting-code-review) — valida cada task
7. **Loop** (ralph-tui) — repete até completar todas as tasks

## Pré-requisitos

```bash
# Browser automation
pip install browser-use && browser-use install

# Website auditing  
# Download from: https://squirrelscan.com/download

# Task orchestration
bun install -g ralph-tui

# OpenCode plugin (já configurado)
# superpowers@git+https://github.com/obra/superpowers.git
```
