<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: philosophy-enforcement
description: Code Philosophy - MANDATORY
version: 1.0.0
author: ecosystem
category: system
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# Philosophy Enforcement

# Code Philosophy - MANDATORY

Before writing or modifying any code, you MUST:

1. **Select the relevant philosophy** based on your task:
   - Working on UI/frontend? → Load **`frontend-philosophy`** (The 5 Pillars of Intentional UI)
   - Working on backend/logic? → Load **`code-philosophy`** (The 5 Laws of Elegant Defense)
   - Working on both? → Load both

2. **Load the skill** using the `skill` tool BEFORE implementation

3. **Verify your implementation** against the philosophy checklist BEFORE completing

4. **Refactor if needed** - if code violates any principle, fix it before proceeding

This is NOT optional. These philosophies define how code must be written in this project.

## Workflow

### Step 1: Identificar
Analise contexto e defina escopo.

### Step 2: Implementar
Aplique modificacoes.

### Step 3: Validar
Execute testes.

### Step 4: Documentar
Registre alteracoes.

## Best Practices

1. Backup antes de modificar
2. Validar com testes
3. Manter logs
4. Documentar decisoes
5. Seguir padroes

## Integration

| Component | Type | Connection |
|-----------|------|------------|
| sync_orchestrator | Script | Sincronizacao |
| memory | MCP | Contexto |
| filesystem | MCP | Arquivos |
