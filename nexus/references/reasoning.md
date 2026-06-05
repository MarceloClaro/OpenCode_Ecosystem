<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Nexus-Multiagents-v6 (NMA) - Granular Reasoning Types

This reference contains the full list of 38 sub-types of reasoning used in NMA.

| Category | Sub-types | Description |
|-----------|-----------|-----------|
| **Deductive** | 8 | Modus Ponens, Tollens, Silogismo, etc |
| **Inductive** | 6 | Enumeração, Analogia, Generalização, etc |
| **Causal** | 5 | Direto, Indireto, Confundidor, etc |
| **Contrafactual** | 4 | Simples, Condicional, Múltiplo, Iterativo |
| **Bayesian** | 5 | Prior, Likelihood, Posterior, etc |
| **Analogical** | 4 | Estrutural, Funcional, Processual, etc |
| **Formal** | 3 | Prova Direta, Contradição, Indução |
| **Abductive** | 3 | Melhor Explicação, Diagnóstico, etc |

### Automatic Selection Selection
Selection is based on:
- `has_rules`: Boolean
- `has_patterns`: Boolean
- `uncertainty`: 0-1
- `complexity`: 0-1
- `time_constraint`: ms
