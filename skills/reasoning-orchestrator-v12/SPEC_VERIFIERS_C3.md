# SPEC — Ciclo 3: Verificadores Paralelos (Cora-Debate V1-V7)

**Versão:** 1.0.0 (C3)  
**Base:** ParallelOrchestrator v12 (Ciclo 1 + Ciclo 2)  
**Objetivo:** Executar verificadores simbólicos V1-V7 em paralelo sobre resultados do pipeline, com ConsensusEngine e retry adaptativo.

---

## 1. Arquitetura

```
┌──────────────────────────────────────────────┐
│         ParallelVerifiers Engine              │
│                                               │
│  ┌────────────────────────────────────────┐  │
│  │         ThreadPoolExecutor (W=4)       │  │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ │  │
│  │  │  V1  │ │  V2  │ │  V3  │ │V4-V7 │ │  │
│  │  │Dim   │ │Algebra│ │C-ex   │ │...   │ │  │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ │  │
│  └────────────────────────────────────────┘  │
│               │                              │
│               ▼                              │
│  ┌────────────────────────────────────────┐  │
│  │        ConsensusEngine                  │  │
│  │  weighted_score = Σ(p_i·conf_i)/Σ(p_i) │  │
│  │  Platt Calibration → final_score       │  │
│  │  threshold = 0.75                      │  │
│  └────────────────────────────────────────┘  │
│               │                              │
│     ┌─────────┴─────────┐                    │
│     ▼                   ▼                    │
│  score≥0.75          score<0.75              │
│  Report final        Retry + mais recursos   │
└──────────────────────────────────────────────┘
```

## 2. Contrato ParallelVerifiers

```python
@dataclass
class VerifierResult:
    verifier_id: str            # "V1" .. "V7"
    passed: bool                # True se verificação aprovada
    confidence: float           # 0.0 a 1.0
    evidence: list[str]         # Evidências que suportam a verificação
    warnings: list[str]         # Avisos e ressalvas
    elapsed_ms: float           # Tempo de execução

@dataclass
class VerificationConsensus:
    weighted_score: float       # Pontuação ponderada composta (0-1)
    passed_count: int           # Quantos V's passaram
    total_count: int            # Total de V's executados
    details: list[VerifierResult]  # Resultados individuais
    platt_calibrated: float     # Score calibrado via Platt
    requires_retry: bool        # True se weighted_score < 0.75
```

### 2.1 Pesos dos Verificadores

| Verif | Função | Peso | Timeout |
|:-----:|--------|:----:|:-------:|
| V1 | Análise Dimensional | 0.15 | 15s |
| V2 | Verificação Algébrica | 0.20 | 15s |
| V3 | Contraexemplos | 0.25 | 30s |
| V4 | Estatístico | 0.10 | 15s |
| V5 | Numérico | 0.10 | 15s |
| V6 | EDO/EDP | 0.10 | 15s |
| V7 | Código-Fonte | 0.10 | 30s |

### 2.2 Métodos

```python
class ParallelVerifiers:
    def __init__(self, max_workers: int = 4, timeout: int = 30)
    
    def verify_parallel(
        self,
        context: dict,          # Contexto do pipeline (agent_results, solution, etc.)
        active_verifiers: Optional[list[str]] = None  # Se None, executa todos V1-V7
    ) -> VerificationConsensus:
        """Executa verificadores em paralelo e retorna consenso."""
    
    def verify_single(self, verifier_id: str, context: dict) -> VerifierResult:
        """Executa um único verificador (útil para debug)."""
    
    def get_supported_domains(self) -> dict[str, list[str]]:
        """Retorna domínios suportados por cada verificador."""
```

### 2.3 Integração com Orchestrator v12

`ParallelOrchestrator` ganha novo método:

```python
def solve_with_verification(
    self, problem: str,
    active_verifiers: Optional[list[str]] = None,
    max_retries: int = 2
) -> tuple[SolutionReport, VerificationConsensus]:
    """Executa pipeline + verificação paralela com retry adaptativo."""
```

