<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Dispatcher MCP: Orquestração Inteligente de Tarefas

## Visão Geral

O **Dispatcher MCP** é o componente central que orquestra a distribuição de tarefas para MCPs especializados, levando em conta:
- Capacidades requeridas
- Disponibilidade de MCPs
- Carga de trabalho
- Prioridade de tarefas
- Alinhamento com especialização de agentes

## Arquitetura do Dispatcher

```
┌──────────────────────────────────┐
│  Agente (A1-A8)                  │
│  Cria tarefa com requisitos      │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│  Task Descriptor                 │
│  - ID, phase, agent_id           │
│  - required_capabilities         │
│  - priority, dependencies        │
│  - estimated_duration            │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│  MCP Router (Intelligent)        │
│  1. Discover capable MCPs        │
│  2. Score each candidate         │
│  3. Select best match            │
│  4. Determine sync barrier need  │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│  Routing Decision                │
│  - mcp_server_id                 │
│  - confidence score              │
│  - alternatives                  │
│  - sync_barrier_required         │
└────────────┬─────────────────────┘
             │
┌────────────▼─────────────────────┐
│  MCP Server                      │
│  Executa operação                │
│  Retorna resultado               │
└──────────────────────────────────┘
```

## Fases de Roteamento

### Fase 1: Descoberta de Capacidades (Capability Discovery)

O dispatcher consulta todos os MCPs registrados para identificar quais podem executar a tarefa.

```python
task.required_capabilities = [FILESYSTEM, CODE_EXECUTION]

capable_mcps = [
    mcp for mcp in registry.all_mcps()
    if mcp.can_handle(task.required_capabilities)
]
# Resultado: [MCP-A4, MCP-A6, MCP-Custom]
```

**Critérios:**
- MCP deve ter TODAS as capacidades requeridas
- MCP deve estar saudável (health_score > 0.5)
- MCP deve ter capacidade disponível (load < max)

### Fase 2: Scoring Multi-Critério (Multi-Criteria Scoring)

Cada MCP capaz recebe um score baseado em múltiplos fatores.

```
Score = (
    0.40 * health_score +
    0.30 * load_factor +
    0.20 * specialization_alignment +
    0.10 * priority_boost
)
```

#### Health Score (40%)
Indicador de confiabilidade e disponibilidade.

```python
health_score = (
    0.6 * uptime_percentage +
    0.3 * success_rate +
    0.1 * response_time_factor
)
```

**Exemplo:**
- MCP-A4: uptime 99%, success 95%, response 100ms → health = 0.94
- MCP-A6: uptime 95%, success 90%, response 200ms → health = 0.82

#### Load Factor (30%)
Capacidade de processamento disponível.

```python
load_factor = 1.0 - (current_load / max_concurrent_tasks)
```

**Exemplo:**
- MCP-A4: 2/5 tasks → load_factor = 0.6
- MCP-A6: 8/10 tasks → load_factor = 0.2

#### Specialization Alignment (20%)
Alinhamento entre papel do agente e especialização do MCP.

```python
if agent_role in mcp.specialization_tags:
    alignment = 0.2  # Full match
else:
    alignment = 0.1  # Fallback
```

**Exemplo:**
- A4 (Feed-Forward) → MCP-A4 (Code Execution): alignment = 0.2
- A4 (Feed-Forward) → MCP-A1 (Filesystem): alignment = 0.1

#### Priority Boost (10%)
Boost baseado na prioridade da tarefa.

```python
priority_boost = (task.priority / 5.0) * 0.10
```

**Exemplo:**
- Priority 1 (low): boost = 0.02
- Priority 5 (critical): boost = 0.10

### Fase 3: Seleção do Melhor Candidato (Best Selection)

Seleciona MCP com maior score. Em caso de empate, usa critério de desempate.

```python
scores = [(mcp, score) for mcp, score in scores]
scores.sort(key=lambda x: x[1], reverse=True)

best_mcp = scores[0][0]
confidence = scores[0][1]
alternatives = [s[0] for s in scores[1:3]]  # Top 2 alternatives
```

**Critério de Desempate:**
1. Health score mais alto
2. Menor latência histórica
3. Menor número de erros recentes

### Fase 4: Determinação de Sync Barrier (Barrier Decision)

Decide se a tarefa requer sincronização granular.

```python
sync_barrier_needed = (
    len(task.dependencies) > 0 or  # Tem dependências
    task.priority >= 4 or           # Crítica
    MCPCapability.DATABASE in task.required_capabilities  # State-changing
)
```

## Padrões de Roteamento

### Padrão 1: Request-Response Simples
```
Tarefa: Ler arquivo de requisitos
├─ Capacidades: [FILESYSTEM]
├─ Prioridade: 2
├─ Roteado para: MCP-Filesystem
└─ Sync barrier: NÃO
```

