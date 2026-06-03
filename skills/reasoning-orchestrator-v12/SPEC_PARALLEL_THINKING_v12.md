# SPEC — Parallel Thinking Engine v12.0

**Versão:** 12.0.0  
**Base:** reasoning-orchestrator-v11 (212 reasoning types, 7 fases sequenciais)  
**Inovação:** 3 camadas de paralelismo + Inference-Time Scaling + Verificadores Paralelos  
**Status:** SDD (Spec-Driven Development) — Ciclo 0

---

## Índice

1. [Arquitetura Geral](#1-arquitetura-geral)
2. [Camada 1: ParallelDispatch Intra-Fase](#2-camada-1-paralleldispatch-intra-fase)
3. [Camada 2: Inter-Fase Pipeline](#3-camada-2-inter-fase-pipeline)
4. [Camada 3: Multi-Caminho (Parallel Chain)](#4-camada-3-multi-caminho-parallel-chain)
5. [Inference-Time Scaling](#5-inference-time-scaling)
6. [Verificadores Paralelos (Cora-Debate V1-V7)](#6-verificadores-paralelos-cora-debate-v1-v7)
7. [Síntese e Votação](#7-sintese-e-votacao)
8. [Métricas e Critérios de Sucesso](#8-metricas-e-criterios-de-sucesso)
9. [Estrutura de Diretórios](#9-estrutura-de-diretorios)
10. [Plano de Migração v11 → v12](#10-plano-de-migracao-v11--v12)
11. [Ciclos de Implementação](#11-ciclos-de-implementacao)

---

## 1. Arquitetura Geral

### 1.1 Diagrama de Componentes

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     PARALLEL THINKING ENGINE v12                          │
│                                                                           │
│  ┌────────────────────────────────────────────────────────────────────┐  │
│  │                    ParallelOrchestrator                              │  │
│  │  ┌─────────┐  ┌──────────┐  ┌──────────┐  ┌───────────────────┐   │  │
│  │  │Domain   │→│Strategy  │→│Parallel  │→│InferenceTime     │   │  │
│  │  │Classifier│  │Selector  │  │Dispatch   │  │Scaler            │   │  │
│  │  └─────────┘  └──────────┘  └─────┬────┘  └───────────────────┘   │  │
│  │                                    │                                │  │
│  │  ┌─────────────────────────────────┴──────────────────────────┐     │  │
│  │  │              Parallel Pipeline (3 Camadas)                  │     │  │
│  │  │                                                             │     │  │
│  │  │  ┌──────────────────────────────────────────────────┐      │     │  │
│  │  │  │  CAMADA 1: Intra-Fase Dispatch                   │      │     │  │
│  │  │  │  ┌──────┐ ┌──────┐ ┌──────┐                      │      │     │  │
│  │  │  │  │Agt A1│ │Agt A2│ │Agt A3│  (ThreadPool)       │      │     │  │
│  │  │  │  └──────┘ └──────┘ └──────┘                      │      │     │  │
│  │  │  └──────────────────────────────────────────────────┘      │     │  │
│  │  │                                                             │     │  │
│  │  │  ┌──────────────────────────────────────────────────┐      │     │  │
│  │  │  │  CAMADA 2: Inter-Fase Pipeline (Async DAG)       │      │     │  │
│  │  │  │  F1 ──→ F2 ──→ F3 ──→ F4 ──→ F5 ──→ F6 ──→ F7 │      │     │  │
│  │  │  │  F1.1═╗                                           │      │     │  │
│  │  │  │  F1.2═╣══→ F3 (merge quando independente)        │      │     │  │
│  │  │  │  F2.1═╝                                           │      │     │  │
│  │  │  └──────────────────────────────────────────────────┘      │     │  │
│  │  │                                                             │     │  │
│  │  │  ┌──────────────────────────────────────────────────┐      │     │  │
│  │  │  │  CAMADA 3: Multi-Caminho (Parallel Chain)         │      │     │  │
│  │  │  │  ┌──────────┐                                     │      │     │  │
│  │  │  │  │Cadeia A  │──→ Síntese por Votação             │      │     │  │
│  │  │  │  │Cadeia B  │──→ Ponderada                       │      │     │  │
│  │  │  │  │Cadeia C  │──→ ou Debate                       │      │     │  │
│  │  │  │  └──────────┘                                     │      │     │  │
│  │  │  └──────────────────────────────────────────────────┘      │     │  │
│  │  └─────────────────────────────────────────────────────────────┘     │  │
│  │                                                                       │  │
│  │  ┌──────────────────────────────────────────────────────────────────┐ │  │
│  │  │  Verificadores Paralelos (Cora-Debate V1-V7)                      │ │  │
│  │  │  V1══╗                                                             │ │  │
│  │  │  V2══╬══→ Consensus Engine → Platt Calibration → Report        │ │  │
│  │  │  V3══╝                                                             │ │  │
│  │  └──────────────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Fluxo de Dados

```
PROBLEM
  │
  ▼
[1. DomainClassifier] ──paralelo──→ Domínio + Confiança
  │                                  (semântico + keyword + LLM)
  ▼
[2. StrategySelector] → Lista de estratégias candidatas
  │
  ▼
[3. ParallelDispatch] ──paralelo──→ Resultados por agente
  │  ├─ Intra-Fase: agentes da fase rodam simultaneamente
  │  ├─ Inter-Fase: DAG de fases com dependências
  │  └─ Multi-Caminho: N cadeias completas em paralelo
  │
  ▼
[4. InferenceScaler] → Aloca recursos adaptiveamente
  │                     (mais compute = maior PCI esperado)
  ▼
[5. ParallelVerifiers] ──paralelo──→ Vereditos V1-V7
  │
  ▼
[6. SynthesisEngine] → Síntese: votação ponderada ou debate
  │
  ▼
[7. Report] → SolutionReport com PCI, trace, métricas de paralelismo
```

### 1.3 Estruturas de Dados Centrais

```python
@dataclass
class ParallelConfig:
    """Configuração do paralelismo para uma execução."""
    intra_phase_workers: int = 4       # ThreadPool size
    inter_phase_async: bool = True      # DAG async execution
    multi_path_count: int = 3           # Cadeias paralelas
    multi_path_variance: float = 0.3    # Variação entre cadeias
    inference_scaling: bool = True      # Ativar scaling law
    max_compute_budget: int = 100       # Unidades arbitrárias
    verifiers_active: list[str] = None  # V1-V7 subset

@dataclass
class ParallelResult:
    """Resultado de uma execução paralela."""
    phase: int
    agent_id: str
    result: ReasoningResult
    elapsed_ms: float
    thread_id: int
    chain_id: int  # Para multi-caminho

@dataclass
class ParallelMetrics:
    """Métricas de eficiência do paralelismo."""
    speedup: float           # T_seq / T_par
    efficiency: float        # speedup / workers
    parallel_fraction: float  # Fração paralelizável (Amdahl)
    total_workers: int
    total_elapsed_ms: float
    overhead_ms: float

@dataclass
class ScalingLaw:
    """Lei de escala para inference-time."""
    alpha: float      # Expoente da lei de potência
    beta: float       # Fator de escala
    r_squared: float  # Qualidade do fit
    predict_pci: Callable[[float], float]  # PCI = f(compute)
```

---

## 2. Camada 1: ParallelDispatch Intra-Fase

### 2.1 Descrição

Cada fase do pipeline contém múltiplos agentes independentes entre si (ex: F1 tem NotationAgent + AbstractionAgent + ModularAgent). Na v11, eles executam **sequencialmente**. Na v12, executam em **paralelo via ThreadPoolExecutor**.

### 2.2 Contrato

```python
class ParallelDispatch:
    """
    Executa agentes de uma fase em paralelo.
    
    Args:
        agents: Lista de ReasoningAgent para executar
        context: Contexto compartilhado (problem, agent_results anteriores)
        max_workers: Tamanho do ThreadPool (default: 4)
    
    Returns:
        dict[agent_id, ParallelResult] — Resultados consolidados
    """
    
    def dispatch_phase(
        agents: list[ReasoningAgent],
        context: dict,
        max_workers: int = 4
    ) -> dict[str, ParallelResult]:
        """
        Dispara todos os agentes da fase em paralelo.
        - Verifica dependências antes de cada agente
        - Executa com timeout por agente (60s)
        - Coleta métricas de tempo por thread
        - Propaga exceções sem abortar outros agentes
        """
```

### 2.3 Dependências Intra-Fase

| Fase | Agentes | Dependente de | Paralelizável? |
|------|---------|---------------|:---:|
| F1 | NotationAgent, AbstractionAgent, ModularAgent | Nada (todos independentes) | ✅ Sim |
| F2 | InductorAgent, BaseCaseAgent, InductionAgent | F1 | ✅ Sim |
| F3 | LemmaTracker, DeductiveChain, BackwardChain, Quantificational | F1, F2 | ⚠️ Parcial (LemmaTracker pode depender de DeductiveChain) |
| F4 | ConstructorAgent, StressTestAgent | F1-F3 | ✅ Sim |
| F5 | RefinedContradiction, Contraexemplo, Reductio | F1-F4 | ✅ Sim |
| F6 | ExhaustiveAgent, CrossRefAgent, EnumerationAgent | F1-F5 | ✅ Sim |
| F7 | GeneralizationAgent | F1-F6 | N/A (1 agente) |

### 2.4 Tratamento de Falhas

- Timeout individual por agente (configurável, default 60s)
- Exceção em um agente não aborta os demais
- Resultado parcial: agentes que falharam têm confidence=0
- Log de erros por agente no ParallelResult

### 2.5 Speedup Esperado

| Fase | Agentes | T_seq (est.) | T_par (est.) | Speedup |
|------|---------|:---:|:---:|:---:|
| F1 | 3 | 300ms | 120ms | 2.5x |
| F2 | 3 | 450ms | 180ms | 2.5x |
| F3 | 4 | 800ms | 350ms | 2.3x |
| F4 | 2 | 400ms | 250ms | 1.6x |
| F5 | 3 | 500ms | 200ms | 2.5x |
| F6 | 3 | 600ms | 250ms | 2.4x |
| **Total** | **18** | **3050ms** | **1350ms** | **~2.3x** |

---

## 3. Camada 2: Inter-Fase Pipeline

### 3.1 Descrição

Fases que **não dependem umas das outras** podem executar em paralelo. Por exemplo, enquanto F5 (Refutacional) está executando, F6 (Verificacional) pode pré-processar. Na v12, o pipeline é modelado como um **DAG assíncrono** onde cada fase só espera suas dependências diretas.

### 3.2 DAG de Dependências

```
F1 (Fundacional) ──────────────────────────────────────────────────────┐
  │                                                                      │
  ├──→ F2 (Indutiva) ───────────────────────────────────────────────┐   │
  │     │                                                             │   │
  │     └──→ F3 (Dedutiva) ───────────────────────────────────────┐   │   │
  │           │                                                     │   │   │
  │           ├──→ F4 (Construtiva) ────────────────────────────┐   │   │   │
  │           │     │                                            │   │   │   │
  │           │     ├──→ F5 (Refutacional) ──────────────────┐   │   │   │   │
  │           │     │     │                                   │   │   │   │   │
  │           │     │     └──→ F6 (Verificacional) ───────┐   │   │   │   │   │
  │           │     │           │                           │   │   │   │   │   │
  │           │     │           └──→ F7 (Meta-Cognitiva)   │   │   │   │   │   │
  │           │     │                                       ▼   ▼   ▼   ▼   ▼   ▼
  │           │     │                                  Sequencial obrigatório
  ▼           ▼     ▼
```

### 3.3 Execução como DAG

```python
class AsyncPhasePipeline:
    """
    Executa fases como DAG assíncrono.
    
    Fases independentes executam em paralelo via asyncio.
    Fases com dependência aguardam conclusão das antecessoras.
    """
    
    PHASE_DAG = {
        1: {"deps": [], "agents": "F1_agents"},
        2: {"deps": [1], "agents": "F2_agents"},
        3: {"deps": [1, 2], "agents": "F3_agents"},
        4: {"deps": [1, 2, 3], "agents": "F4_agents"},
        5: {"deps": [1, 2, 3, 4], "agents": "F5_agents"},
        6: {"deps": [1, 2, 3, 4, 5], "agents": "F6_agents"},
        7: {"deps": [1, 2, 3, 4, 5, 6], "agents": "F7_agents"},
    }
```

### 3.4 Acoplamento Real vs Projetado

**Descoberta da análise:** Na prática, as 7 fases são estritamente sequenciais por construção — cada fase depende dos resultados da fase anterior. O DAG atual **não tem ramos independentes**.

**Solução v12:** Criar **ramos paralelos artificiais**:
- **F5a e F5b**: Duas versões do Refutacional com diferentes configurações
- **F6a e F6b**: Verificação exaustiva e cross-reference em paralelo
- **Pré-processamento**: F6 pode começar a preparar dados enquanto F5 executa

**Ganho realista:** ~1.1x a 1.2x para inter-fase (limitado pela dependência linear).

---

## 4. Camada 3: Multi-Caminho (Parallel Chain)

### 4.1 Descrição

Múltiplas cadeias F1→F7 completas executam em paralelo com **diferentes configurações** (temperatura, agentes variantes, random seeds). Cada cadeia produz uma resposta. Ao final, um **SynthesisEngine** consolida via votação ponderada ou debate.

### 4.2 Contrato

```python
class ParallelChain:
    """
    Executa N cadeias completas F1-F7 em paralelo.
    
    Cada cadeia tem configuração ligeiramente diferente:
    - Chain A: Configuração padrão (baseline)
    - Chain B: Alta temperatura (mais exploratório)
    - Chain C: Baixa temperatura (mais conservador)
    - Chain D: Agentes variantes (refined vs original)
    
    Args:
        n_chains: Número de cadeias paralelas
        config_variance: Variância entre configurações
        synthesis_method: "weighted_vote" | "debate" | "ensemble"
    
    Returns:
        SynthesisResult com resposta consolidada e confiança
    """
    
    def execute_chains(
        problem: dict,
        n_chains: int = 3,
        config_variance: float = 0.3
    ) -> list[ChainResult]:
        """Executa N cadeias em paralelo via ProcessPoolExecutor."""
```

### 4.3 Variantes por Cadeia

| Parâmetro | Chain A | Chain B | Chain C | Chain D |
|-----------|:-------:|:-------:|:-------:|:-------:|
| Temperatura | 0.7 | 1.0 | 0.4 | 0.85 |
| Agentes F1 | Notation+Abstraction | RobustNotation+RobustAbstraction | Notation+Modular | Todos robustos |
| Agentes F5 | RefinedContradiction | ContraexemploAgent | ReductioAgent | Todos |
| Random seed | 42 | 123 | 456 | 789 |
| Inference budget | 100 | 150 | 80 | 120 |

### 4.4 Speedup Esperado

Com N cadeias em ProcessPoolExecutor em uma máquina com 4+ cores:

| N cadeias | T_seq (est.) | T_par (est.) | Speedup |
|:---------:|:---:|:---:|:---:|
| 2 | 6000ms | 3200ms | 1.9x |
| 3 | 9000ms | 3500ms | 2.6x |
| 4 | 12000ms | 4000ms | 3.0x |

**Nota:** ProcessPoolExecutor (multiprocess) evita GIL, mas tem overhead de serialização. Para inferência pura (sem I/O), ThreadPoolExecutor pode ser mais rápido.

---

## 5. Inference-Time Scaling

### 5.1 Descrição

Implementa a **scaling law** para raciocínio: mais tempo de inferência (mais agentes, mais verificadores, mais cadeias) produz resultados melhores, seguindo uma lei de potência PCI = α · compute^β.

### 5.2 Lei de Potência

```python
class InferenceScaler:
    """
    Gerencia alocação adaptativa de compute baseada em scaling law.
    
    PCI(compute) = α · compute^β
    
    Onde:
    - α: Fator de escala (base line)
    - β: Expoente da lei (0.2-0.5 típico)
    - compute: Unidades de computação (soma de agentes executados)
    
    Uso: Dado um orçamento de compute, aloca recursos para maximizar PCI.
    """
    
    SCALING_PARAMS = {
        "alpha": 35.0,   # PCI base
        "beta": 0.35,    # Expoente (lei sublinear)
        "diminishing_returns_threshold": 0.8,  # Onde returns começam a diminuir
    }
    
    def allocate_budget(
        total_budget: float,
        phases: list[PhaseConfig]
    ) -> dict[int, float]:
        """
        Aloca orçamento de compute entre fases para maximizar PCI.
        
        Usa otimização marginal: aloca recurso extra para a fase
        com maior ganho marginal esperado.
        """
```

### 5.3 Alocação Adaptativa

```
Orçamento total: 100 unidades

Alocação inicial (uniforme):
  F1: 14 | F2: 14 | F3: 14 | F4: 14 | F5: 14 | F6: 14 | F7: 14

Após otimização marginal (PCI esperado máximo):
  F1: 10 | F2: 12 | F3: 20 | F4: 15 | F5: 18 | F6: 15 | F7: 10
  (F3 e F5 recebem mais porque têm maior impacto no PCI)
```

### 5.4 Budget por Modo de Operação

| Modo | Budget | PCI Esperado | Uso |
|------|:------:|:------------:|-----|
| Express (N3) | 30 | 70-75 | Rascunho rápido |
| Standard (N2) | 60 | 80-85 | Uso diário |
| Magnum (N1) | 100 | 88-93 | Máxima qualidade |
| Pesquisa | 200 | 93-97 | Auditoria formal |

---

## 6. Verificadores Paralelos (Cora-Debate V1-V7)

### 6.1 Descrição

Os 7 verificadores simbólicos do Cora-Debate executam em paralelo sobre os resultados do pipeline. Cada verificador audita um aspecto diferente:

| Verificador | Função | Peso | Domínio |
|:-----------:|--------|:---:|---------|
| V1 | Análise Dimensional | 15% | Physics, Engineering |
| V2 | Verificação Algébrica (SymPy) | 20% | Mathematics |
| V3 | Contraexemplos Randomizados | 25% | All |
| V4 | Estatístico (Shapiro-Wilk, Cohen) | 10% | Statistics, Science |
| V5 | Numérico (IEEE 754) | 10% | Numerical |
| V6 | EDO/EDP | 10% | Physics, Engineering |
| V7 | Código-Fonte (V7a-V7g) | 10% | Software |

### 6.2 Contrato

```python
class ParallelVerifiers:
    """
    Executa verificadores V1-V7 em paralelo.
    
    Cada verificador recebe o resultado do pipeline e retorna:
    - passed: bool
    - confidence: float (0-1)
    - evidence: list[str]
    - warnings: list[str]
    
    Ao final, o ConsensusEngine combina:
    - weighted_score = Σ(peso_i * confidence_i) / Σ(peso_i)
    - Platt calibration aplicada ao score
    - Consenso exige weighted_score > 0.75
    """
    
    VERIFIER_WEIGHTS = {
        "V1": 0.15,
        "V2": 0.20,
        "V3": 0.25,  # Contraexemplos têm maior peso
        "V4": 0.10,
        "V5": 0.10,
        "V6": 0.10,
        "V7": 0.10,
    }
    
    def verify_parallel(
        result: ChainResult,
        active_verifiers: list[str] = None
    ) -> VerificationConsensus:
        """
        Executa verificadores em ThreadPoolExecutor.
        Timeout individual: 30s por verificador.
        Retorna consenso com weighted_score e decisão.
        """
```

### 6.3 Integração com v11

A v11 já tem integração conceitual com Cora-Debate V1-V6 na Fase 6. A v12 torna isso **explícito e paralelo**:

1. Pipeline termina → resultados enviados para ParallelVerifiers
2. V1-V7 executam em paralelo (ThreadPool, 4 workers)
3. ConsensusEngine computa weighted_score
4. Se weighted_score < 0.75 → pipeline reinicia com mais recursos
5. Se weighted_score >= 0.75 → report final

---

## 7. Síntese e Votação

### 7.1 Síntese Multi-Caminho

Quando N cadeias paralelas produzem respostas, o SynthesisEngine consolida:

```python
class SynthesisEngine:
    """
    Consolida resultados de múltiplas cadeias paralelas.
    
    Métodos de síntese:
    1. weighted_vote: PCI da cadeia = peso do voto
    2. debate: Cadeias debatem divergências (via Cora-Debate)
    3. ensemble: Média ponderada das confianças
    4. best_of: Seleciona cadeia com maior PCI
    
    Args:
        chains: list[ChainResult] — resultados das cadeias
        method: Método de síntese
        consensus_threshold: 0.75 (default)
    """
    
    def synthesize(
        chains: list[ChainResult],
        method: str = "weighted_vote"
    ) -> SynthesisResult:
        """
        Retorna resposta consolidada com:
        - final_answer: str
        - confidence: float (0-1)
        - chain_agreement: float (0-1) — concordância entre cadeias
        - diversity_score: float — quão diversas foram as abordagens
        - trace: list — decisões de síntese
        """
```

### 7.2 Algoritmo de Votação Ponderada

```
Para cada cadeia i:
  peso_i = chain.pci / Σ(chain_j.pci)

Para cada resposta candidata r:
  score_r = Σ(peso_i * indicação_i(r))

Resposta final = argmax score_r

Se score < consensus_threshold:
  → Iniciar debate entre cadeias divergentes
  → Ou alocar mais compute para refinamento
```

---

## 8. Métricas e Critérios de Sucesso

### 8.1 Métricas de Paralelismo

| Métrica | Fórmula | Alvo v12 | Medido em |
|---------|---------|:--------:|:---------:|
| Speedup | T_seq / T_par | ≥ 2.0x | Execução |
| Eficiência | Speedup / workers | ≥ 0.6 | Execução |
| Fração Paralela | Lei de Amdahl | ≥ 0.7 | Profiling |
| Overhead | T_par / Σ(T_agente) | ≤ 1.3x | Execução |
| Ganho Multi-Caminho | PCI_n_chain / PCI_1 | ≥ 1.05 | Qualidade |

### 8.2 Métricas de Qualidade

| Métrica | Alvo v12 | Comparação v11 |
|---------|:--------:|:--------------:|
| PCI médio | ≥ 88 | ~82 (v11) |
| CORA-Score (benchmark) | ≥ 0.72 | 0.67 (v11) |
| Taxa de consenso | ≥ 80% | ~70% |
| Tempo médio (modo Standard) | ≤ 3s | ~4.5s (v11 seq) |

### 8.3 Critérios de Aceitação por Ciclo

| Ciclo | Critérios |
|-------|-----------|
| **C1** (ParallelDispatch) | Speedup ≥ 1.8x intra-fase, sem perda de PCI |
| **C2** (Inference Scaling) | PCI segue lei de potência R² ≥ 0.85 |
| **C3** (Verificadores Paralelos) | V1-V7 executam em ≤ 2s total |
| **C4** (Multi-Caminho) | PCI ≥ +3% sobre cadeia única |

### 8.4 Pipeline de Testes (CI)

```yaml
test_parallel_dispatch:     # C1
  assert speedup >= 1.8
  assert pci_drop <= 0.02
  
test_inference_scaling:     # C2
  assert scaling_r_squared >= 0.85
  assert diminishing_returns_detected
  
test_parallel_verifiers:    # C3
  assert v1_v7_elapsed <= 2.0
  assert weighted_score >= 0.70
  
test_multi_chain_synthesis: # C4
  assert pci_improvement >= 0.03
  assert agreement >= 0.60
  
test_regression_v11:         # Sempre
  assert pci_v12 >= pci_v11 * 0.98  # Não regredir
```

---

## 9. Estrutura de Diretórios

```
reasoning-orchestrator-v12/
│
├── SKILL.md                         # Definição da skill v12
├── SPEC_PARALLEL_THINKING_v12.md    # Este documento
├── CATALOGO_RACIOCINIOS_212.md      # Copiado/vinculado da v11
│
├── agents/
│   ├── __init__.py
│   ├── framework.py                 # Estendido da v11 (novos tipos R213+)
│   ├── parallel_dispatch.py         # NOVO: ParallelDispatch intra-fase
│   ├── async_pipeline.py            # NOVO: AsyncPhasePipeline
│   ├── parallel_chain.py            # NOVO: ParallelChain multi-caminho
│   ├── inference_scaler.py          # NOVO: Inference-Time Scaling
│   ├── parallel_verifiers.py        # NOVO: Verificadores paralelos V1-V7
│   ├── synthesis_engine.py           # NOVO: Síntese e votação
│   ├── orchestrator_v12.py          # NOVO: Orquestrador principal v12
│   │
│   ├── critical_agents.py           # Copiado/ref da v11
│   ├── domain_agents.py             # Copiado/ref da v11
│   ├── complementary_agents.py      # Copiado/ref da v11
│   ├── final_agents.py              # Copiado/ref da v11
│   ├── refined_agents.py            # Copiado/ref da v11
│   ├── exhaustive_fixes.py          # Copiado/ref da v11
│   ├── game_theory_agents.py        # Copiado/ref da v11
│   │
│   └── __pycache__/
│
├── tests/
│   ├── test_parallel_dispatch.py    # Testes C1
│   ├── test_inference_scaling.py    # Testes C2
│   ├── test_parallel_verifiers.py   # Testes C3
│   ├── test_multi_chain_synthesis.py# Testes C4
│   ├── test_regression_v11.py       # Regressão
│   └── test_orchestrator_v12.py     # Integração
│
└── ciclos/
    ├── CICLO_1_RELATORIO.md
    ├── CICLO_2_RELATORIO.md
    ├── CICLO_3_RELATORIO.md
    └── CICLO_4_RELATORIO.md
```

---

## 10. Plano de Migração v11 → v12

### 10.1 Compatibilidade Retroativa

- `orchestrator_v12.py` importa agentes da v11 via `sys.path`
- Nenhum arquivo da v11 é modificado
- Skill v12 coexiste com v11 (pastas separadas)
- CLI `reason.py` atualizado com flag `--v12`

### 10.2 Mapeamento de Módulos

| v11 | v12 | Observação |
|-----|-----|------------|
| `orchestrator.py` | `orchestrator_v12.py` | Novo orquestrador com paralelismo |
| `definitive_orchestrator.py` | `agents/orchestrator_v12.py` | Unificado no ParallelOrchestrator |
| `framework.py` | `agents/framework.py` | Estendido (novos R213+) |
| `agents/*.py` | `agents/*.py` | Reutilizados via import |
| — | `agents/parallel_dispatch.py` | **NOVO** |
| — | `agents/inference_scaler.py` | **NOVO** |
| — | `agents/parallel_verifiers.py` | **NOVO** |
| — | `agents/synthesis_engine.py` | **NOVO** |

### 10.3 Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|:------------:|:-------:|-----------|
| Race conditions em agent_results | Média | Alto | Locks por chave, operações atômicas |
| Deadlock no ThreadPool | Baixa | Alto | Timeout por worker, watchdog |
| GIL limitando speedup | Alta | Médio | ProcessPool para CPU-bound |
| Overhead de serialização | Média | Baixo | Pickle otimizado, shared mem |
| Não-determinismo em multi-cadeia | Alta | Médio | Seeds fixas por cadeia, documentado |

---

## 11. Ciclos de Implementação

### Ciclo 0 (Atual): Análise e Especificação

**Status:** ✅ Completo  
**Artefatos:**
- Mapeamento completo do v11 (orchestrator.py, definitive_orchestrator.py, framework.py, reason.py)
- Análise de dependências entre fases
- Identificação de 3 camadas de paralelismo
- Esta especificação (SPEC_PARALLEL_THINKING_v12.md)

### Ciclo 1: ParallelDispatch Intra-Fase

**Objetivo:** Implementar execução paralela de agentes dentro de cada fase.

**Tarefas:**
1. [ ] Criar `agents/parallel_dispatch.py` com ParallelDispatch
2. [ ] Estender `framework.py` com metadados de paralelismo
3. [ ] Criar `orchestrator_v12.py` com pipeline paralelo
4. [ ] Escrever `tests/test_parallel_dispatch.py`
5. [ ] Executar benchmark: speedup, eficiência, PCI
6. [ ] Relatório: CICLO_1_RELATORIO.md

**Critérios de Aceitação:**
- Speedup ≥ 1.8x intra-fase vs v11
- PCI ≥ 80 (não inferior a v11)
- Eficiência ≥ 0.6

### Ciclo 2: Inference-Time Scaling

**Objetivo:** Implementar alocação adaptativa de recursos baseada em scaling law.

**Tarefas:**
1. [ ] Criar `agents/inference_scaler.py` com InferenceScaler
2. [ ] Implementar calibração da lei de potência PCI(compute)
3. [ ] Integrar com ParallelDispatch para alocação de budget
4. [ ] Escrever `tests/test_inference_scaling.py`
5. [ ] Benchmark: PCI vs tempo para diferentes budgets
6. [ ] Relatório: CICLO_2_RELATORIO.md

**Critérios de Aceitação:**
- Lei de potência com R² ≥ 0.85
- Alocação adaptativa supera alocação uniforme em ≥ 5% PCI

### Ciclo 3: Verificadores Paralelos

**Objetivo:** Integrar Cora-Debate V1-V7 como verificadores paralelos.

**Tarefas:**
1. [ ] Criar `agents/parallel_verifiers.py`
2. [ ] Integrar V1-V7 existentes como workers paralelos
3. [ ] Implementar ConsensusEngine com pesos
4. [ ] Implementar pipeline de retry quando consenso < threshold
5. [ ] Escrever `tests/test_parallel_verifiers.py`
6. [ ] Benchmark: tempo de verificação, qualidade do consenso
7. [ ] Relatório: CICLO_3_RELATORIO.md

**Critérios de Aceitação:**
- V1-V7 executam em ≤ 2s total (paralelo)
- Consenso com weighted_score ≥ 0.70
- Taxa de falso positivo < 5%

### Ciclo 4: Síntese Multi-Caminho

**Objetivo:** Implementar cadeias completas F1-F7 paralelas com síntese.

**Tarefas:**
1. [ ] Criar `agents/parallel_chain.py` com ParallelChain
2. [ ] Criar `agents/synthesis_engine.py` com SynthesisEngine
3. [ ] Implementar 4 métodos de síntese (weighted_vote, debate, ensemble, best_of)
4. [ ] Integrar InferenceScaler com Multi-Caminho
5. [ ] Escrever `tests/test_multi_chain_synthesis.py`
6. [ ] Benchmark completo vs v11 (PCI, tempo, diversidade)
7. [ ] Relatório: CICLO_4_RELATORIO.md

**Critérios de Aceitação:**
- PCI ≥ +3% sobre cadeia única
- Agreement entre cadeias ≥ 0.60
- PCI ≥ 88 no benchmark CORA-Eval

---

## Apêndice A: Glossário

| Termo | Definição |
|-------|-----------|
| **ParallelDispatch** | Execução simultânea de agentes independentes dentro de uma fase |
| **AsyncPhasePipeline** | Execução de fases como DAG assíncrono |
| **ParallelChain** | Execução de N cadeias F1-F7 completas em paralelo |
| **Inference-Time Scaling** | Lei de potência PCI = f(compute) |
| **SynthesisEngine** | Consolidação de múltiplos resultados paralelos |
| **ConsensusEngine** | Combinação ponderada de verificadores |
| **PCI** | Proof Confidence Index (0-100) |
| **CORA-Score** | Benchmark score (0-1) do CORA-Eval |
| **Amdahl's Law** | Speedup_max = 1 / ((1-P) + P/N) onde P = fração paralelizável |

## Apêndice B: Referências

- `reasoning-orchestrator-v11/orchestrator.py` — Pipeline sequencial base
- `reasoning-orchestrator-v11/definitive_orchestrator.py` — Entry point unificado
- `reasoning-orchestrator-v11/agents/framework.py` — Framework base + REASONING_REGISTRY
- `skills/cora-debate/SKILL.md` — Verificadores V1-V7
- `specs/skills/system.md` — Specs existentes do ecossistema
- `CATALOGO_RACIOCINIOS_212.md` — Catálogo completo de 212 reasoning types
