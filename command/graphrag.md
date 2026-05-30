<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Inspirado pelo GraphRAG + Zep Cloud do MiroFish.
-->

---
description: >
  Constrói e consulta o grafo de conhecimento do ecossistema OpenCode.
  Inspirado pelo GraphRAG (graph_builder.py + zep_tools.py) do MiroFish.
  Mapeia agentes, skills, MCPs, comandos e suas relações em SQLite.
  Uso: /graphrag [--rebuild] [--query="termo"] [--verify] [--visualize]
  Exemplos:
    /graphrag                           — status do grafo + menu
    /graphrag --rebuild                 — reconstrói grafo do zero
    /graphrag --query "security"        — busca componentes relacionados a segurança
    /graphrag --query "dependências do MCP sqlite"
    /graphrag --verify                  — verifica integridade
    /graphrag --visualize               — visualiza grafo completo
---

# GraphRAG — Grafo de Conhecimento OpenCode

Ativa o **Code GraphRAG Agent**, que constrói e consulta um grafo de
conhecimento do ecossistema OpenCode em SQLite.

## Como funciona

```
/graphrag [opção]
```

### Opções

| Opção | Descrição |
|-------|-----------|
| (vazia) | Status do grafo + menu interativo |
| `--rebuild` | Reconstrói o grafo do zero |
| `--update` | Atualização incremental |
| `--query "texto"` | Busca semântica |
| `--verify` | Verifica integridade |
| `--visualize` | Gera visualização do grafo |

### Exemplos de Query

```
/graphrag --query "find all agents"
/graphrag --query "what depends on MCP filesystem"
/graphrag --query "path from agent:scout to mcp:sqlite"
/graphrag --query "orphans"
/graphrag --query "stats"
/graphrag --query "components related to security"
```

## Pipeline

```
/graphrag --rebuild

🔍 Escaneando: C:\Users\marce\.config\opencode
  📦 Agents...     8 nós, 12 arestas
  📦 Skills...     22 nós, 18 arestas
  📦 Commands...   14 nós, 10 arestas
  📦 MCPs...       35 nós, 0 arestas

📊 Estatísticas: 79 nós, 40 arestas, 156 tags
✅ Grafo íntegro!
```

## Arquitetura

```
Nodes: Agent | Skill | MCP | Command | Module | File | Config
Edges: imports | depends_on | registers_in | extends | related_to
DB:    .reversa/code-graph.db (SQLite)
```
