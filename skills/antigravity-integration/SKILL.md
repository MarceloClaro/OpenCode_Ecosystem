---
name: antigravity-integration
version: "1.0.0"
description: "Skill de integração OpenCode ↔ Antigravity — expõe capacidades exclusivas do Google DeepMind Advanced Agentic Coding ao ecossistema OpenCode v4.2"
category: orchestration
author: "OpenCode Ecosystem / Antigravity Bridge"
evolved: false
source: "antigravity-bridge.ts + antigravity_mcp_server.py"
tags:
  - antigravity
  - bridge
  - orchestration
  - external-ai
  - image-generation
  - browser-automation
  - web-search
---

# Skill: Integração Antigravity

## Visão Geral

Esta skill implementa a ponte bidirecional entre o **OpenCode Ecosystem v4.6** e o
**Antigravity** (Google DeepMind Advanced Agentic Coding), permitindo que o OpenCode
orquestre capacidades exclusivas do Antigravity de forma transparente e auditável.

## Componentes

| Componente | Arquivo | Função |
|---|---|---|
| Plugin Bridge | `plugins/antigravity-bridge.ts` | Eventos de sessão + rastreamento |
| Agente Orquestrador | `agents/antigravity-orchestrator.md` | Roteamento e delegação |
| Servidor MCP | `nexus/antigravity_mcp_server.py` | Protocolo JSON-RPC 2.0 |
| Configuração | `opencode.json` (plugin + mcp) | Registro no ecossistema |

## Capacidades Exclusivas do Antigravity

```
generate_image       → Diagramas, mockups, UI, figuras acadêmicas
browser_subagent     → Automação de browser com gravação WebP
search_web           → Pesquisa web com síntese de múltiplas fontes
read_url_content     → Extração de conteúdo de URLs específicas
parallel_subagents   → Execução paralela com estado compartilhado
artifact_creation    → Artefatos markdown estruturados
```

## Afinidade no Ecossistema (Matriz de Validação Cruzada)

```
antigravity ↔ manus-evolve:        0.95 (evolução autônoma)
antigravity ↔ openagent:           0.90 (orquestração universal)
antigravity ↔ criador-artigo:      0.90 (MASWOS + figuras + busca)
antigravity ↔ seeker:              0.85 (pesquisa + verificação web)
antigravity ↔ ecosystem-sync:      0.85 (health monitoring)
antigravity ↔ quantum-nexus-phd:   0.80 (análise avançada)
```

## Uso via Agente

```
task(
  subagent_type="AntigravityOrchestrator",
  description="Gerar diagrama visual do pipeline MASWOS",
  prompt="""
    Delegar ao Antigravity:
    Tipo: image
    Descrição: Diagrama de arquitetura do pipeline MASWOS v4.6,
    mostrando os 49 agentes em fluxo sequencial com setas coloridas
    Estilo: academic (para inclusão em artigo LaTeX)
  """
)
```

## Uso via MCP

```python
# Via antigravity-mcp MCP
result = await mcp.call_tool("antigravity_generate_image", {
    "description": "Diagrama do pipeline OpenCode Ecosystem",
    "style": "diagram",
    "context": "Artigo acadêmico Qualis A1"
})
```

## Variáveis de Ambiente Expostas

```bash
ANTIGRAVITY_BRIDGE_VERSION     # Versão da ponte
ANTIGRAVITY_BRIDGE_ACTIVE      # true|false
ANTIGRAVITY_BRIDGE_HEALTH      # Score 0-100
ANTIGRAVITY_BRIDGE_DELEGATED   # Total de tarefas delegadas
ANTIGRAVITY_BRIDGE_SUCCESS_RATE # Taxa de sucesso
ANTIGRAVITY_BRIDGE_PENDING     # Tarefas na fila
ANTIGRAVITY_SESSION_ID         # ID da sessão atual
ANTIGRAVITY_CAP_IMAGE          # Capacidade de imagem ativa
ANTIGRAVITY_CAP_BROWSER        # Capacidade de browser ativa
ANTIGRAVITY_CAP_SEARCH         # Capacidade de busca ativa
ANTIGRAVITY_CAP_PARALLEL       # Capacidade paralela ativa
```

## Observabilidade

Logs persistentes em `.evolve/`:
- `antigravity-bridge-state.json` — Estado completo da ponte
- `antigravity-observability.jsonl` — Log de eventos por linha
- `antigravity-task-log.jsonl` — Log detalhado de tarefas

## Tratamento de Erros

| Cenário | Comportamento |
|---|---|
| Antigravity indisponível | Degradar para capacidade OpenCode equivalente |
| Caracteres CJK no output | Executar `ptbr_corrector.py` automaticamente |
| Timeout (>120s browser, >60s imagem) | Recolocar na fila para retry |
| 3 retries falhados | Marcar como "failed", reportar ao usuário |
| Erro de conexão MCP | Fallback para delegação via prompt direto |

## Integração com Pipeline Acadêmico (MASWOS → Qualis A1)

```
SEEKER (pesquisa) → Antigravity (verificação web + figuras)
  → Criador Artigo (49 agentes, 8 estágios)
  → Antigravity (browser demo se necessário)
  → PhD Auditor (Nash + Qualis)
  → Resultado: Artigo Qualis A1 com figuras geradas por IA
```
