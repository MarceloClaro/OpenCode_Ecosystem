# Benchmark C5 — Empírico de Integração do Pipeline (SDD)

## 1. Objetivo

Validar empiricamente que o paralelismo multi-cadeia do Ciclo 5 produz
speedup real mensurável no hardware Windows, documentar as métricas de
desempenho (speedup × worker count, eficiência, PCI sintético) e confirmar
que a seleção automática de estratégia ocorre corretamente.

## 2. Arquitetura do Benchmark

```
benchmark_c5.py
  │
  ├── Parte 1: Raw ProcessPoolExecutor Benchmark
  │     ├── chain function picklable com time.sleep()
  │     ├── worker counts: [1, 2, 4, 8]
  │     └── compute_scales: [0.5, 1.0, 2.0]
  │
  ├── Parte 2: Strategy Selection Correctness
  │     ├── Testa seleção para 6 domínios
  │     └── Verifica mapeamento correto
  │
  └── Parte 3: FullPipeline End-to-End
        ├── Problemas sintéticos reais
        └── Métricas: speedup, PCI, síntese
```

### 2.1 Dimensões do Benchmark

| Dimensão | Valores | Justificativa |
|:---------|:--------|:--------------|
| Worker count (W) | 1, 2, 4, 8 | Cobre Express(W=1), Standard(W=2), Magnum(W=4), Research(W=8) |
| Compute scale (S) | 0.5, 1.0, 2.0 | Simula problemas leves, médios e pesados |
| Domínios | code, math, debate, creative, simple, physics | Testa seleção de estratégia |
| Número de cadeias | 1, 2, 3, 4 | Testa escalabilidade |

### 2.2 Função de Benchmark (Picklable)

```python
def _benchmark_chain(compute_seconds: float, chain_id: int) -> dict:
    """Função picklable executada via ProcessPoolExecutor.
    
    Simula o custo computacional de uma cadeia de raciocínio.
    """
    import time, os
    start = time.time()
    time.sleep(compute_seconds)
    elapsed = (time.time() - start) * 1000
    return {
        "chain_id": chain_id,
        "compute_time": compute_seconds,
        "elapsed_ms": round(elapsed, 2),
        "pid": os.getpid(),
    }
```

### 2.3 Métricas Coletadas

| Métrica | Definição | Critério |
|:--------|:----------|:---------|
| Speedup | T_seq(W=1) / T_par(W=n) | ≥ 1.5× para W=4 |
| Eficiência | Speedup / W | Quanto mais próximo de 1 melhor |
| Overhead | T_par_real - (T_seq_total / W_msr) | Mínimo possível |
| Speedup Marginal | (T_par(W)) / (T_par(W*2)) | Decrescente com W |
| PCI Simulado | max(0, min(1, budget/200)) | 0–1 |

## 3. Critérios de Sucesso

- [ ] Speedup ≥ 1.5× com W=4 e S=1.0 (Standard)
- [ ] Eficiência > 0.3 em todas as configurações
- [ ] Seleção de estratégia correta em 6/6 domínios
- [ ] Overhead < 500ms na configuração Standard
- [ ] Resultados exportáveis para JSON
- [ ] Relatório gerado em docs/CICLO_5_RELATORIO.md

## 4. Testes de Sanidade

| ID | Descrição | Verificação |
|:---|:----------|:------------|
| B5-T1 | W=1 produz speedup ≈ 1.0 | `abs(speedup - 1.0) < 0.2` |
| B5-T2 | W=2 produz speedup > W=1 | `speedup_W2 > speedup_W1` |
| B5-T3 | W=4 produz speedup > W=2 | `speedup_W4 > speedup_W2` |
| B5-T4 | Eficiência > 0 em todas configs | `efficiency > 0` |
| B5-T5 | Domínio "code" seleciona weighted_vote | `strategy == "weighted_vote"` |
| B5-T6 | Domínio "debate" seleciona debate | `strategy == "debate"` |
| B5-T7 | JSON exportado tem estrutura correta | `len(results) == N` |
| B5-T8 | Resultados têm todos os campos | `all(k in r for k in REQUIRED_KEYS)` |

## 5. Formato de Saída (JSON)

```json
{
  "benchmark": "C5 - Pipeline Integration Benchmark",
  "timestamp": "2026-05-31T12:00:00",
  "system": {
    "platform": "win32",
    "python": "3.12.10",
    "cpu_logical": 16,
    "cpu_physical": 8
  },
  "results": [
    {
      "worker_count": 4,
      "compute_scale": 1.0,
      "num_chains": 4,
      "sequential_ms": 4000.0,
      "parallel_ms": 1050.0,
      "speedup": 3.81,
      "efficiency": 0.95,
      "overhead_ms": 50.0
    }
  ]
}
```

## 6. Dependências

- Python 3.12+ (stdlib apenas: time, json, os, math, concurrent.futures)
- Sem dependências externas para o benchmark raw
- `agents/full_pipeline.py` para Parte 3 (opcional)

## 7. Execução

```bash
python tests/benchmark_c5.py          # benchmark completo
pytest tests/test_benchmark_c5.py -v  # testes de sanidade
```
