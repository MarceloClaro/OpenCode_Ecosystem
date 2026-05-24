# Referência Técnica — Integração Antigravity v1.0

> Progressive disclosure de `SKILL.md`

---

## 1. Arquitetura

```
OpenCode → AntiBridgePlugin (TS) → MCP Server (Python) → Agente Orquestrador → Antigravity
              classifyTask()         7 ferramentas JSON-RPC    fallback automático
              .evolve/ persist       antigravity_prompt        generate_image | browser | search
```

---

## 2. Ferramentas MCP (7 endpoints)

| Ferramenta | Parâmetros | Capacidade |
|---|---|---|
| `antigravity_delegate_task` | `task_type`, `prompt`, `context?`, `priority?` | Genérica |
| `antigravity_generate_image` | `description`, `style?`, `context?` | `generate_image` |
| `antigravity_browser_action` | `url`, `action`, `record?` | `browser_subagent` |
| `antigravity_web_search` | `query`, `sources?`, `synthesize?` | `search_web` |
| `antigravity_read_url` | `url`, `extract?` | `read_url_content` |
| `antigravity_run_subagent` | `task`, `parallel?`, `count?` | Subagente paralelo |
| `antigravity_get_bridge_state` | — | Estado JSON da ponte |

**Exemplo:**
```python
result = await mcp.call_tool("antigravity_generate_image", {
    "description": "Diagrama MASWOS v4.2, 49 agentes, 8 estágios sequenciais, estilo acadêmico vetorial",
    "style": "academic_diagram",
    "context": "Artigo Qualis A1"
})
# result["antigravity_prompt"] → enviar ao Antigravity
```

---

## 3. Classificação de Tarefas (`classifyTask`)

| Tipo | Gatilho | `requiresAntigravity` |
|---|---|:---:|
| `image` | imagem, visual, UI, design | `true` |
| `browser` | browser, navegador | `true` |
| `search` | pesquisa, URL, website | `true` |
| `orchestration` | paralelo, concurrent, demo | `true` |
| `analysis` | análise, refactor | `false` |
| `code` | (padrão) | `false` |

---

## 4. Ciclo de Vida de uma Tarefa

```
Prompt detectado → classifyTask() → AntiBridgeTask(status:"pending")
  → session.idle: status="delegated", totalDelegated++
  → MCP formata antigravity_prompt
  → Orquestrador envia ao Antigravity
  → tool.execute.after: status="completed", totalCompleted++
  → healthScore atualizado, estado salvo em .evolve/
```

**Retry (3 tentativas):**
```
session.error → retries++ → retries < 3: status="pending" (retry)
                           → retries ≥ 3: status="failed", reportar
```

---

## 5. Integração MASWOS → Qualis A1

```
SEEKER → identifica necessidade de figura
Antigravity Bridge (antigravity_generate_image)
  → Gera diagrama vetorial acadêmico
  → Salva em criador-artigo/figuras/
Agente A36 (exportacao_latex_pdf)
  → \includegraphics{figuras/fig_pipeline}
  → Legenda ABNT: "Figura X — Fonte: elaborada pelos autores via Antigravity"
PhD Auditor L5 → valida qualidade visual
Resultado: Artigo Qualis A1 com figuras auditáveis
```

---

## 6. Checklist de Saúde

| Item | Arquivo | Status Esperado |
|---|---|---|
| Plugin registrado | `opencode.json` L15 | `"plugins/antigravity-bridge.ts"` |
| MCP registrado | `opencode.json` L526 | `"antigravity-mcp": {..., "enabled": true}` |
| Agente existe | `agents/antigravity-orchestrator.md` | ✅ |
| Estado persistido | `.evolve/antigravity-bridge-state.json` | `healthScore > 80` |
| SKILL indexada | `skills/agent-forum/antigravity-integration/SKILL.md` | ✅ (criada 2026-05-24) |

---

## 7. Erros e Fallbacks

| Código | Cenário | Fallback |
|---|---|---|
| `E01` | Antigravity indisponível | Tarefa executada pelo OpenCode |
| `E02` | Timeout imagem >60s | Retry; após 3x: `[FIGURA PENDENTE]` |
| `E03` | Timeout browser >120s | Retry; após 3x: descrição textual |
| `E04` | 3 retries falhados | Notificar usuário |
| `E05` | Caracteres CJK no output | `ptbr_corrector.py` automático |
| `E06` | Erro conexão MCP | Delegação via prompt direto |

---

## 8. Estado JSON (`.evolve/antigravity-bridge-state.json`)

```json
{
  "version": "1.0.0",
  "sessionId": "session-abc123",
  "totalDelegated": 42,
  "totalCompleted": 40,
  "successRate": 0.952,
  "healthScore": 87.4,
  "capabilities": {
    "imageGeneration": true,
    "browserAutomation": true,
    "webSearch": true,
    "parallelExecution": true
  }
}
```
