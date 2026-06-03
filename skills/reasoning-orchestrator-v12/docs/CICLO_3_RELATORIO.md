# CICLO 3 — Parallel Verifiers (Cora-Debate V1-V7)

**Data:** 2026-05-31  
**Versão:** v1.0.0  
**Arquivos:**
- `agents/parallel_verifiers.py` (438 linhas)
- `tests/test_parallel_verifiers.py` (22 testes)
- `tests/benchmark_c3.py` (benchmark)

---

## 1. Objetivo

Implementar verificadores simbólicos V1-V7 em paralelo sobre os resultados do pipeline de 7 fases, com ConsensusEngine, pesos configuráveis e calibração Platt. Integrar ao ParallelOrchestrator v12 via `solve_with_verification()`.

## 2. Arquitetura Implementada

```
ParallelVerifiers Engine
├── ThreadPoolExecutor (max_workers=4)
│   ├── V1: Dimensional Analysis       (peso 0.15, timeout 15s)
│   ├── V2: Algebraic Verification     (peso 0.20, timeout 15s)
│   ├── V3: Counterexample Search      (peso 0.25, timeout 30s)
│   ├── V4: Statistical Validation     (peso 0.10, timeout 15s)
│   ├── V5: Numerical Precision        (peso 0.10, timeout 15s)
│   ├── V6: ODE/PDE Verification       (peso 0.10, timeout 15s)
│   └── V7: Source Code Verification   (peso 0.10, timeout 30s)
├── ConsensusEngine
│   ├── weighted_score = Σ(p_i·conf_i) / Σ(p_i)
│   ├── Platt: sigmoid(10·(score-0.5))
│   └── threshold = 0.75
└── Retry adaptativo: +50% budget se score < 0.75
```

## 3. Testes TDD (22 testes, 44/44 GREEN)

### Testes C3 Especificados (C3-T1 a C3-T14)

| ID | Nome | Status | Descrição |
|:--:|------|:------:|-----------|
| C3-T1 | verify_parallel_returns_consensus | ✅ | VerificationConsensus retornado |
| C3-T2 | all_verifiers_executed | ✅ | V1-V7 executados com active_verifiers=None |
| C3-T3 | subset_verifiers | ✅ | Subset de verificadores funciona |
| C3-T4 | weighted_score_formula | ✅ | Σ(p_i·conf_i)/Σ(p_i) verificado |
| C3-T5 | consensus_threshold | ✅ | score<0.75 → requires_retry |
| C3-T6 | verifier_timeout | ✅ | Timeout não aborta outros |
| C3-T7 | failure_isolation_verifiers | ✅ | Falha isolada por V |
| C3-T8 | parallel_execution_time | ✅ | < 2s (medido: ~0.3s) |
| C3-T9 | get_supported_domains | ✅ | 7 verificadores, cada um com domínios |
| C3-T10 | verify_single | ✅ | Verificador individual funciona |
| C3-T11 | solve_with_verification | ✅ | Fluxo integrado com orchestrator |
| C3-T12 | retry_on_low_consensus | ✅ | Retry com +50% budget |
| C3-T13 | max_retries_exceeded | ✅ | Exaustão de retries não quebra |
| C3-T14 | platt_calibration | ✅ | Score calibrado ∈ [0,1], monotônico |

### Testes Adicionais de Robustez

| Teste | Status | Descrição |
|-------|:------:|-----------|
| verifier_known_ids | ✅ | 7 IDs V1-V7 conhecidos |
| verifier_weights_sum | ✅ | Σ pesos = 1.0 |
| parallel_faster_than_sequential | ✅ | Paralelo < 3s |
| varied_contexts (×5 parametrizações) | ✅ | Física, Estatística, Código, EDO, Vazio |

## 4. Métricas de Qualidade

| Métrica | Alvo | Obtido |
|---------|:----:|:------:|
| Testes TDD | 14 | 14 |
| Testes totais | 22 | 22 |
| Cobertura (asserts) | 50+ | ~80 |
| Tempo execução V1-V7 | ≤ 2s | ~0.3s |
| Platt calibration | score∈[0,1] | ✅ monotônico |
| Soma pesos | 1.0 | 1.0 ✅ |
| Isolamento falhas | 100% | ✅ |

## 5. Integrações Realizadas

| Componente | Mudança |
|-----------|---------|
| `agents/orchestrator_v12.py` | `_ConfigNamespace` → `ConfigNamespace` (público); `agent_results` adicionado ao `SolutionReport`; `CUR_DIR` adicionado ao sys.path |
| `agents/parallel_dispatch.py` | Floor 0.1ms para `elapsed_ms` (evita PCI=0 em agentes muito rápidos) |
| `agents/parallel_verifiers.py` | Novo — 438 linhas, 7 verificadores, ConsensusEngine, Platt |

## 6. Observações

1. **Verificadores são simbólicos (stubs)**: cada V implementa detecção de padrões via regex, não verificação formal completa. A implementação completa requer integração com ferramentas externas (SymPy para V2, Z3 para V3, NumPy/SciPy para V4-V6, pylint/mypy para V7).
2. **Platt calibration simplificada**: usa sigmoid fixo `sigmoid(10*(score-0.5))`. Em produção, os parâmetros da sigmoid devem ser calibrados com dados reais (Platt scaling completo).
3. **ThreadPool sem context manager**: `executor = ThreadPoolExecutor(...)` + `finally: executor.shutdown(wait=False)` — padrão já estabelecido no C1.
4. **C3 concluído em 1 ciclo TDD**: sem refatorações necessárias após implementação inicial (além dos ajustes de import e floor 0.1ms).

---

*Próximo: Ciclo 4 — Síntese Multi-Caminho (ProcessPool + 4 estratégias de síntese)*
