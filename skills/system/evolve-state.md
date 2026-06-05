<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: evolve-state
description: Aprendizado
version: 1.0.0
author: ecosystem
category: system
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# Evolve State

# Aprendizado
- Ranking: frequência × sucesso × recência
- Sugestões: skills pouco usadas → remover; erros recorrentes → self-heal
- Auto-otimização: desabilitar skills que falham; priorizar similares às mais usadas

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