Fluxo:
1. Executa pipeline normal (solve)
2. Envia resultados para ParallelVerifiers
3. Se weighted_score < 0.75 e retries < max_retries:
   - Aumenta budget em 50%
   - Re-executa pipeline (apenas fases com agentes falhos)
   - Re-verifica
4. Retorna (SolutionReport, VerificationConsensus)

## 3. Implementação dos Verificadores (Stub → Simbólico)

Cada verificador implementa o mesmo contrato interno:

```python
def _run_V1(self, context: dict) -> VerifierResult
def _run_V2(self, context: dict) -> VerifierResult
# ... V3 a V7
```

### V1: Análise Dimensional
- Extrai equações do texto da solução
- Verifica consistência dimensional (kg·m/s² = N, etc.)
- Stub: detecta padrões de unidades no texto

### V2: Verificação Algébrica
- Identifica expressões algébricas na solução
- Verifica expansão e simplificação
- Stub: detecta operadores matemáticos e valida estrutura

### V3: Contraexemplos
- Para afirmações universais, busca contraexemplos
- Usa busca randomizada de valores de contorno
- Stub: verifica se solução cobre casos extremos

### V4: Estatístico
- Verifica se dados e conclusões usam estatística correta
- Stub: detecta menção a testes estatísticos

### V5: Numérico
- Verifica precisão numérica e arredondamentos
- Stub: detecta erros de arredondamento

### V6: EDO/EDP
- Verifica equações diferenciais
- Stub: detecta padrões de derivadas

### V7: Código-Fonte
- Verifica código na solução
- Stub: detecta presença de blocos de código

## 4. Testes TDD (C3-T1 a C3-T14)

| ID | Nome | Descrição |
|:--:|------|-----------|
| C3-T1 | `verify_parallel_returns_consensus` | Verificadores executam e retornam VerificationConsensus |
| C3-T2 | `all_verifiers_executed` | Todos V1-V7 são executados quando active_verifiers=None |
| C3-T3 | `subset_verifiers` | Apenas verificadores especificados em active_verifiers executam |
| C3-T4 | `weighted_score_formula` | weighted_score = Σ(p_i·conf_i)/Σ(p_i) |
| C3-T5 | `consensus_threshold` | weighted_score < 0.75 → requires_retry=True |
| C3-T6 | `verifier_timeout` | Verificador lento (>timeout) não aborta os outros |
| C3-T7 | `failure_isolation_verifiers` | Falha em um V não afeta resultados dos outros |
| C3-T8 | `parallel_execution_time` | V1-V7 executam em ≤ 2s (paralelo, 4 workers) |
| C3-T9 | `get_supported_domains` | Domínios retornados corretamente |
| C3-T10 | `verify_single` | verify_single retorna VerifierResult para um V específico |
| C3-T11 | `solve_with_verification` | solve_with_verification retorna (SolutionReport, VerificationConsensus) |
| C3-T12 | `retry_on_low_consensus` | weighted_score < 0.75 → retry com mais budget |
| C3-T13 | `max_retries_exceeded` | Após max_retries, retorna mesmo com score < 0.75 |
| C3-T14 | `platt_calibration` | Platt calibration produz score ∈ [0,1] |

## 5. Critérios de Aceitação

| Critério | Alvo | Métrica |
|----------|:----:|---------|
| V1-V7 executam em paralelo | ≤ 2s total | tempo de execução |
| Weighted score ≥ 0.70 | ≥ 0.70 | score médio em soluções corretas |
| Falso positivo | < 5% | proporção de V's aprovando solução errada |
| Retry funciona | ≥ 1 ciclo | budget aumenta 50% no retry |
| Isolamento de falhas | 100% | V falho não afeta outros |

## 6. Estrutura de Arquivos

```
agents/parallel_verifiers.py    # Implementação principal
tests/test_parallel_verifiers.py  # 14 testes TDD
docs/CICLO_3_RELATORIO.md        # Relatório do ciclo
SPEC_VERIFIERS_C3.md             # Esta especificação
```
