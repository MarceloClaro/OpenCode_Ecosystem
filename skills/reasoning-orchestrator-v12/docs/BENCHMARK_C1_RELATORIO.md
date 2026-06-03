# Benchmark C1 — ParallelDispatch Intra-Fase

## Data: 31/05/2026
## Pipeline: Sequencial (v11) vs Paralelo (v12) — 19 agentes em 7 fases

## Resumo Executivo

O ParallelDispatch (v12) atinge **speedup de ~1.93x** com 4 workers sobre a execução sequencial (v11), com eficiência de ~48%. O melhor custo-benefício é com **2 workers (Eficiência 85%)**, enquanto 8 workers sofre de diminishing returns (eficiência 24%) devido a fases com poucos agentes.

## Resultados

| Config | Seq (ms) | Par (ms) | Speedup | Eficiência | Overhead (ms) | Amdahl Max |
|--------|----------|----------|---------|------------|---------------|------------|
| Scale=1.0 W=4 (Standard) | 3992.78 | 2068.42 | **1.930x** | 0.483 | 1068.27 | 3.333x |
| Scale=2.0 W=4 | 7975.50 | 4112.18 | **1.939x** | 0.485 | 2117.73 | 3.333x |
| Scale=1.0 W=2 (Express) | 4033.92 | 2367.36 | **1.704x** | 0.852 | 368.79 | 3.333x |
| Scale=1.0 W=8 (Research) | 4012.56 | 2059.47 | **1.948x** | 0.244 | 1559.30 | 3.333x |

## Análise por Fase (Scale=1.0, W=4)

| Fase | Agentes | Seq (ms) | Par (ms) | Speedup Intra-Fase | Gargalo |
|------|---------|----------|----------|-------------------|---------|
| 1 — Problem Analysis | 3 | 381.78 | 183.73 | **2.08x** | notation (0.12s) |
| 2 — Reasoning Selection | 3 | 471.58 | 226.05 | **2.09x** | induction (0.22s) |
| 3 — Deductive Derivation | 4 | 651.72 | 251.33 | **2.59x** | deductive_chain (0.25s) |
| 4 — Inductive Verification | 2 | 750.75 | 451.45 | **1.66x** | stress_test (0.45s) |
| 5 — Cross-Reference | 3 | 735.18 | 352.45 | **2.09x** | contraexemplo (0.35s) |
| 6 — Proof Health Check | 3 | 901.43 | 501.39 | **1.80x** | exhaustive (0.50s) |
| 7 — Synthesis | 1 | 100.34 | 102.02 | **0.98x** | — |

## Achados

### 1. Speedup consistente com Amdahl
- Fração paralelizável estimada: ~70% (gargalo sequencial das fases)
- Speedup máximo teórico (Amdahl): 3.33x
- Speedup prático (4 workers): **1.93x** — 58% do limite teórico
- A diferença (~1.4x) é o overhead de sincronização + scheduling

### 2. Eficiência vs Workers
- W=2: eficiência **85.2%** (quase linear — ótimo para Express)
- W=4: eficiência **48.3%** (bom — escolha default para Standard)
- W=8: eficiência **24.4%** (diminishing returns — útil apenas se houver mais agentes por fase)
- **Recomendação**: usar W=2 como default, W=4 para problemas complexos, W=8 apenas com expansão de agentes

### 3. Overhead de Paralelismo
- Overhead fixo médio: **~1.0s** (criação de ThreadPool, scheduling, coleta)
- Overhead escala com tempo de computação: 1068ms (scale=1.0) → 2118ms (scale=2.0)
- **Overhead relativo**: ~27% do tempo total para problemas rápidos, ~26% para problemas lentos
- Overhead aceitável para raciocínio que tipicamente leva 3-10s

### 4. Fases com Speedup Limitado
- **Fase 4** (1.66x): apenas 2 agentes, um dominante (stress_test = 0.45s)
- **Fase 6** (1.80x): 3 agentes, mas exhaustive (0.50s) domina 56% do tempo
- **Fase 7** (0.98x): 1 único agente — paralelismo é impossível
- **Limitação estrutural**: 3 das 7 fases têm ≤ 2 agentes, limitando o speedup máximo

## Decisões Pós-Benchmark

| Decisão | Justificativa |
|---------|---------------|
| Default Workers = 2 | Melhor eficiência (85%) para uso geral |
| Max Workers = 4 para problemas complexos | Escala bem com fases de 3-4 agentes |
| Não usar W > 4 sem expansão de agentes | Eficiência cai abaixo de 25% |
| Expansão de agentes por fase (Ciclo 3) | Verificadores paralelos podem adicionar agentes às fases 4-6 |

## Pipeline de Validação

```mermaid
flowchart LR
    A[Benchmark C1] --> B[Speedup 1.93x ✓]
    B --> C[Eficiência 48% ✓]
    C --> D[Overhead 1.07s ✓]
    D --> E[OK para Ciclo 2]
```

## Conclusão

**Ciclo 1 validado com sucesso.** Speedup de 1.93x com 4 workers e eficiência de 85% com 2 workers confirmam que o ParallelDispatch é eficaz para paralelismo intra-fase. O overhead de ~27% é aceitável. Próximo passo: Ciclo 2 (Inference-Time Scaling) para alocação adaptativa de budget.
