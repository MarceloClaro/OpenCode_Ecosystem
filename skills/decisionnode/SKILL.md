---
name: decisionnode
description: "DecisionNode: CLI + MCP para memória estruturada de decisões entre ferramentas de IA (Claude Code, Cursor, Windsurf, Antigravity). Permite registrar, buscar semanticamente, editar e depreciar decisões técnicas. Use sempre que precisar registrar uma decisão arquitetural, lembrar decisões passadas ou consultar contexto histórico de design."
---

# DecisionNode Skill

## Visão Geral

DecisionNode é um armazenamento local de **decisões estruturadas** com busca semântica via embeddings (Gemini free tier). Cada decisão é um nó JSON com `id`, `decision`, `rationale`, `constraints` e `scope`. Opera via:

| Interface | Comando | Para |
|-----------|---------|------|
| **CLI** | `decide <comando>` | Você (terminal) |
| **MCP Server** | `decide-mcp` | Sua IA (9 ferramentas) |

Ambos leem/escrevem no mesmo store local (`~/.decisionnode/`).

## Instalação

```bash
npm install -g decisionnode
cd seu-projeto && decide init    # cria store do projeto
decide setup                      # configura Gemini API key (gratuito)
```

> O MCP server `decide-mcp` já está registrado no OpenCode como `decisionnode`.

## Comandos CLI Rápidos

| Comando | Descrição |
|---------|-----------|
| `decide add` | Adicionar decisão (interativo) |
| `decide add -s Backend -d "decisão"` | Adicionar inline |
| `decide add --global` | Decisão global (todos projetos) |
| `decide search "consulta"` | Busca semântica |
| `decide list` | Listar todas |
| `decide get <id>` | Ver decisão |
| `decide deprecate <id>` | Soft-delete |
| `decide activate <id>` | Reativar |
| `decide ui` | Web UI local (grafo + espaço vetorial) |

## Fluxo Recomendado

1. **Ao fazer uma decisão arquitetural**: `decide add -s "Módulo X" -d "decidimos Y porque Z"`
2. **Ao iniciar uma tarefa**: agente chama `search_decisions` via MCP automaticamente
3. **Ao revisar**: `decide list` + `decide history` para auditoria

## Conteúdo de Referência

* `referencias/visao-geral.md` — Documentação completa do DecisionNode
* `referencias/mcp-server.md` — 9 ferramentas MCP e configuração
* `referencias/workflows.md` — Padrões de uso recomendados
* `referencias/cli-reference.md` — Referência completa da CLI
