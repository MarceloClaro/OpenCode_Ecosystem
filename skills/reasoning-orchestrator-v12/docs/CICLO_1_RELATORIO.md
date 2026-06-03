# Ciclo 1 — ParallelDispatch Intra-Fase

## Status: ✅ COMPLETO (10/10 testes GREEN)

## Resumo
Implementado o **ParallelDispatch** (ThreadPoolExecutor) para execução paralela de agentes dentro de cada fase do pipeline de 7 fases (F1-F7). O orquestrador `ParallelOrchestrator` coordena as fases sequencialmente enquanto paraleliza os agentes dentro de cada fase.

## Arquivos Criados/Modificados

| Arquivo | Tipo | Descrição |
|---------|------|-----------|
| `agents/__init__.py` | Criado | Módulo v12 |
| `agents/parallel_dispatch.py` | Criado | ParallelDispatch + ParallelResult + PhaseMetrics |
| `agents/orchestrator_v12.py` | Criado | ParallelOrchestrator + SolutionReport + modos |
| `tests/test_parallel_dispatch.py` | Modificado | 10 testes TDD (C1-T1 a C1-T10) |
| `docs/CICLO_1_RELATORIO.md` | Criado | Este relatório |

## Métricas do Ciclo 1

| Métrica | Valor |
|---------|-------|
| Testes escritos | 10 |
| Testes que passaram (GREEN) | 10 |
| Ciclos RED→GREEN | 3 (timeout, agent creation, config) |
| Linhas de código (impl) | ~380 (parallel_dispatch: 200 + orchestrator: 180) |
| Linhas de teste | ~320 |
| Cobertura funcional | 100% dos cenários do Ciclo 1 |

## Testes C1-T1 a C1-T10

| ID | Teste | Descrição | Resultado |
|----|-------|-----------|-----------|
| C1-T1 | `test_parallel_dispatch_exists` | ParallelDispatch importável e instanciável | ✅ |
| C1-T2 | `test_dispatch_parallel_execution` | 3 agentes com tempos [0.2, 0.3, 0.1] executam em < 0.5s | ✅ |
| C1-T3 | `test_all_results_collected` | Todos 3 agentes têm resultados coletados | ✅ |
| C1-T4 | `test_failure_isolation` | Falha em agente A não aborta agente B | ✅ |
| C1-T5 | `test_agent_timeout` | Agente lento (5s) é interrompido em < 3s | ✅ |
| C1-T6 | `test_parallel_metrics_reported` | elapsed_ms > 0 e thread_id int em resultados | ✅ |
| C1-T7 | `test_dependency_validation` | Agente sem pré-requisito tem status=skipped | ✅ |
| C1-T8 | `test_orchestrator_creation` | ParallelOrchestrator com config default | ✅ |
| C1-T9 | `test_orchestrator_solve_returns_report` | solve() retorna SolutionReport com .pci | ✅ |
| C1-T10 | `test_mode_configuration` | Modos Express(1)/Standard(2)/Magnum(4) | ✅ |

## Achados Técnicos

### 1. ThreadPoolExecutor + Timeout
- **Problema**: `with ThreadPoolExecutor(...)` chama `shutdown(wait=True)` no `__exit__`, bloqueando até threads lentas terminarem mesmo após timeout ser acionado.
- **Solução**: Usar `executor.shutdown(wait=False)` manualmente no `finally` para não aguardar threads canceladas.
- **Impacto**: Timeout funcional em 1.0s em vez de 5.0s.

### 2. AbstractReasoningAgent
- **Problema**: `ReasoningAgent` (framework.py v11) é ABC com métodos abstratos `reason()` e `get_dependencies()`, não pode ser instanciado diretamente.
- **Solução**: Criar `_ConcreteOrchestratorAgent` (uso interno) e `_DummyTestAgent` (testes) como subclasses concretas.
- **Impacto**: Factory method `select_agents_for_phase()` funcional.

### 3. Dynamic Class Creation with type()
- **Problema**: `type('Agent', (ReasoningAgent,), {...})()` falha porque `type()` não invoca `__init__` com argumentos posicionais.
- **Solução**: Criar classe concreta separada `_DummyTestAgent` com `__init__` adequado.
- **Impacto**: Testes de paralelismo com sleep configurável passam corretamente.

### 4. Config Dict vs. Namespace
- **Problema**: Testes esperam `orch.config.intra_phase_workers`, implementação usava `config["max_workers"]`.
- **Solução**: Criar `_ConfigNamespace` que expõe dict como atributos via dot notation + adicionar property `pci` como alias para `pci_score`.
- **Impacto**: `orch.config.intra_phase_workers` e `report.pci` funcionam.

## Decisões de Design

| Decisão | Opção | Justificativa |
|---------|-------|---------------|
| Executor lifecycle | `shutdown(wait=False)` manual | `with` bloqueia no timeout |
| Agentes concretos | Classe separada por contexto | Estabilidade vs. monkey-patching |
| Config access | Dot notation (`config.budget`) | Testes exigem dot notation |
| Modos de operação | 4 (Express/Standard/Magnum/Research) | Escalabilidade incremental |
| Número workers | Express=1, Standard=2, Magnum=4, Research=8 | Crescimento linear com modo |

## Próximos Passos

1. **Benchmark C1**: medir speedup real vs v11 sequencial (estimar overhead)
2. **Ciclo 2: Inference-Time Scaling**: implementar `agents/inference_scaler.py` com lei de potência PCI = α·budget^β
3. **Ciclo 3: Verificadores Paralelos**: integrar Cora-Debate V1-V7 como workers paralelos
4. **Ciclo 4: Síntese Multi-Caminho**: ProcessPoolExecutor + 4 métodos de síntese
