<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: world-bank-data-analysis
description: Indicadores de Sucesso
version: 1.0.0
author: ecosystem
category: research
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# World Bank Data Analysis

# Indicadores de Sucesso

- r > 0.70: correlacao forte (ex: P&D, servicos alta tecnologia)
- r < 0.30: correlacao fraca (ex: educacao %PIB isolada)
- r negativo: trade-off estrutural (ex: agricultura vs desenvolvimento)

## Workflow

### Step 1: Definir escopo
Identifique tema, fontes e criterios.

### Step 2: Coletar dados
Utilize ferramentas de busca.

### Step 3: Analisar
Processe dados, identifique padroes.

### Step 4: Gerar output
Produza resultado final.

## Best Practices

1. Citar fontes verificaveis (DOIs, URLs)
2. Cruzar informacoes de 2+ fontes
3. Manter registro de buscas
4. Validar dados antes do output
5. Saida em PT-BR formal

## Integration

| Component | Type | Connection |
|-----------|------|------------|
| scihub | MCP | Download artigos |
| websearch | MCP | Busca web |
| context7 | MCP | Documentacao |
