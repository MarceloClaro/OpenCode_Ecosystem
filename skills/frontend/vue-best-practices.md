<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: vue-best-practices
description: Performance (after correctness)
version: 1.0.0
author: ecosystem
category: frontend
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# Vue Best Practices

# Performance (after correctness)
- Virtualize large lists
- `v-once`/`v-memo` for static subtrees
- Avoid component abstraction in hot list paths

Install: `npx skills add vuejs-ai/skills`
More: https://github.com/vuejs-ai/skills

## Workflow

### Step 1: Analisar requisitos
Identifique componentes e estado.

### Step 2: Implementar
Crie estrutura com semantica correta.

### Step 3: Estilizar
Aplique estilos consistentes.

### Step 4: Testar
Verifique acessibilidade e responsividade.

## Best Practices

1. Semantica HTML correta
2. Acessibilidade (ARIA, contrastes)
3. Design system consistente
4. Testar em multiplos viewports
5. Componentes modulares

## Integration

| Component | Type | Connection |
|-----------|------|------------|
| chrome-devtools | MCP | Debug |
| playwright | MCP | Automacao |
| eslint | Tool | Linting |
