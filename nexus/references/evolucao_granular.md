<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# Evolução Granular: Transformação Contínua de Agentes

## Conceito

**Evolução Granular** permite que agentes mudem de especialização, capacidades e até de forma durante a execução do pipeline, não apenas ao final de um ciclo.

## Tipos de Transformação

### 1. **Especialização (Specialization)**
Agente muda de papel dentro do TMA.

```
A1 (Embedding) → A2 (Attention) → A3 (Consensus)
```

**Quando usar:**
- Agente completou sua fase com sucesso
- Próxima fase precisa de análise adicional
- Fitness score do agente está alto

**Impacto:**
- Fitness score: -10% (penalidade por transição)
- Novas capacidades: Herdadas do novo papel
- Geração: +1

### 2. **Mutação de Capacidade (Capability Mutation)**
Agente ganha, perde ou melhora uma capacidade específica.

```
A4 (Feed-Forward):
  ├─ Enhance: code_generation (1.0 → 1.0)
  ├─ Add: performance_optimization
  └─ Disable: legacy_code_support
```

**Operações:**
- **Enhance**: Aumenta performance_score de 0.1
- **Add**: Nova capacidade com score inicial 0.5
- **Disable**: Marca como inativa (pode ser reativada)
- **Remove**: Deleta capacidade permanentemente

**Impacto no Fitness:**
- Enhance: +5%
- Add: +8%
- Disable: -10%
- Remove: -5%

### 3. **Fusão (Fusion)**
Dois agentes se combinam em um híbrido.

```
A1 (Embedding) + A2 (Attention) → A_hybrid
```

**Estratégias:**
- **Union**: Combina todas as capacidades
- **Intersection**: Mantém apenas capacidades comuns
- **Weighted**: Blend baseado em fitness scores

**Quando usar:**
- Tarefa complexa requer múltiplas perspectivas
- Agentes têm fitness scores similares
- Redução de latência por paralelismo

**Impacto:**
- Novo agente: geração = max(gen1, gen2) + 1
- Fitness: (fitness1 + fitness2) / 2
- Agentes originais: podem ser desativados

### 4. **Divisão (Division)**
Um agente se divide em dois especializados.

```
A4 (Feed-Forward) → A4a (Backend) + A4b (Frontend)
```

**Estratégias:**
- **Balanced**: Divide capacidades 50/50
- **Role-based**: Agrupa por afinidade

**Quando usar:**
- Agente está sobrecarregado
- Tarefa tem dois domínios distintos
- Necessário paralelismo

**Impacto:**
- Cada novo agente: fitness = fitness_original * 0.85
- Geração: +1
- Agente original: desativado

## Ciclo de Evolução

```
┌─────────────────────────────────────────┐
│  Fase 1: Execução                       │
│  Agente executa operação                │
│  Coleta métricas de performance         │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Fase 2: Avaliação                      │
│  Calcula fitness score                  │
│  Identifica gargalos                    │
│  Propõe transformações                  │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Fase 3: Decisão                        │
│  Consenso entre especialistas           │
│  Validação de guardrails                │
│  Aprovação de mutação                   │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Fase 4: Transformação                  │
│  Aplicar metamorfose                    │
│  Criar checkpoint                       │
│  Registrar em git                       │
└────────────┬────────────────────────────┘
             │
┌────────────▼────────────────────────────┐
│  Fase 5: Validação                      │
│  Testar novo agente                     │
│  Comparar com baseline                  │
│  Rollback se necessário                 │
└─────────────────────────────────────────┘
```

## Métricas de Evolução

### Fitness Score
```
fitness = (
    0.3 * success_rate +
    0.25 * speed_factor +
    0.2 * quality_score +
    0.15 * resource_efficiency +
    0.1 * innovation_factor
)
```

### Success Rate
Percentual de operações completadas com sucesso.
```
success_rate = completed_operations / total_operations
```

### Speed Factor
Quanto mais rápido, melhor (normalizado).
```
speed_factor = baseline_time / actual_time
```

### Quality Score
Baseado em testes e revisões.
```
quality_score = (
    test_coverage * 0.4 +
    code_review_score * 0.3 +
    pattern_adherence * 0.3
)
```

