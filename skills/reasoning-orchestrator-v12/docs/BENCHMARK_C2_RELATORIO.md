# Relatório do Benchmark C2 — Inference-Time Scaling

## Sumário

Benchmark comparando alocação **adaptativa** (InferenceScaler com lei de potência
PCI = α·compute^β) vs **uniforme** (budget igual para todas as 7 fases) no
ParallelOrchestrator v12.

## Parâmetros

| Parâmetro | Valor |
|-----------|-------|
| α (alpha) | 35.0 |
| β (beta)  | 0.35 |
| Fases     | 7 (F1-F7) |
| Modos     | Express (30), Standard (60), Magnum (100), Research (200) |
| Runs/modo | 3 |

## Resultados

| Modo     | Budget | PCI Uniforme | PCI Adaptativo | Melhoria | Fases com +budget |
|----------|--------|-------------|----------------|----------|-------------------|
| EXPRESS  | 30     | 58.25       | 58.96          | +1.22%   | F3=5, F5=5, F6=5 |
| STANDARD | 60     | 74.24       | 75.27          | +1.39%   | F3=10, F5=10     |
| MAGNUM   | 100    | 88.77       | 90.06          | +1.45%   | F3=17, F5=17     |
| RESEARCH | 200    | 113.15      | 114.86         | +1.51%   | F3=35, F5=33     |

## Análise

### 1. Melhoria consistente em todos os modos
A alocação adaptativa supera a uniforme em **todos os 4 modos**, com melhoria
média de **+1.39%** no PCI.

### 2. Melhoria cresce com o budget
A melhoria aumenta de +1.22% (Express, budget=30) até +1.51% (Research, budget=200).
Isso confirma que a otimização marginal se beneficia de maior espaço de manobra
(distribuição mais granular).

### 3. Padrão de alocação por peso
As fases com maior peso recebem consistentemente mais budget:

| Fase | Nome                | Peso | Express | Standard | Magnum | Research |
|------|---------------------|------|---------|----------|--------|----------|
| F1   | Problem Analysis    | 0.8  | 4       | 7        | 12     | 25       |
| F2   | Reasoning Selection | 1.0  | 4       | 9        | 14     | 28       |
| F3   | Deductive Derivation| 1.5  | **5**   | **10**   | **17** | **35**   |
| F4   | Inductive Verif.    | 1.2  | 4       | 9        | 15     | 31       |
| F5   | Cross-Reference     | 1.4  | **5**   | **10**   | **17** | **33**   |
| F6   | Proof Health Check  | 1.0  | **5**   | 9        | 15     | 29       |
| F7   | Synthesis           | 0.5  | 3       | 6        | 10     | 19       |

F3 (peso 1.5) e F5 (peso 1.4) consistentemente recebem mais; F7 (peso 0.5) recebe menos.

### 4. Speedup consolidado (C1 + C2)

| Camada | Técnica          | Ganho       | Observação |
|--------|------------------|-------------|------------|
| Intra-fase (C1) | ThreadPool | 1.93x | 4 workers, 85% eficiência W=2 |
| Inference-Time (C2) | Alocação adaptativa | +1.39% PCI | Lei de potência α·compute^β |
| **Combinado** | **C1 + C2** | **~1.96x** | Speedup × melhoria PCI |

O ganho de PCI (+1.39%) é multiplicativo sobre o speedup de paralelismo (1.93x),
resultando em ganho composto estimado de ~1.96x.

## Decisões do Ciclo 2

1. **Alocação adaptativa via otimização marginal é confirmada** como superior
   à uniforme em todos os cenários testados.
2. **Limiar de retornos decrescentes (5%)** permanece como condição de parada
   no `allocate_budget()`.
3. **F3 e F5 como pontos de maior investimento** — reflete os pesos definidos
   na especificação C2 (Deductive=1.5, CrossRef=1.4).
4. **ESCALABILIDADE**: a melhoria cresce com o budget, sugerindo que para
   problemas maiores (Research, 200+), o ganho pode ultrapassar +2%.

## Arquivos

| Arquivo | Descrição |
|---------|-----------|
| `docs/BENCHMARK_C2_RESULTADOS.json` | Resultados em JSON |
| `agents/inference_scaler.py` | InferenceScaler implementado |
| `tests/test_inference_scaler.py` | 12 testes TDD (100% GREEN) |
| `tests/benchmark_c2.py` | Script de benchmark |
