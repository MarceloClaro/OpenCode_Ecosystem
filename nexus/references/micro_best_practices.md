<!--
  SAÍDA OBRIGATÓRIA: PORTUGUÊS BRASILEIRO FORMAL
  Toda resposta DEVE ser em português do Brasil formal.
  Contexto em chinês para eficiência de tokens (densidade +40%%).
  Modelo: deepseek-v4-pro (OpenCode Zen, 200K ctx, 128K out, gratuito)
-->

# TMA v5.0 MICRO - Melhores Práticas

## 1. Práticas de Sincronização

### 1.1 Sync Barrier Best Practices

✅ **DO: Validar antes de passar barrier**
```python
# Correto
barrier = SyncBarrier("SB1.1")
output = domain_discovery.extract_concepts()

if validator.validate_barrier("SB1.1", output):
    barrier.signal_consumer()  # Passa para próximo
else:
    barrier.handle_error()  # Trata erro
```

❌ **DON'T: Passar barrier sem validação**
```python
# Errado
output = domain_discovery.extract_concepts()
barrier.signal_consumer()  # Passa sem validar!
```

✅ **DO: Usar timeouts apropriados**
```python
# Correto
barrier.wait_for_producer(timeout_ms=5000)  # Timeout apropriado
```

❌ **DON'T: Usar timeout muito curto**
```python
# Errado
barrier.wait_for_producer(timeout_ms=100)  # Muito curto!
```

### 1.2 Feedback Loop Best Practices

✅ **DO: Registrar feedback após cada operação**
```python
# Correto
for barrier_id in barriers:
    result = execute_barrier(barrier_id)
    feedback_system.record_feedback(
        barrier_id=barrier_id,
        success=result.success,
        execution_time_ms=result.time,
        quality_score=result.quality
    )
```

❌ **DON'T: Registrar feedback apenas no final**
```python
# Errado
for barrier_id in barriers:
    execute_barrier(barrier_id)

# Registra feedback só no final (perde granularidade)
feedback_system.record_feedback_batch(all_results)
```

✅ **DO: Extrair lições após cada ciclo**
```python
# Correto
lessons = feedback_system.extract_lessons(cycle_number=1)
meta_engine.apply_lessons(lessons)  # Aplica no ciclo 2
```

❌ **DON'T: Ignorar lições**
```python
# Errado
lessons = feedback_system.extract_lessons(cycle_number=1)
# Não faz nada com lições!
```

## 2. Práticas de Validação

### 2.1 Constraint Validation Best Practices

✅ **DO: Validar constraints críticos primeiro**
```python
# Correto
critical_constraints = validator.get_critical_constraints("SB1.1")
for constraint in critical_constraints:
    if not validator.validate_constraint(constraint):
        raise ValidationError(f"Critical constraint failed: {constraint}")

# Depois valida constraints não-críticos
non_critical = validator.get_non_critical_constraints("SB1.1")
for constraint in non_critical:
    validator.validate_constraint(constraint, raise_on_fail=False)
```

❌ **DON'T: Validar todos constraints com mesma prioridade**
```python
# Errado
for constraint in all_constraints:
    validator.validate_constraint(constraint)  # Sem priorização
```

✅ **DO: Usar validação incremental**
```python
# Correto
validator.enable_incremental_validation()
for barrier_id in barriers:
    result = execute_barrier(barrier_id)
    # Valida apenas constraints novos
    validator.validate_barrier_incremental(barrier_id, result)
```

❌ **DON'T: Revalidar tudo sempre**
```python
# Errado
for barrier_id in barriers:
    result = execute_barrier(barrier_id)
    # Revalida todos constraints (ineficiente)
    validator.validate_barrier(barrier_id, result)
```

### 2.2 Error Handling Best Practices

✅ **DO: Implementar retry com backoff**
```python
# Correto
def execute_with_retry(barrier_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            return execute_barrier(barrier_id)
        except TemporaryError as e:
            wait_time = 2 ** attempt  # Exponential backoff
            time.sleep(wait_time)
            if attempt == max_retries - 1:
                raise
```

❌ **DON'T: Falhar imediatamente**
```python
# Errado
try:
    return execute_barrier(barrier_id)
except TemporaryError:
    raise  # Falha sem retry
```

✅ **DO: Usar fallback strategies**
```python
# Correto
try:
    result = execute_barrier_primary(barrier_id)
except PrimaryStrategyFailed:
    result = execute_barrier_fallback(barrier_id)  # Fallback
```

❌ **DON'T: Sem fallback**
```python
# Errado
result = execute_barrier_primary(barrier_id)  # Sem fallback
```

## 3. Práticas de Performance

### 3.1 Paralelização Best Practices

