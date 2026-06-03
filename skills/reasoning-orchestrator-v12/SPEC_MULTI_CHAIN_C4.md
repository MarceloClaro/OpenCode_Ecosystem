# SPEC — Ciclo 4: Síntese Multi-Caminho (ProcessPool + 4 Estratégias)

**Versão:** 1.0.0 (C4)  
**Base:** ParallelOrchestrator v12 (C1+C2+C3)  
**Objetivo:** Executar múltiplas cadeias de raciocínio em processos paralelos (ProcessPoolExecutor) e consolidar resultados via 4 estratégias de síntese.

---

## 1. Arquitetura

```
┌──────────────────────────────────────────────────────────┐
│                   ParallelChain Engine                     │
│  ProcessPoolExecutor (max_workers=4)                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐     │
│  │ Chain 1  │ │ Chain 2  │ │ Chain 3  │ │ Chain 4  │     │
│  │(W=2,Ex)  │ │(W=2,Std) │ │(W=2,Mag) │ │(W=2,Res) │     │
│  └────┬─────┘ └────┬─────┘ └────┬─────┘ └────┬─────┘     │
│       │            │            │            │           │
│       └────────────┴────────────┴────────────┘           │
│                        │                                  │
│                        ▼                                  │
│  ┌──────────────────────────────────────────────────┐    │
│  │              Synthesis Engine                      │    │
│  │  4 estratégias: WeightedVote | Debate | Ensemble |  │    │
│  │  BestOf                                              │    │
│  └──────────────────────────────────────────────────┘    │
│                        │                                  │
│                        ▼                                  │
│               SolutionReport Consolidado                  │
└──────────────────────────────────────────────────────────┘
```

## 2. Contratos

### 2.1 ParallelChain

```python
@dataclass
class ChainResult:
    chain_id: int
    mode: str
    solution: SolutionReport
    consensus: Optional[VerificationConsensus]
    elapsed_ms: float

class ParallelChain:
    def __init__(self, max_workers: int = 4)
    
    def run_chains(
        self,
        problem: str,
        chain_modes: Optional[list[dict]] = None,
        verify: bool = True
    ) -> list[ChainResult]:
        """Executa N cadeias em ProcessPoolExecutor."""
    
    def run_single_chain(
        self, problem: str, mode: str, budget: int, workers: int
    ) -> ChainResult:
        """Executa uma cadeia única (para subprocesso)."""
```

### 2.2 SynthesisEngine

```python
@dataclass
class SynthesisResult:
    final_answer: str
    strategy: str
    confidence: float
    sources: list[str]
    disagreements: list[str]

class SynthesisEngine:
    def __init__(self, strategy: str = "weighted_vote")
    
    def synthesize(
        self,
        chains: list[ChainResult],
        strategy: Optional[str] = None
    ) -> SynthesisResult:
        """Sintetiza resultados de múltiplas cadeias."""
    
    def weighted_vote(self, chains: list[ChainResult]) -> SynthesisResult
    def debate_synthesis(self, chains: list[ChainResult]) -> SynthesisResult
    def ensemble_synthesis(self, chains: list[ChainResult]) -> SynthesisResult
    def best_of_synthesis(self, chains: list[ChainResult]) -> SynthesisResult
```

### 2.3 Estratégias de Síntese

| Estratégia | Descrição | Quando usar |
|-----------|-----------|-------------|
| weighted_vote | Voto ponderado por PCI de cada cadeia | Consenso geral |
| debate | Identifica divergências e resolve | Soluções conflitantes |
| ensemble | Combina múltiplas perspectivas | Problemas complexos |
| best_of | Seleciona a melhor cadeia (maior PCI) | Speed é prioridade |

## 3. Estrutura de Arquivos

```
agents/parallel_chain.py           # ParallelChain (ProcessPool)
agents/synthesis_engine.py         # SynthesisEngine (4 estratégias)
tests/test_multi_chain_synthesis.py  # 14+ testes TDD
docs/CICLO_4_RELATORIO.md           # Relatório do ciclo
SPEC_MULTI_CHAIN_C4.md              # Esta especificação
```

## 4. Testes TDD (C4-T1 a C4-T14)

| ID | Nome | Descrição |
|:--:|------|-----------|
| C4-T1 | parallel_chain_runs_chains | 4 cadeias executam em paralelo |
| C4-T2 | chain_result_structure | ChainResult tem campos corretos |
| C4-T3 | process_isolation | Falha em 1 cadeia não afeta outras |
| C4-T4 | chain_timeout | Timeout de cadeia não aborta outras |
| C4-T5 | different_modes | Cadeias usam modos diferentes (Ex, Std, Mag, Res) |
| C4-T6 | synthesis_weighted_vote | Voto ponderado por PCI |
| C4-T7 | synthesis_debate | Identifica divergências |
| C4-T8 | synthesis_ensemble | Combina perspectivas |
| C4-T9 | synthesis_best_of | Seleciona melhor cadeia |
| C4-T10 | synthesis_fallback | Estratégia inválida fallback para weighted_vote |
| C4-T11 | empty_chains | Lista vazia retorna SynthesisResult com erro |
| C4-T12 | single_chain | Apenas 1 cadeia funciona |
| C4-T13 | confidence_propagation | Confiança da síntese reflete confiança das cadeias |
| C4-T14 | benchmark_speedup | Speedup C4 > 1.5x vs sequencial |

## 5. Critérios de Aceitação

| Critério | Alvo | Métrica |
|----------|:----:|---------|
| 4 cadeias paralelas | < 2× tempo da mais lenta | comparação temporal |
| Isolamento entre cadeias | 100% | falha não propaga |
| Coerência da síntese | ≥ 0.80 | similaridade entre cadeias |
| Speedup consolidado | ≥ 1.5× | benchmark C1-C4 |
