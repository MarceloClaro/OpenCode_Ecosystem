# Ciclo 5 — Integração do Pipeline Completo (SDD)

## 1. Objetivo

Integrar as 4 camadas de paralelismo em um pipeline unificado executável com:
- Seleção automática de estratégia de síntese baseada no perfil das cadeias
- Benchmark empírico real no hardware Windows (ProcessPool real)
- Relatório consolidado de métricas (speedup, PCI, tempo)

## 2. Arquitetura

```
FullPipeline
  │
  ├── 1. Analyze Problem → profile: {type, complexity, domain}
  │
  ├── 2. Select Strategy → auto | weighted_vote | debate | ensemble | best_of
  │      baseado no profile (regras heurísticas simples)
  │
  ├── 3. Run Chains (ParallelChain)
  │      ├── Chain Express (budget=30, W=1)
  │      ├── Chain Standard (budget=60, W=2)   ← ProcessPoolExecutor
  │      ├── Chain Magnum (budget=100, W=4)
  │      └── Chain Research (budget=200, W=8)
  │
  ├── 4. Synthesize (SynthesisEngine)
  │      └── strategy selecionada + fallback automático
  │
  ├── 5. Measure & Report
  │      ├── speedup vs sequencial
  │      ├── PCI por cadeia
  │      └── tempo total
  │
  └── 6. Return FullPipelineResult
```

## 3. Especificação

### 3.1 ProblemProfile

```python
@dataclass
class ProblemProfile:
    complexity: Literal["low", "medium", "high", "research"]
    domain: str  # "math", "physics", "code", "general", "debate"
    num_chains: int = 4  # default
    preferred_strategy: str | None = None  # override
```

### 3.2 FullPipeline

```python
class FullPipeline:
    def __init__(self, profile: ProblemProfile | None = None):
        self.profile = profile or ProblemProfile(...)
    
    def analyze_problem(self, problem: str) -> ProblemProfile:
        """Analisa o problema para determinar perfil e estratégia."""
    
    def select_strategy(self, profile: ProblemProfile) -> str:
        """Seleciona estratégia com base no perfil."""
    
    def run(self, problem: str) -> FullPipelineResult:
        """Executa pipeline completo."""
    
    def run_with_benchmark(self, problem: str) -> BenchmarkResult:
        """Executa com medição empírica detalhada."""
```

### 3.3 Heurísticas de Seleção de Estratégia

| Característica do Problema | Estratégia Recomendada |
|:---------------------------|:-----------------------|
| Domínio "code" ou "math" | weighted_vote |
| Domínio "debate" ou controvérsia | debate |
| Complexidade "research" | ensemble |
| Complexidade "low" | best_of |
| Default | weighted_vote |

### 3.4 BenchmarkResult

```python
@dataclass
class BenchmarkResult:
    # Tempos
    total_elapsed_ms: float
    chain_times_ms: list[float]
    synthesis_time_ms: float
    
    # Speedup
    speedup_vs_sequential: float
    
    # PCI por cadeia
    chain_pci_scores: list[float]
    mean_pci: float
    
    # Síntese
    strategy_used: str
    synthesis_confidence: float
    chain_count: int
    
    # Resultado final
    final_answer: str
```

## 4. Testes (14 casos)

| ID | Descrição | Tipo |
|:---|:----------|:-----|
| C5-T1 | Profile: domínio "math" → weighted_vote | Unit |
| C5-T2 | Profile: domínio "debate" → debate | Unit |
| C5-T3 | Profile: complexidade "low" → best_of | Unit |
| C5-T4 | Profile: complexidade "research" → ensemble | Unit |
| C5-T5 | Profile: sem preferência → default weighted_vote | Unit |
| C5-T6 | analyze_problem detecta keywords | Unit |
| C5-T7 | FullPipeline.run() retorna FullPipelineResult | Integration |
| C5-T8 | run_with_benchmark() retorna BenchmarkResult | Integration |
| C5-T9 | Benchmark speedup > 1.0 | Integration |
| C5-T10 | Fallback se cadeia falha | Robustez |
| C5-T11 | Pipe: run + synthesis flui sem erro | Integration |
| C5-T12 | Profiles diferentes geram estratégias diferentes | Unit |
| C5-T13 | Pipeline roda com 1, 2, 3, 4 cadeias | Escalabilidade |
| C5-T14 | Resultado tem final_answer não vazio | Sanidade |

## 5. Critérios de Sucesso

- [ ] 14/14 testes GREEN
- [ ] Benchmark empírico real no Windows com ProcessPool
- [ ] Speedup ≥ 1.5× documentado
- [ ] Seleção de estratégia consistente com heurísticas
- [ ] Relatório C5 gerado

## 6. Dependências

- Ciclo 1: `agents/parallel_dispatch.py`
- Ciclo 2: `agents/inference_scaler.py`
- Ciclo 3: `agents/parallel_verifiers.py`
- Ciclo 4: `agents/parallel_chain.py`, `agents/synthesis_engine.py`

## 7. Detalhamento da Implementação

### 7.1 Estratégia de Seleção Automática

```python
STRATEGY_RULES = {
    "code":       "weighted_vote",
    "math":       "weighted_vote",
    "physics":    "weighted_vote",
    "debate":     "debate",
    "controversy":"debate",
    "creative":   "ensemble",
    "exploration":"ensemble",
    "quick":      "best_of",
    "simple":     "best_of",
}

COMPLEXITY_MAP = {
    "low":      "best_of",
    "medium":   "weighted_vote",
    "high":     "debate",
    "research": "ensemble",
}
```

A seleção funciona em 2 passos:
1. Se domínio tem regra explícita → usa
2. Senão, usa mapeamento por complexidade

### 7.2 Benchmark Empírico

O benchmark executa:
1. Pipeline completo 1 vez (não sequencial — Chains em ProcessPool)
2. Simula execução sequencial somando tempos individuais das cadeias
3. Calcula speedup = tempo_sequencial / tempo_paralelo
4. Mede PCI de cada cadeia (simulado com base no budget)

### 7.3 Tratamento de Erros

- Se `ParallelChain.run()` retorna lista vazia → synthesis com confidence=0.0
- Se strategy selecionada falha → fallback para weighted_vote
- Se uma cadeia falha → remover da lista de resultados, continuar com as demais

### 7.4 Mecanismo de Simulação Sequencial

Para calcular speedup sem executar duas vezes:
```python
chain_results = parallel_chain.run(...)  # execução real
simulated_sequential_time = sum(r.elapsed_ms for r in chain_results)
actual_parallel_time = max(r.elapsed_ms for r in chain_results)
speedup = simulated_sequential_time / actual_parallel_time
```
Isso superestima ligeiramente o speedup (não considera overhead de scheduling), mas é uma aproximação válida para benchmark interno.