### Resource Efficiency
Uso de MCPs e computação.
```
resource_efficiency = baseline_resources / actual_resources
```

### Innovation Factor
Capacidades novas e mutações bem-sucedidas.
```
innovation_factor = (new_capabilities + successful_mutations) / generation
```

## Guardrails de Evolução

### 1. **Limite de Mutação**
Máximo de 3 mutações por ciclo por agente.

```python
if agent.mutation_count >= 3:
    skip_mutation()
```

### 2. **Fitness Floor**
Não permitir transformações que reduzam fitness abaixo de 0.4.

```python
if new_fitness < 0.4:
    reject_transformation()
```

### 3. **Geração Máxima**
Agente não pode evoluir além de geração 20.

```python
if agent.generation >= 20:
    freeze_evolution()
```

### 4. **Rollback Automático**
Se fitness cair >20% após transformação, reverter.

```python
if (old_fitness - new_fitness) / old_fitness > 0.2:
    rollback_transformation()
```

### 5. **Consenso Obrigatório**
Transformações críticas requerem aprovação de 2+ especialistas.

```python
if transformation.is_critical():
    require_consensus(min_votes=2)
```

## Linhagem Genética (Lineage)

Cada agente mantém histórico completo de sua evolução.

```json
{
  "agent_id": "A4_v7",
  "current_role": "Feed-Forward",
  "generation": 7,
  "fitness_score": 0.92,
  "parent_ids": ["A4_v6", "A_hybrid_v3"],
  "transformations": [
    {
      "type": "specialization",
      "from": "A1",
      "to": "A4",
      "generation": 1,
      "fitness_delta": -0.1
    },
    {
      "type": "capability_mutation",
      "operation": "enhance",
      "capability": "code_generation",
      "generation": 3,
      "fitness_delta": +0.05
    },
    {
      "type": "fusion",
      "with": "A_hybrid_v3",
      "generation": 7,
      "fitness_delta": +0.08
    }
  ],
  "genome_hash": "a1b2c3d4e5f6g7h8"
}
```

## Padrões de Evolução Bem-Sucedida

### Padrão 1: **Especialização Progressiva**
```
A1 → A2 → A3 → A4 → A5
(Cada fase, agente se especializa mais)
```

**Resultado:** Fitness cresce de 0.5 → 0.95

### Padrão 2: **Fusão Estratégica**
```
A1 + A2 → A_hybrid (especialista em Embedding+Attention)
```

**Resultado:** Reduz latência em 30%, fitness = 0.88

### Padrão 3: **Divisão para Paralelismo**
```
A4 (sobrecarregado) → A4a (Backend) + A4b (Frontend)
```

**Resultado:** Throughput aumenta 2x, fitness = 0.85 cada

### Padrão 4: **Recuperação de Falha**
```
A6 (fitness 0.3) → Enhance QA → Disable legacy_support → fitness 0.75
```

**Resultado:** Agente recuperado através de mutações direcionadas

## Integração com TMA Platform

### Dashboard: Aba "Evolution"
```
┌─────────────────────────────────┐
│ AGENT METAMORPHOSIS TRACKER     │
├─────────────────────────────────┤
│ A1: Embedding → Attention       │
│     Gen: 3 | Fitness: 0.88 ↑    │
│                                 │
│ A4: Feed-Forward (Stable)       │
│     Gen: 1 | Fitness: 0.92 ─    │
│                                 │
│ A_hybrid: Fusion (A1+A2)        │
│     Gen: 2 | Fitness: 0.85 ↓    │
└─────────────────────────────────┘
```

### Logs: Metamorphosis Events
```json
{
  "timestamp": "2026-04-14T15:30:00Z",
  "event_id": "meta-001",
  "agent_id": "A4",
  "transformation_type": "capability_mutation",
  "operation": "enhance",
  "capability": "code_generation",
  "fitness_delta": +0.05,
  "success": true,
  "rollback_available": true
}
```

## Referências
- Agent Metamorphosis Script: `scripts/agent_metamorphosis.py`
- TMA Pipeline: `references/arquitetura_transformer.md`
- MCP Integration: `references/arquitetura_mcp.md`
