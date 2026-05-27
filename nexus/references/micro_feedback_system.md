<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# TMA v5.0 MICRO - Sistema de Feedback Granular (120 Feedback Points)

## 1. Visão Geral do Feedback MICRO

O sistema de feedback MICRO coleta informações **após cada operação atômica** para:

- ✅ Validar sucesso/falha
- ✅ Medir qualidade
- ✅ Extrair lições
- ✅ Alimentar evolução
- ✅ Otimizar próximos ciclos

**Total de Feedback Points:** 120 (um por operação atômica)

## 2. Tipos de Feedback

| Tipo | Descrição | Ação |
|------|-----------|------|
| SUCCESS | Operação completou com sucesso | Confirma padrão |
| PARTIAL_SUCCESS | Operação completou parcialmente | Identifica limitação |
| FAILURE | Operação falhou | Identifica problema |
| WARNING | Operação completou com aviso | Alerta para otimização |
| OPTIMIZATION | Operação completou mas lenta | Detecta gargalo |

## 3. Estrutura de Feedback

```python
@dataclass
class OperationFeedback:
    # Identificação
    barrier_id: str              # SB1.1, SB2.5, etc
    operation_name: str          # "Extract Concepts"
    timestamp: datetime          # Quando executou
    
    # Resultado
    success: bool                # Sucesso/falha
    feedback_type: str           # SUCCESS, FAILURE, etc
    
    # Métricas
    execution_time_ms: float     # Tempo de execução
    quality_score: float         # 0-1 qualidade
    confidence: float            # 0-1 confiança
    
    # Validação
    constraints_passed: int      # Quantos constraints passaram
    constraints_total: int       # Total de constraints
    
    # Lições
    lessons_learned: List[str]   # Lições extraídas
    recommendations: List[str]   # Recomendações
    
    # Evolução
    improvement_potential: float # 0-1 potencial de melhoria
    next_optimization: str       # Próxima otimização
```

## 4. Feedback por Camada

### Camada 1: Discovery (15 Feedback Points)

#### SB1.1: Extract Concepts

```yaml
Feedback Point 1.1:
  Operation: Extract Concepts
  Success Criteria:
    - Conceitos extraídos: 5-100
    - Qualidade média: ≥ 0.7
    - Tempo: ≤ 5000ms
  
  Feedback Types:
    SUCCESS:
      - Lição: "Extração rápida e precisa"
      - Recomendação: "Usar mesma estratégia para domínios similares"
      - Potencial: "Otimizar para 2000ms"
    
    FAILURE:
      - Lição: "Extração falhou por entrada ruim"
      - Recomendação: "Validar entrada antes"
      - Potencial: "Adicionar pré-processamento"
    
    OPTIMIZATION:
      - Lição: "Extração lenta (4500ms > 3000ms)"
      - Recomendação: "Paralelizar processamento"
      - Potencial: "Reduzir para 2000ms"
```

#### SB1.2-1.15: Similar Pattern (14 Feedback Points)

### Camada 2: Reasoning (20 Feedback Points)

#### SB2.1-2.4: Analyze Characteristics (4 Feedback Points)

```yaml
Feedback Point 2.1:
  Operation: Analyze Domain Characteristics
  Success Criteria:
    - Características extraídas: ≥ 5
    - Cobertura: ≥ 80%
    - Tempo: ≤ 2000ms
  
  Feedback Types:
    SUCCESS:
      - Lição: "Análise completa e rápida"
      - Recomendação: "Usar para análises futuras"
      - Potencial: "Expandir para 10 características"
    
    PARTIAL_SUCCESS:
      - Lição: "Análise incompleta (3/5 características)"
      - Recomendação: "Adicionar mais analisadores"
      - Potencial: "Atingir 100% de cobertura"
```

#### SB2.5-2.8: Select Reasoning Type (4 Feedback Points)

```yaml
Feedback Point 2.5:
  Operation: Select Reasoning Type
  Success Criteria:
    - Tipo selecionado: válido
    - Score: ≥ 0.8
    - Tempo: ≤ 500ms
  
  Feedback Types:
    SUCCESS:
      - Lição: "Seleção precisa (score 0.95)"
      - Recomendação: "Usar mesmo algoritmo para problemas similares"
      - Potencial: "Atingir score 0.99"
    
    FAILURE:
      - Lição: "Seleção falhou (score 0.45)"
      - Recomendação: "Revisar características do domínio"
      - Potencial: "Adicionar novo tipo de raciocínio"
```

