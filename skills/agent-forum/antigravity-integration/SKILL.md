---
name: antigravity-integration
description: "Integração bidirecional OpenCode ↔ Antigravity (Google DeepMind) — delegação de imagem, browser, busca web e subagentes paralelos"
user-invocable: true
license: MIT
compatibility: OpenCode, Claude Code
metadata:
  author: OpenCode Ecosystem v4.2.1
  version: "1.0.0"
  ecossistema: opencode
  categoria: agent-forum
  componente: antigravity-bridge
  plugin: plugins/antigravity-bridge.ts
  mcp: nexus/antigravity_mcp_server.py
  agente: agents/antigravity-orchestrator.md
allowed-tools: Read Edit Write Bash
---

# Skill: Integração Antigravity v1.0

Ponte bidirecional entre o **OpenCode Ecosystem v4.2** e o **Antigravity** (Google DeepMind Advanced Agentic Coding). Permite que o OpenCode orquestre capacidades exclusivas do Antigravity de forma transparente, auditável e com fallback automático.

## Componentes

| Componente | Arquivo | Função |
|---|---|---|
| Plugin Bridge | `plugins/antigravity-bridge.ts` | Eventos de sessão + rastreamento de tarefas |
| Agente Orquestrador | `agents/antigravity-orchestrator.md` | Roteamento, delegação e fallback |
| Servidor MCP | `nexus/antigravity_mcp_server.py` | Protocolo JSON-RPC 2.0 (7 ferramentas) |
| Configuração | `opencode.json` L15 (plugin) + L526 (mcp) | Registro no ecossistema |

## Capacidades Exclusivas Delegadas ao Antigravity

| Capacidade | Gatilho | Timeout |
|---|---|---|
| `generate_image` | Palavras: imagem, visual, UI, design, diagrama | 60s |
| `browser_subagent` | Palavras: browser, navegador, automação web | 120s |
| `search_web` | Palavras: pesquisa web, busca online, DuckDuckGo | 30s |
| `read_url_content` | Palavras: URL, website, página web | 30s |
| `parallel_subagents` | Palavras: paralelo, simultâneo, concurrent | 90s |
| `artifact_creation` | Qualquer tarefa de artefato markdown estruturado | 60s |
| `query_rag` | Palavras: RAG, banco vetorial, consultar base | 45s |

## Matriz de Afinidade (Validação Cruzada)

| Par | Score | Razão |
|---|:---:|---|
| `antigravity ↔ manus-evolve` | 0.95 | Evolução autônoma de padrões delegados |
| `antigravity ↔ openagent` | 0.90 | Orquestração universal de tarefas |
| `antigravity ↔ criador-artigo` | 0.90 | MASWOS + figuras acadêmicas + busca |
| `antigravity ↔ seeker` | 0.85 | Pesquisa + verificação web de citações |
| `antigravity ↔ ecosystem-sync` | 0.85 | Health monitoring da ponte |
| `antigravity ↔ quantum-nexus-phd` | 0.80 | Análise avançada + visualizações |

## Uso via Agente

```
task(
  subagent_type="AntigravityOrchestrator",
  description="Gerar diagrama visual do pipeline MASWOS",
  prompt="""
    Tipo: image
    Descrição: Diagrama de arquitetura MASWOS v4.2, 49 agentes em fluxo sequencial
    Estilo: academic (para inclusão em artigo LaTeX)
  """
)
```

## Uso via MCP

```python
result = await mcp.call_tool("antigravity_generate_image", {
    "description": "Diagrama do pipeline OpenCode Ecosystem",
    "style": "diagram",
    "context": "Artigo acadêmico Qualis A1"
})
```

## Tratamento de Erros

| Cenário | Comportamento |
|---|---|
| Antigravity indisponível | Degradar para capacidade OpenCode equivalente |
| Timeout (>120s browser, >60s imagem) | Recolocar na fila para retry automático |
| 3 retries falhados | Marcar como "failed", reportar ao usuário |
| Erro de conexão MCP | Fallback para delegação via prompt direto |
| Caracteres CJK no output | Executar `ptbr_corrector.py` automaticamente |

## Observabilidade (`.evolve/`)

| Arquivo | Conteúdo |
|---|---|
| `antigravity-bridge-state.json` | Estado completo: sessão, fila, taxa de sucesso, healthScore |
| `antigravity-observability.jsonl` | Log de eventos JSONL por linha |
| `antigravity-task-log.jsonl` | Log detalhado de tarefas delegadas |

## Variáveis de Ambiente Expostas (via `shell.env`)

```bash
ANTIGRAVITY_BRIDGE_VERSION      # "1.0.0"
ANTIGRAVITY_BRIDGE_ACTIVE       # "true"
ANTIGRAVITY_BRIDGE_HEALTH       # Score 0-100
ANTIGRAVITY_BRIDGE_DELEGATED    # Total de tarefas delegadas
ANTIGRAVITY_BRIDGE_SUCCESS_RATE # Taxa de sucesso (0.000–1.000)
ANTIGRAVITY_BRIDGE_PENDING      # Tarefas na fila
ANTIGRAVITY_SESSION_ID          # ID da sessão atual
ANTIGRAVITY_CAP_IMAGE           # "true"
ANTIGRAVITY_CAP_BROWSER         # "true"
ANTIGRAVITY_CAP_SEARCH          # "true"
ANTIGRAVITY_CAP_PARALLEL        # "true"
ANTIGRAVITY_CAP_RAG             # "true"
```

## Integração com Pipeline Acadêmico (MASWOS → Qualis A1)

```
SEEKER (pesquisa) → Antigravity (verificação web + figuras)
  → Criador Artigo (49 agentes, 8 estágios)
  → Antigravity (browser demo se necessário)
  → PhD Auditor (Nash + Qualis)
  → Resultado: Artigo Qualis A1 com figuras geradas por IA
```

## Referências

- Detalhes técnicos completos: [`references/antigravity-bridge-reference.md`](references/antigravity-bridge-reference.md)
- Código do plugin: [`plugins/antigravity-bridge.ts`](../../plugins/antigravity-bridge.ts)
- Servidor MCP: [`nexus/antigravity_mcp_server.py`](../../nexus/antigravity_mcp_server.py)
- Agente orquestrador: [`agents/antigravity-orchestrator.md`](../../agents/antigravity-orchestrator.md)
