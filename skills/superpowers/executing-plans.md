<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: executing-plans
description: When to Stop
version: 1.0.0
author: ecosystem
category: superpowers
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# Executing Plans

# When to Stop

STOP when:
- Hit a blocker
- Plan has critical gaps
- Don't understand instruction
- Verification fails repeatedly

Don't force through blockers — stop and ask.

## Workflow

### Step 1: Analisar
Entenda o problema.

### Step 2: Planejar
Defina passos e criterios.

### Step 3: Executar
Implemente solucao.

### Step 4: Verificar
Valide resultado.

## Best Practices

1. Validar antes de completar
2. PT-BR formal
3. Documentar decisoes
4. Verificacao automatica
5. Rastreabilidade

## Integration

| Component | Type | Connection |
|-----------|------|------------|
| nexus_integration | Script | Orquestracao |
| memory | MCP | Contexto |
| sequential-thinking | MCP | Raciocinio |
