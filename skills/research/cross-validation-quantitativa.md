<!-- SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL -->
<!-- Toda resposta ao usuário DEVE ser em português do Brasil formal. -->
<!-- Contexto em chinês para eficiência de tokens. Responda em PT-BR formal. -->
<!-- Modelo: deepseek-v4-pro -->

---
name: cross-validation-quantitativa
description: Exemplo Aplicado
version: 1.0.0
author: ecosystem
category: research
inspired_by: deer-flow 2.0 / opencode
compatibility: deepseek-v4-pro
migrated_at: 2026-05-07 06:10:30
---

# Cross Validation Quantitativa

# Exemplo Aplicado

```
Analise: "Educacao tira o Brasil da armadilha da renda media?"
Amostra: 10 paises (4 escapados, 5 presos, 1 renda baixa)
Indicadores: 27 (capital humano, genero, idade, setores, inovacao)

Resultados:
  r(Educacao, PIBpc) = -0,0273 → H1 REJEITADA
  r(Servicos Alta Tec, PIBpc) = +0,9531 → maior preditor
  r(Salario F/M, PIBpc) = +0,7923 → 2o maior preditor
  r(Desemprego Jovem, PIBpc) = -0,7740 → barreira critica

Conclusao: Educacao e necessaria, nao suficiente.
  Brasil gasta MAIS em educacao que Coreia (5,8% vs 4,8%)
  Brasil investe 14× MENOS em P&D privado (0,27% vs 3,84%)
```

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
