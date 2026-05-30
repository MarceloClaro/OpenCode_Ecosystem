<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: open-design
description: Quick Start
version: 1.0.0
author: ecosystem
category: frontend
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# Open Design

# Quick Start
```bash
git clone https://github.com/nexu-io/open-design.git
cd open-design
pnpm install
pnpm tools-dev run web
```

Source: https://github.com/nexu-io/open-design (25.7k ⭐)

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
