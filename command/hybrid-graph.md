<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Inspirado pelo GraphToolsService do MiroFish-Offline (graph_tools.py).
-->

---
description: >
  Busca híbrida em grafo de conhecimento com 3 estratégias: InsightForge
  (análise profunda), PanoramaSearch (visão panorâmica), QuickSearch (busca
  rápida). Inspirado pelo GraphToolsService do MiroFish-Offline.
  Uso: /hybrid-graph <estratégia> --graph <id> --query "<texto>" [opções]
  Estratégias: insight, panorama, quick, stats
  Exemplos:
    /hybrid-graph insight --graph mirofish_abc --query "Impacto das políticas"
    /hybrid-graph panorama --graph mirofish_abc --query "privacidade"
    /hybrid-graph quick --graph mirofish_abc --query "GDPR" --limit 5
    /hybrid-graph stats --graph mirofish_abc
pinned: false
---

# Hybrid Graph Retrieval — Busca em Grafo de Conhecimento

Ativa o **Hybrid Graph Agent** para buscar informações em grafos de
conhecimento com diferentes níveis de profundidade.

## Como funciona

```
/hybrid-graph <estratégia> --graph <id> --query "<texto>" [opções]
```

### Estratégias

| Estratégia | Descrição | Uso típico |
|---|---|---|
| `insight` | Análise profunda com sub-perguntas | "Qual o impacto de X em Y?" |
| `panorama` | Visão completa com histórico | "Me mostre tudo sobre X" |
| `quick` | Busca rápida e leve | "O que é X?" |
| `stats` | Estatísticas do grafo | — |

### Opções globais

| Opção | Descrição | Padrão |
|---|---|---|
| `--graph <id>` | ID do grafo | mirofish_abc |
| `--query <texto>` | Consulta/pesquisa | — |
| `--limit <n>` | Limite de resultados | 15 |
| `--include-historical` | Incluir histórico (panorama) | true |
| `--json` | Saída em JSON | false |

### Fluxo

```
Usuário
  → Estratégia escolhida
    → InsightForge: decompõe pergunta em sub-perguntas
    → PanoramaSearch: varre todos os nós e arestas
    → QuickSearch: busca direta com keywords
  → Resultados com escala de confiança (🟢/🟡/🔴)
  → Apresentação formatada
```
