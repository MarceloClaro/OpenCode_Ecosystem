# DecisionNode — MCP Server

## Conexão

O MCP server `decide-mcp` já está registrado no OpenCode como `decisionnode`.
Para conectar manualmente em outras ferramentas:

```bash
# Claude Code
claude mcp add decisionnode -s user decide-mcp

# Cursor
# Adicionar em .cursor/mcp.json
```

## 9 Ferramentas MCP

| Ferramenta | Descrição | Parâmetros |
|------------|-----------|------------|
| `search_decisions` | Busca semântica por similaridade | query: string, topK?: number (default 5), scope?: string |
| `add_decision` | Adicionar nova decisão | decisions: AddDecisionInput[] (id, scope, decision, rationale, constraints, status) |
| `update_decision` | Atualizar decisão existente | id: string, updates: Partial\<Decision\> |
| `delete_decision` | Remover permanentemente | id: string |
| `list_decisions` | Listar decisões | scope?: string, status?: "active" \| "deprecated" \| "all" |
| `get_history` | Histórico de alterações | limit?: number |
| `deprecate_decision` | Soft-delete (reversível) | id: string |
| `activate_decision` | Reativar decisão depreciada | id: string |
| `get_project_info` | Informações do projeto | (nenhum) |

## Comportamento do Agente

- **strict** (default): descrição da ferramenta instrui IA a SEMPRE buscar antes de qualquer mudança de código
- **relaxed**: IA decide quando a busca é relevante

Configurar via: `decide config set agent_behavior <strict|relaxed>`
