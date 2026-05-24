---
name: agent-observability-monitor
description: "Monitoramento e observabilidade de agentes no ecossistema OpenCode. Health checks, tracking de performance por ferramenta, metricas de sessao, thresholds de alerta. Inspirado em monte-carlo-data/mc-agent-toolkit."
---

# Agent Observability Monitor

## Visao Geral

Sistema de observabilidade para agentes do ecossistema OpenCode. Proporciona visibilidade sobre saude, performance e comportamento dos agentes em tempo real, com metricas por ferramenta, sessao e componente.

## Componentes Monitorados

| Tipo | Quantidade | Metrica Principal |
|------|-----------|-------------------|
| MCPs | 17 ativos | Latencia + taxa de erro |
| Skills | 76 em 12 categorias | Taxa de ativacao + utilidade |
| Agentes | 118+ | Sucesso por tarefa |
| Plugins | 2 (ecosystem-sync, manus-evolve) | Estabilidade + score |
| Comandos | 14 | Frequencia de uso |

## Thresholds de Saude

| Nivel | Score | Acao |
|-------|-------|------|
| **Healthy** | >= 95 | Normal - apenas logging |
| **Attention** | >= 85 | Log Warning, verificar componente |
| **Alert** | >= 70 | Notificar, agendar reparo |
| **Critical** | < 70 | Intervencao imediata |

## Metricas por Sessao

Toda sessao deve registrar:
- `session_id`: UUID da sessao
- `agent`: Nome do agente principal
- `tools_used`: Array de objetos com tool, calls, success_rate, avg_latency_ms, errors
- `total_calls`: Numeros total de chamadas de ferramenta
- `total_errors`: Total de erros
- `error_rate`: Proporcao de erros
- `health_score`: Score composto (0-100)
- `duration_minutes`: Duracao da sessao

## Health Check Pipeline

### 1. Coleta
- Capturar metricas de cada chamada de ferramenta (tool.execute.after)
- Registrar latencia, sucesso/falha, tokens usados
- Agregar por sessao e por agente

### 2. Analise
- Calcular health score por componente: `score = (successos / total) * 100 - penalidade_por_latencia`
- Aplicar thresholds para classificacao
- Detectar anomalias (desvio > 2 sigma da media historica)

### 3. Acao
- Componentes Healthy: apenas logging
- Attention: marcar para revisao no proximo sync
- Alert: notificar, registrar em memory.json
- Critical: tentar auto-healing (reiniciar MCP, recarregar skill)

## Comandos de Observabilidade

```
/health          - Relatorio de saude do ecossistema
/health --agent  - Saude de um agente especifico
/health --mcp    - Saude dos MCPs
/metrics         - Metricas detalhadas da sessao
/trace           - Trace de chamadas de ferramentas
```

## Integracao com Memory Graph

Cada sessao de agente registra:
- **Entidade**: `agent:<nome>` com observacoes de performance
- **Relacao**: `agent:<nome> -> tool:<nome>` com metrica de sucesso
- **Entidade**: `session:<uuid>` com observacoes de health score

## Troubleshooting

| Sintoma | Causa Provavel | Acao |
|---------|---------------|------|
| Health score caindo | MCP offline ou lento | ecosystem-sync para diagnosticar |
| Skill nao ativa | Description nao corresponde ao prompt | Ajustar palavras-chave no frontmatter |
| Erro frequente em ferramenta | API rate limit ou timeout | Verificar logs, ajustar timeout |
| Agente looping | Contexto estourando | Reduzir skills carregadas simultaneas |
