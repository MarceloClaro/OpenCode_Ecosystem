<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: agent-browser
description: Key Features
version: 1.0.0
author: ecosystem
category: tooling
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# Agent Browser

# Key Features
- **Snapshot:** Accessibility tree with refs for AI
- **Annotated Screenshots:** Numbered element labels
- **React DevTools:** Component tree, props, hooks, renders
- **Network:** Request tracking, route interception, HAR export
- **Auth:** Chrome profile reuse, session persistence, state encryption
- **Security:** Domain allowlist, action policy, content boundaries
- **Diff:** Snapshot and screenshot comparison

Install: `npm install -g agent-browser && agent-browser install`
More: https://github.com/vercel-labs/agent-browser

## Workflow

### Step 1: Configurar
Instale dependencias.

### Step 2: Executar
Rode com parametros adequados.

### Step 3: Analisar
Verifique output.

### Step 4: Limpar
Remova temporarios.

## Best Practices

1. Verificar compatibilidade
2. Testar em ambiente isolado
3. Documentacao atualizada
4. Validar outputs
5. Limpar temporarios

## Integration

| Component | Type | Connection |
|-----------|------|------------|
| code-runner | Tool | Execucao |
| bash | Tool | Sistema |
| filesystem | MCP | Arquivos |
