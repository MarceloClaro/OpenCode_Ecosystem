# Módulo de Auditoria Acadêmica — MASWOS V5 NEXUS

Pipeline completo para produção e auditoria de artigos com score Qualis A1.

## 9 Skills de Auditoria

| # | Skill | Agentes | Função |
|---|-------|---------|--------|
| 1 | `auditor_estatistico` | 4 | Valida Cohen's d, η², p-valores |
| 2 | `auditor_dados_economicos` | 4 | Cross-reference World Bank |
| 3 | `auditor_citacoes` | 5 | Valida ABNT |
| 4 | `auditor_dados_datasets` | 5 | Valida fontes de dados |
| 5 | `auditor_tratamento_dados` | 5 | Missing, outliers |
| 6 | `auditor_metodologia_analise` | 6 | Design, métodos, robustez |
| 7 | `auditor_qualis_a1` | 7 | Simula banca |
| 8 | `pipeline_auditoria` | 1 | Orquestra todos |
| 9 | `criador_artigo` | 43 | Cria artigos |

## Quality Gates

| Gate | Nome | Threshold | Responsável |
|------|------|-----------|-------------|
| G0 | Intent Detection | 100% | orchestrator_unified |
| GR | Routing Validation | 85% | intent_router |
| GE | Execution Validation | 90% | cross_mcp_validator |
| GF | Final Output | 95% | result_aggregator |

## Pipeline Completo

```
Input → G0 (Intent Detection) → GR (Routing)
  → 7 estágios de auditoria (36 agentes)
  → GE (Cross-MCP Validation)
  → GF (Aggregation)
  → Output: artigo corrigido + parecer 100/100
```

## Arquitetura em Camadas

```
┌──────────────────────────────────────┐
│ OUTPUT LAYER                         │
│ [Formatter] [Compliance] [Score]     │
├──────────────────────────────────────┤
│ AGGREGATION LAYER                    │
│ [Result Aggregator] [Synthesizer]    │
├──────────────────────────────────────┤
│ VALIDATION LAYER                     │
│ [Cross-Validator] [Quality Gate]     │
├──────────────────────────────────────┤
│ ANALYSIS LAYER                       │
│ [Statistical] [Methodology] [Data]   │
├──────────────────────────────────────┤
│ EXECUTION LAYER                      │
│ [Parallel] [Sequential] [Hybrid]     │
├──────────────────────────────────────┤
│ ROUTING LAYER                        │
│ [Skill Matcher] [Agent Selector]     │
├──────────────────────────────────────┤
│ INPUT LAYER                          │
│ [Intent Parser] [RAG Builder]        │
└──────────────────────────────────────┘
```

> **Fonte:** `github.com/MarceloClaro/maswos-v5-nexus` / `ARQUITETURA_TRANSFORMER_AUDITORIA.md` 🟢
