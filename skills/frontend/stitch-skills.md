<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: stitch-skills
description: Available Skills
version: 1.0.0
author: ecosystem
category: frontend
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# Stitch Skills

# Available Skills
- **stitch-design** — Unified entry point for Stitch design work (prompt enhancement, design system synthesis, screen generation)
- **stitch-loop** — Multi-page website generation from a single prompt
- **design-md** — Generate DESIGN.md files documenting design systems
- **enhance-prompt** — Transform vague UI ideas into polished Stitch prompts
- **react-components** — Convert Stitch screens to React component systems
- **remotion** — Generate walkthrough videos from Stitch projects
- **shadcn-ui** — Expert guidance for shadcn/ui integration

Install: `npx skills add google-labs-code/stitch-skills --skill <name> --global`
More: https://github.com/google-labs-code/stitch-skills

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
