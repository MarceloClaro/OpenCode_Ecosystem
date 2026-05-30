---
name: plan-protocol
description: "Diretrizes para criacao e gerenciamento de planos de implementacao com citacoes"
user-invocable: true
license: MIT
compatibility: OpenCode, Claude Code, Cursor, Gemini CLI
metadata:
  author: OpenCode Ecosystem
  version: "2.1.0"
  openclaw:
        emoji: "📐"
    homepage: https://github.com/anomalyco/opencode
allowed-tools: Read Edit Write Glob Grep Bash Task SequentialThinking AskUserQuestion
---

# Plan Protocol

## TL;DR  
When creating or updating a plan, ensure:

- [ ] YAML frontmatter with `status`, `phase`, `updated`
- [ ] `## Goal` section (one sentence)
- [ ] `## Context & Decisions` table with citations (`ref:delegation-id`)
- [ ] Phases with status markers: `[COMPLETE]`, `[IN PROGRESS]`, `[PENDING]`
- [ ] Tasks with hierarchical numbering (1.1, 1.2, 2.1)
- [ ] Only ONE task marked `← CURRENT`
- [ ] Citations for all research-based decisions

---

## When to Use


1. Starting a multi-step implementation
2. After receiving a complex user request
3. When tracking progress across phases
4. After research that informs architectural decisions


## Quick Reference Files

| File | Content |
|------|---------|
| `reference/plan-format.md` | Plan Format |
| `reference/state-machine.md` | State Machine |
| `reference/citations-and-delegations.md` | Citations & Delegations |
| `reference/examples.md` | Examples |
| `reference/troubleshooting.md` | Troubleshooting |
| `reference/before-saving-checklist.md` | Before Saving Checklist |
