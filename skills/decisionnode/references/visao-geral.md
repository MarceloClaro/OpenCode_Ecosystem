# DecisionNode — Visão Geral

> Fonte: [github.com/decisionnode/DecisionNode](https://github.com/decisionnode/DecisionNode) | MIT License

## Conceito

DecisionNode não é um arquivo markdown — são **decisões estruturadas** armazenadas como JSON, embedadas como vetores e buscáveis por significado semântico.

Cada decisão é um nó:

```json
{
  "id": "backend-007",
  "scope": "Backend",
  "decision": "Skipped connection pooling for the embeddings DB — single writer, revisit if we add a sync daemon",
  "status": "active",
  "rationale": "Only one process writes at a time. Pooling added complexity with no measurable benefit.",
  "constraints": ["Do not add concurrent writers without revisiting this first"],
  "createdAt": "2024-11-14T09:22:00Z"
}
```

Decisões NÃO são "regras" para o contexto da IA (essas vão em CLAUDE.md).  
Decisões são "memórias" que a IA recupera via busca semântica quando relevante.

## Como Funciona

1. **Decisão é tomada** — via `decide add` (CLI) ou `add_decision` (MCP)
2. **Embedada como vetor** — Gemini `gemini-embedding-001`, armazenado em `vectors.json`
3. **IA recupera depois** — chama `search_decisions` via MCP, recebe decisões ranqueadas por similaridade de cosseno

A recuperação é **explícita**: a IA chama a ferramenta `search_decisions` passando uma query. Nada é pré-injetado no system prompt.

## Armazenamento

- Local: `~/.decisionnode/`
- SQLite para metadados + JSON para vetores
- Geminação via API free da Google (sem custo)
- Tudo roda localmente, sem nuvem

## Interfaces

| Interface | Comando | Para | Ferramentas |
|-----------|---------|------|-------------|
| **CLI** | `decide` | Você (terminal) | init, setup, add, search, list, get, edit, deprecate, activate, delete, delete-scope, export, import, check, embed, history, projects, config, ui |
| **MCP** | `decide-mcp` | Sua IA | search_decisions, add_decisions, update_decision, delete_decision, list_decisions, get_history, deprecate_decision, activate_decision, get_project_info |
| **Web UI** | `decide ui` | Visualização | Grafo, Espaço Vetorial (UMAP 2D), Lista |

## Configuração

```bash
decide config set agent_behavior strict    # IA DEVE buscar antes de codificar (default)
decide config set agent_behavior relaxed   # IA decide quando buscar
decide config set threshold 0.3            # Score mínimo similaridade (0.0-1.0)
```

## Web UI

```bash
decide ui              # foreground (Ctrl+C para parar)
decide ui -d           # background
decide ui status       # verificar se está rodando
decide ui stop         # parar servidor
```

Acessar em `http://localhost:7788`. Três visões: grafo de similaridade, projeção UMAP 2D dos embeddings, e lista filtrada por escopo.