#### SB2.9-2.20: Similar Pattern (12 Feedback Points)

### Camada 3: Organization (25 Feedback Points)

#### SB3.1-3.5: Discover MCPs (5 Feedback Points)

```yaml
Feedback Point 3.1:
  Operation: Discover MCPs
  Success Criteria:
    - MCPs descobertos: ≥ 1
    - Saúde média: ≥ 0.8
    - Tempo: ≤ 3000ms
  
  Feedback Types:
    SUCCESS:
      - Lição: "Descoberta completa (12 MCPs)"
      - Recomendação: "Manter registro para próximas buscas"
      - Potencial: "Descobrir 20+ MCPs"
    
    WARNING:
      - Lição: "Poucos MCPs saudáveis (2/12)"
      - Recomendação: "Verificar saúde do sistema"
      - Potencial: "Recuperar MCPs offline"
```

#### SB3.6-3.25: Similar Pattern (20 Feedback Points)

### Camada 4: Specialization (30 Feedback Points)

#### SB4.1-4.10: Analyze Success Patterns (10 Feedback Points)

```yaml
Feedback Point 4.1:
  Operation: Analyze Success Patterns
  Success Criteria:
    - Padrões identificados: ≥ 3
    - Confiança: ≥ 0.75
    - Tempo: ≤ 5000ms
  
  Feedback Types:
    SUCCESS:
      - Lição: "Padrão identificado: Entrada > Qualidade"
      - Recomendação: "Priorizar qualidade de entrada"
      - Potencial: "Identificar 10+ padrões"
    
    OPTIMIZATION:
      - Lição: "Análise lenta (4800ms)"
      - Recomendação: "Usar cache para padrões frequentes"
      - Potencial: "Reduzir para 2000ms"
```

#### SB4.11-4.30: Similar Pattern (20 Feedback Points)

### Camada 5: Healing (30 Feedback Points)

#### SB5.1-5.10: Monitor Health (10 Feedback Points)

```yaml
Feedback Point 5.1:
  Operation: Monitor Health
  Success Criteria:
    - Métricas coletadas: ≥ 10
    - Anomalias detectadas: ≥ 1
    - Tempo: ≤ 1000ms
  
  Feedback Types:
    SUCCESS:
      - Lição: "Monitoramento completo"
      - Recomendação: "Manter frequência de monitoramento"
      - Potencial: "Expandir para 20 métricas"
    
    WARNING:
      - Lição: "Anomalia detectada: CPU > 80%"
      - Recomendação: "Investigar causa"
      - Potencial: "Implementar auto-scaling"
```

#### SB5.11-5.40: Similar Pattern (20 Feedback Points)

## 5. Extração Automática de Lições

### Algoritmo de Extração

```python
def extract_lessons(feedback: OperationFeedback) -> List[str]:
    lessons = []
    
    # Lição 1: Padrão de Sucesso
    if feedback.success and feedback.quality_score > 0.9:
        lessons.append(
            f"Padrão de sucesso: {feedback.operation_name} "
            f"com qualidade {feedback.quality_score:.2f}"
        )
    
    # Lição 2: Gargalo de Performance
    if feedback.execution_time_ms > EXPECTED_TIME * 1.5:
        lessons.append(
            f"Gargalo: {feedback.operation_name} "
            f"executou em {feedback.execution_time_ms:.0f}ms "
            f"(esperado {EXPECTED_TIME:.0f}ms)"
        )
    
    # Lição 3: Falha Recorrente
    if not feedback.success:
        lessons.append(
            f"Falha recorrente: {feedback.operation_name} "
            f"falhou {feedback.failure_count}x"
        )
    
    # Lição 4: Limitação Descoberta
    if feedback.constraints_passed < feedback.constraints_total:
        lessons.append(
            f"Limitação: {feedback.operation_name} "
            f"passou {feedback.constraints_passed}/"
            f"{feedback.constraints_total} constraints"
        )
    
    # Lição 5: Oportunidade de Otimização
    if feedback.improvement_potential > 0.5:
        lessons.append(
            f"Oportunidade: {feedback.operation_name} "
            f"pode melhorar {feedback.improvement_potential:.0%}"
        )
    
    return lessons
```

## 6. Feedback Loop Evolutivo

### Ciclo de Aprendizado