### Padrão 2: Tarefa Crítica com Fallback
```
Tarefa: Gerar código crítico
├─ Capacidades: [CODE_EXECUTION, LLM_INFERENCE]
├─ Prioridade: 5
├─ Roteado para: MCP-A4 (score 0.92)
├─ Alternativas: MCP-A6 (0.85), MCP-Custom (0.78)
└─ Sync barrier: SIM (consenso obrigatório)
```

### Padrão 3: Tarefa com Dependências
```
Tarefa: Validar código gerado
├─ Dependências: [op-feed-forward-001]
├─ Capacidades: [CODE_EXECUTION]
├─ Roteado para: MCP-A6
└─ Sync barrier: SIM (aguarda prerequisito)
```

### Padrão 4: Batch Processing
```
Tarefas: [test_1, test_2, test_3]
├─ Roteadas para: MCP-A6 (paralelo)
├─ Load balancing: Distribuir entre 2 instâncias
└─ Sync barrier: SIM (aguarda todas completarem)
```

## Estratégias de Fallback

Se o MCP selecionado falhar, o dispatcher ativa fallback automático.

### Nível 1: Retry no Mesmo MCP
```
Tentativa 1: MCP-A4 → TIMEOUT
  └─ Retry com timeout aumentado (2x)
```

### Nível 2: Tentar Alternativa
```
Tentativa 2: MCP-A4 → ERRO
  └─ Tentar MCP-A6 (alternativa)
```

### Nível 3: Fallback Genérico
```
Tentativa 3: MCP-A6 → ERRO
  └─ Tentar MCP-Custom (genérico)
```

### Nível 4: Degradação
```
Tentativa 4: Todos falharam
  └─ Executar localmente (sem MCP)
     ou marcar como FAILED
```

## Métricas de Roteamento

### Por MCP
```json
{
  "mcp_id": "mcp-a4-1",
  "tasks_routed": 1250,
  "success_rate": 0.98,
  "avg_latency_ms": 245,
  "avg_confidence": 0.87,
  "health_score": 0.94,
  "current_load": 3,
  "max_concurrent": 5
}
```

### Por Agente
```json
{
  "agent_id": "A4",
  "tasks_created": 450,
  "avg_routing_confidence": 0.89,
  "preferred_mcps": ["mcp-a4-1", "mcp-a6-1"],
  "fallback_rate": 0.02
}
```

### Por Tarefa
```json
{
  "task_id": "task-001",
  "phase": "Feed-Forward",
  "routed_to": "mcp-a4-1",
  "confidence": 0.92,
  "alternatives": ["mcp-a6-1", "mcp-custom-1"],
  "sync_barrier": true,
  "execution_time_ms": 234,
  "success": true
}
```

## Otimizações Avançadas

### 1. **Predictive Routing**
Usa histórico para prever qual MCP será melhor.

```python
# Baseado em padrões históricos
if task.type == "code_generation":
    best_mcp = predict_best_mcp(task)
```

### 2. **Load Balancing Inteligente**
Distribui carga entre múltiplas instâncias de MCP.

```python
if mcp.current_load > 0.7 * mcp.max_concurrent:
    alternative_instance = find_less_loaded_instance(mcp.type)
```

### 3. **Affinity Scheduling**
Mantém tarefas relacionadas no mesmo MCP para cache.

```python
if task.phase == previous_task.phase:
    prefer_same_mcp(previous_task.mcp_id)
```

### 4. **Adaptive Scoring**
Ajusta pesos de scoring baseado em performance histórica.

```python
if mcp.recent_errors > threshold:
    reduce_health_score_weight()
```

## Integração com TMA Platform

### Dashboard: Aba "Dispatcher"
```
┌─────────────────────────────────┐
│ MCP DISPATCHER METRICS          │
├─────────────────────────────────┤
│ Total Routes: 12,450            │
│ Avg Confidence: 0.89            │
│ Fallback Rate: 1.2%             │
│                                 │
│ Top MCPs:                       │
│ • MCP-A4: 3,200 rotas (0.94)   │
│ • MCP-A6: 2,800 rotas (0.91)   │
│ • MCP-Custom: 1,500 rotas (0.85)│
└─────────────────────────────────┘
```

### Logs: Routing Decisions
```json
{
  "timestamp": "2026-04-14T15:30:00Z",
  "task_id": "task-001",
  "phase": "Feed-Forward",
  "agent_id": "A4",
  "required_capabilities": ["CODE_EXECUTION", "FILESYSTEM"],
  "routed_to": "mcp-a4-1",
  "confidence": 0.92,
  "rationale": "Selected mcp-a4-1 (score: 0.92) for Feed-Forward phase. Health: 94%, Load: 3/5. Margin over next option: 0.07.",
  "alternatives": ["mcp-a6-1", "mcp-custom-1"],
  "sync_barrier_required": true
}
```

## Referências
- MCP Router Script: `scripts/mcp_router.py`
- MCP Architecture: `references/arquitetura_mcp.md`
- Granular Sync: `references/evolucao_granular.md`
