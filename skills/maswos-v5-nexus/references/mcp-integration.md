# Integração MCP — MASWOS V5 NEXUS

## Servidores MCP

| Servidor | Tipo | Comando no opencode.json | Agentes | Tools |
|----------|------|--------------------------|---------|-------|
| `maswos-juridico` | local (stdio) | `python skills/maswos-v5-nexus/servers/juridico_server.py` | 60 | consultar_legislacao, validar_documento_juridico, listar_modelos_juridicos |
| `maswos-mcp` | local (stdio) | `python skills/maswos-v5-nexus/servers/maswos_server.py` | 15 | orquestrar_pipeline, listar_agentes, verificar_status_mcp |
| `maswos-rag` | local (stdio) | `python skills/maswos-v5-nexus/servers/rag_server.py` | 21 | consultar_rag, listar_estrategias_rag, comparar_estrategias_rag |

## Dependências Cross-MCP

```
juridico       → (provides: legal_context)
academic       → (provides: research_data, papers, datasets)
maswos-mcp     → depends_on: [juridico, academic]
pageindex      → depends_on: [academic]
opencode       → depends_on: [juridico, academic, maswos-mcp]
```

## Launcher

```bash
# Modo stdio (auto-iniciado pelo OpenCode): ja configurado em opencode.json
# Modo SSE (servidor persistente):
python skills/maswos-v5-nexus/servers/launch_maswos_mcps.py --sse
# Servidor especifico em SSE:
python skills/maswos-v5-nexus/servers/juridico_server.py --sse --port 3001

## PageIndex (Vectorless RAG)

API externa para RAG sem vector database.
- Endpoint: `https://api.pageindex.ai/mcp`
- Auth: Bearer token via variável de ambiente `PAGEINDEX_API_KEY`
- Benchmarks: 98.7% no FinanceBench

> **Fonte:** `github.com/MarceloClaro/maswos-v5-nexus` / `mcp_servers_config.json` 🟢