```
Ciclo N:
  1. SB1.1 executa → Feedback registrado
  2. SB1.2 executa → Feedback registrado
  ...
  120. SB5.40 executa → Feedback registrado
  
  Lições Extraídas:
  - Padrão 1: Entrada > Qualidade
  - Padrão 2: Raciocínio Bayesiano é 20% mais rápido
  - Padrão 3: MCP X falha 5% das vezes
  - Otimização 1: Paralelizar SB1.1
  - Otimização 2: Cachear resultados de SB2.5
  
Ciclo N+1:
  └─ Inicia com otimizações do Ciclo N
  └─ Esperado: Melhoria de 10-15%
  └─ Feedback registrado para Ciclo N+2
```

## 7. Métricas de Feedback

### Por Operação

```python
@dataclass
class OperationMetrics:
    barrier_id: str
    operation_name: str
    
    # Execução
    total_executions: int
    successful: int
    failed: int
    partial_success: int
    
    # Performance
    avg_execution_time_ms: float
    min_execution_time_ms: float
    max_execution_time_ms: float
    
    # Qualidade
    avg_quality_score: float
    avg_confidence: float
    
    # Feedback
    success_rate: float
    failure_rate: float
    optimization_opportunities: int
    
    # Evolução
    lessons_extracted: int
    improvements_applied: int
    improvement_trend: float  # % melhoria por ciclo
```

### Agregadas por Camada

```python
@dataclass
class LayerMetrics:
    layer_name: str
    
    # Operações
    total_barriers: int
    total_operations: int
    
    # Sucesso
    total_successes: int
    total_failures: int
    success_rate: float
    
    # Performance
    avg_execution_time_ms: float
    total_time_ms: float
    
    # Feedback
    total_feedback_points: int
    total_lessons_extracted: int
    
    # Evolução
    avg_improvement_trend: float
    total_improvements_applied: int
```

## 8. Relatório de Feedback

### Exemplo: Ciclo N

```
╔════════════════════════════════════════════════════════════════╗
║           FEEDBACK REPORT - CYCLE N                           ║
╚════════════════════════════════════════════════════════════════╝

Total Feedback Points: 120/120 ✓
Total Executions: 120
Successful: 118 (98.3%)
Failed: 2 (1.7%)
Partial Success: 0 (0%)

Performance:
  Total Time: 45.2s
  Avg per Operation: 377ms
  Fastest: SB2.6 (45ms)
  Slowest: SB5.15 (2.3s)

Quality:
  Avg Quality Score: 0.92
  Avg Confidence: 0.88
  Constraints Passed: 4,850/5,000 (97%)

Lessons Learned:
  1. Padrão: Entrada > Qualidade (confidence 0.95)
  2. Otimização: Paralelizar SB1.1 (potencial 30%)
  3. Falha: SB3.7 falha com MCP offline (2 ocorrências)
  4. Oportunidade: Cache para SB2.5 (potencial 40%)
  5. Gargalo: SB5.15 lento (2.3s > 1.5s esperado)

Improvements to Apply in Cycle N+1:
  ✓ Paralelizar SB1.1
  ✓ Implementar cache SB2.5
  ✓ Adicionar fallback para MCP offline
  ✓ Otimizar SB5.15

Expected Improvement: +12%
```

## 9. Feedback Loop com A8 (Meta-Learning Engine)

### Integração com A8

```
A6-A7 (Self-Healing)
  ├─ Registra 120 Feedback Points
  ├─ Extrai lições
  └─ Envia para A8
       ↓
A8 (Meta-Learning Engine)
  ├─ Recebe 120 Feedback Points
  ├─ Analisa padrões
  ├─ Gera otimizações
  └─ Envia recomendações para A1
       ↓
A1 (Domain Discovery)
  ├─ Recebe recomendações
  ├─ Atualiza Domain Model
  └─ Próximo ciclo começa com melhorias
```

## 10. Customização de Feedback

### Template para Novo Feedback Point

```yaml
Barrier: SB_X_Y
Operation: "Operation Name"
Feedback Point: X.Y
Success Criteria:
  - Critério 1
  - Critério 2
  - Critério 3

Feedback Types:
  SUCCESS:
    Lesson: "Lição de sucesso"
    Recommendation: "Recomendação"
    Potential: "Potencial de melhoria"
  
  FAILURE:
    Lesson: "Lição de falha"
    Recommendation: "Recomendação"
    Potential: "Potencial de recuperação"
  
  OPTIMIZATION:
    Lesson: "Lição de otimização"
    Recommendation: "Recomendação"
    Potential: "Potencial de speedup"
```

---

**Versão:** 5.0 MICRO | **Status:** Production Ready | **Total Feedback Points:** 120