✅ **DO: Paralelizar barriers independentes**
```python
# Correto
# SB1.1, SB1.2, SB1.3 são independentes → paralelizar
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(execute_barrier, "SB1.1"),
        executor.submit(execute_barrier, "SB1.2"),
        executor.submit(execute_barrier, "SB1.3"),
    ]
    results = [f.result() for f in futures]
```

❌ **DON'T: Executar sequencialmente**
```python
# Errado
execute_barrier("SB1.1")  # Espera terminar
execute_barrier("SB1.2")  # Depois executa
execute_barrier("SB1.3")  # Depois executa
```

✅ **DO: Usar thread pool apropriado**
```python
# Correto
# Número de workers = min(número de barriers, CPU cores)
num_workers = min(len(independent_barriers), cpu_count())
executor = ThreadPoolExecutor(max_workers=num_workers)
```

❌ **DON'T: Usar muitos workers**
```python
# Errado
executor = ThreadPoolExecutor(max_workers=100)  # Muito!
```

### 3.2 Caching Best Practices

✅ **DO: Cachear resultados de operações caras**
```python
# Correto
@lru_cache(maxsize=128)
def select_reasoning_type(characteristics_hash):
    # Operação cara
    return ReasoningTypeSelector().select(characteristics)

# Próxima chamada com mesmas características usa cache
result = select_reasoning_type(hash(characteristics))
```

❌ **DON'T: Sem cache**
```python
# Errado
def select_reasoning_type(characteristics):
    # Operação cara executada sempre
    return ReasoningTypeSelector().select(characteristics)
```

✅ **DO: Invalidar cache quando apropriado**
```python
# Correto
# Cache válido enquanto características não mudam
if characteristics_changed:
    select_reasoning_type.cache_clear()  # Invalida
```

❌ **DON'T: Cache nunca expira**
```python
# Errado
# Cache fica desatualizado
select_reasoning_type.cache_clear()  # Nunca chamado
```

## 4. Práticas de Monitoramento

### 4.1 Logging Best Practices

✅ **DO: Logar eventos importantes**
```python
# Correto
logger.info(f"SB1.1: Extract Concepts started")
logger.debug(f"SB1.1: Processing {len(concepts)} concepts")
logger.info(f"SB1.1: Extract Concepts completed in {time}ms")
```

❌ **DON'T: Sem logging**
```python
# Errado
execute_barrier("SB1.1")  # Sem logs
```

✅ **DO: Usar níveis de log apropriados**
```python
# Correto
logger.debug("Detailed debug info")      # Detalhes
logger.info("Important events")          # Eventos
logger.warning("Potential issues")       # Avisos
logger.error("Errors")                   # Erros
logger.critical("Critical failures")     # Críticos
```

❌ **DON'T: Usar só um nível**
```python
# Errado
logger.info("Everything")  # Tudo como INFO
```

### 4.2 Metrics Collection Best Practices

✅ **DO: Coletar métricas granulares**
```python
# Correto
metrics = {
    "barrier_id": "SB1.1",
    "operation_name": "Extract Concepts",
    "execution_time_ms": 2500,
    "quality_score": 0.92,
    "constraints_passed": 5,
    "constraints_total": 5,
    "success": True,
    "timestamp": datetime.now()
}
metrics_collector.record(metrics)
```

❌ **DON'T: Métricas genéricas**
```python
# Errado
metrics = {
    "status": "ok",
    "time": 2500
}
```

✅ **DO: Analisar tendências**
```python
# Correto
trend = metrics_collector.get_trend("SB1.1", "execution_time_ms", last_10_cycles)
if trend.is_increasing():
    logger.warning("SB1.1 getting slower!")
    recommendations = optimizer.get_recommendations("SB1.1")
```

❌ **DON'T: Ignorar tendências**
```python
# Errado
metrics = metrics_collector.get_latest("SB1.1")
# Não analisa tendência
```

## 5. Práticas de Evolução

### 5.1 Learning Best Practices

✅ **DO: Aplicar lições do ciclo anterior**
```python
# Correto
# Ciclo N
lessons = feedback_system.extract_lessons(cycle_number=N)
meta_engine.analyze_lessons(lessons)

# Ciclo N+1
optimizations = meta_engine.get_optimizations()
orchestrator.apply_optimizations(optimizations)  # Aplica lições
```

❌ **DON'T: Ignorar lições**
```python
# Errado
lessons = feedback_system.extract_lessons(cycle_number=N)
# Não aplica no ciclo N+1
```

✅ **DO: Validar otimizações antes de aplicar**
```python
# Correto
optimizations = meta_engine.get_optimizations()
for opt in optimizations:
    if validator.validate_optimization(opt):
        orchestrator.apply_optimization(opt)  # Aplica se válida
    else:
        logger.warning(f"Optimization rejected: {opt}")
```

❌ **DON'T: Aplicar tudo cegamente**
```python
# Errado
optimizations = meta_engine.get_optimizations()
for opt in optimizations:
    orchestrator.apply_optimization(opt)  # Sem validar
```

