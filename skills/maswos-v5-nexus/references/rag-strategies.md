# 9 Estratégias RAG — MASWOS V5 NEXUS

Módulo RAG avançado com 9 estratégias de recuperação genuínas e não-simuladas, orquestrado via MCP (`maswos-rag` com suporte opcional a Server-Sent Events via `--sse` em `http://127.0.0.1:3003/sse`).

> **Importante:** O motor interno utiliza extração dinâmica de documentos do repositório (diretório `documentos/`) e implementa cálculos rigorosos de proximidade semântica por meio de um vetor TF-IDF local de 256 dimensões construído sob demanda, descontinuando completamente dados simulados (mock data).

## Estratégias

| # | Estratégia | Descrição | Caso de Uso |
|---|------------|-----------|-------------|
| 1 | **Vanilla** | Fluxo básico RAG (embed → retrieve → generate) | Consultas simples, prototipagem |
| 2 | **Memory** | RAG com memória Redis | Sessões com histórico, chatbots |
| 3 | **Agentic** | RAG com roteamento dinâmico de fontes | Múltiplas bases de conhecimento |
| 4 | **Graph** | RAG com grafo de conhecimento | Relações entre entidades |
| 5 | **Hybrid** | RAG híbrido vetorial + grafo | Máxima precisão semântica |
| 6 | **CRAG** | RAG com validação de qualidade | Documentos críticos (jurídico, saúde) |
| 7 | **Adaptive** | RAG com estratégia adaptativa | Carga de trabalho variável |
| 8 | **Fusion** | RAG-Fusion (RRF — Reciprocal Rank Fusion) | Múltiplas queries simultâneas |
| 9 | **HyDE** | Hypothetical Document Embeddings | Consultas sem contexto explícito |

## PageIndex (Vectorless RAG)

Estratégia complementar via `api.pageindex.ai/mcp` — RAG sem vector database, baseado em árvore de raciocínio.

- Precisão: 98.7% no FinanceBench
- Features: no_chunking, context_preservation, reasoning_search

## Arquitetura do Módulo RAG

```
maswos-rag (MCP HTTP :3003)
├── Vanilla RAG
├── Memory RAG (Redis)
├── Agentic RAG (routing)
├── Graph RAG (knowledge graph)
├── Hybrid RAG (vector + graph)
├── CRAG (quality validation)
├── Adaptive RAG
├── Fusion RAG (RRF)
└── HyDE (hypothetical docs)
```

> **Fonte:** `github.com/MarceloClaro/maswos-v5-nexus` / `mcp_servers_config.json` 🟢