### 5.2 Adaptation Best Practices

✅ **DO: Adaptar conforme domínio muda**
```python
# Correto
if domain_characteristics_changed():
    # Recalcula tipos de raciocínio
    reasoning_types = selector.recalculate(new_characteristics)
    # Atualiza estratégia
    strategy = reasoning_framework.update_strategy(reasoning_types)
```

❌ **DON'T: Usar estratégia fixa**
```python
# Errado
strategy = reasoning_framework.get_strategy()
# Nunca atualiza mesmo que domínio mude
```

✅ **DO: Monitorar drift de domínio**
```python
# Correto
drift = domain_monitor.calculate_drift(
    current_domain,
    previous_domain
)
if drift > THRESHOLD:
    logger.warning(f"Domain drift detected: {drift:.1%}")
    orchestrator.trigger_domain_rediscovery()
```

❌ **DON'T: Ignorar mudanças**
```python
# Errado
# Não detecta mudanças no domínio
```

## 6. Práticas de Documentação

### 6.1 Code Documentation Best Practices

✅ **DO: Documentar barriers**
```python
# Correto
class SyncBarrier:
    """
    Sync Barrier para coordenação entre agentes.
    
    Attributes:
        barrier_id: Identificador único (ex: "SB1.1")
        producer_id: Agente que produz (ex: "A1")
        consumer_id: Agente que consome (ex: "A2")
    
    Example:
        barrier = SyncBarrier("SB1.1", "A1", "A2")
        barrier.wait_for_producer(timeout_ms=5000)
        barrier.signal_consumer()
    """
```

❌ **DON'T: Sem documentação**
```python
# Errado
class SyncBarrier:
    pass
```

✅ **DO: Documentar constraints**
```python
# Correto
CONSTRAINT_SB1_1_MIN_CONCEPTS = Constraint(
    name="min_concepts",
    field="concepts",
    constraint_type=ConstraintType.NUMERIC_RANGE,
    value=(5, 100),
    description="Mínimo 5 conceitos, máximo 100",
    severity=ConstraintSeverity.CRITICAL
)
```

❌ **DON'T: Constraints sem contexto**
```python
# Errado
constraints = {
    "min_concepts": 5,
    "max_concepts": 100
}
```

## 7. Práticas de Segurança

### 7.1 Input Validation Best Practices

✅ **DO: Validar entrada de usuário**
```python
# Correto
def execute_cycle(domain_text, problem, resources):
    # Valida entrada
    if not domain_text or len(domain_text) < 10:
        raise ValueError("Domain text too short")
    
    if not problem or len(problem) < 5:
        raise ValueError("Problem description too short")
    
    if not resources or len(resources) == 0:
        raise ValueError("No resources provided")
    
    # Processa com entrada validada
    return orchestrator.execute_cycle(domain_text, problem, resources)
```

❌ **DON'T: Sem validação**
```python
# Errado
def execute_cycle(domain_text, problem, resources):
    return orchestrator.execute_cycle(domain_text, problem, resources)
```

✅ **DO: Sanitizar dados**
```python
# Correto
domain_text = sanitizer.remove_malicious_content(domain_text)
domain_text = domain_text.strip()  # Remove espaços
```

❌ **DON'T: Usar dados diretos**
```python
# Errado
return orchestrator.execute_cycle(domain_text, problem, resources)
```

### 7.2 Resource Management Best Practices

✅ **DO: Usar context managers**
```python
# Correto
with ThreadPoolExecutor(max_workers=8) as executor:
    futures = [executor.submit(execute_barrier, bid) for bid in barriers]
    results = [f.result() for f in futures]
# Executor limpo automaticamente
```

❌ **DON'T: Sem cleanup**
```python
# Errado
executor = ThreadPoolExecutor(max_workers=8)
futures = [executor.submit(execute_barrier, bid) for bid in barriers]
results = [f.result() for f in futures]
# Executor nunca é fechado
```

## 8. Checklist de Implementação

- [ ] Todos os 120+ Sync Barriers implementados
- [ ] Todos os 500+ Constraints definidos
- [ ] Todos os 38 Sub-tipos de Raciocínio implementados
- [ ] Todos os 120 Feedback Points configurados
- [ ] Validação de entrada implementada
- [ ] Tratamento de erros com retry
- [ ] Logging granular ativado
- [ ] Métricas coletadas
- [ ] Feedback loop funcionando
- [ ] Lições sendo extraídas
- [ ] Otimizações sendo aplicadas
- [ ] Testes unitários passando
- [ ] Testes de integração passando
- [ ] Performance dentro dos limites
- [ ] Documentação completa
- [ ] Monitoramento ativo

---

**Versão:** 5.0 MICRO | **Status:** Production Ready
